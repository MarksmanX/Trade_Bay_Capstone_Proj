import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, flash, redirect, session, g, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from ebay_24 import Ebay_24
from forms import UserAddForm, LoginForm, EditProfileForm
from models import db, connect_db, User, Item, OfferedItem, RequestedItem, Trade

CURR_USER_KEY = "curr_user"
bcrypt = Bcrypt()
API_KEY=os.getenv('api_key')

# Check if we are in testing mode (you can set an environment variable for this)
TESTING = os.getenv('FLASK_ENV') == 'testing'

app = Flask(__name__)

if TESTING:
    # Use in-memory SQLite database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///trade_bay')

# Configuration settings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")


with app.app_context():
    connect_db(app)
    db.create_all()

toolbar = DebugToolbarExtension(app)
migrate = Migrate(app, db)

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    
    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def homepage():
    """Displays the homepage of Tradebay."""

    return render_template('index.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    
    Create new user and add to DB. Redirect to home page.
    
    If form not valid, present form.
    
    If there already is a user with that username: flash message and re-present form."""

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)
        
        do_login(user)

        return redirect("/")
    
    else: 
        print("Form is invalid:", form.errors)
        return render_template('users/signup.html', form=form)
    

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(f"/user/{user.id}")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    flash(f'Goodbye!')
    session.pop('curr_user')
    return redirect('/login')


@app.route('/add-offered-item', methods=['POST'])
def add_offered_item():
    """Add an item to the user's offered items list."""
    if (g.user == None):
        flash("You must log in first.")
        form = LoginForm()
        return render_template('users/login.html', form=form)

    data = request.get_json()
    item_id = data.get('item_id')

    if not item_id:
        return jsonify({"success": False, "error": "Item not found."}), 400

    # Fetch the item and add it to the offered items list
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"success": False, "error": "Item does not exist."}), 404
    
    existing_item = OfferedItem.query.filter_by(user_id=g.user.id, item_id=item_id).first()
    if existing_item:
        return jsonify({"success": False, "error": "Item already in your offered items list."}), 400

    offered_item = OfferedItem(user_id=g.user.id, item_id=item_id)
    
    db.session.add(offered_item)
    db.session.commit()

    return jsonify({"success": True})


@app.route('/add-requested-item', methods=['POST'])
def add_requested_item():
    """Add an item to the user's requested items list."""
    if (g.user == None):
        flash("You must log in first.")
        form = LoginForm()
        return render_template('users/login.html', form=form)
    
    data = request.get_json()
    item_id = data.get('item_id')

    if not item_id:
        return jsonify({"success": False, "error": "Item not found."}), 400

    # Fetch the item and add it to the requested items list
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"success": False, "error": "Item does not exist."}), 404
    
    existing_item = RequestedItem.query.filter_by(user_id=g.user.id, item_id=item_id).first()
    if existing_item:
        return jsonify({"success": False, "error": "Item already in your requested items list."}), 400

    requested_item = RequestedItem(user_id=g.user.id, item_id=item_id)
    
    db.session.add(requested_item)
    db.session.commit()

    return jsonify({"success": True})


@app.route('/items/search', methods=['GET'])
def search():
    term = request.args.get('q')
    if not term:
        flash("You must enter a search term.", "danger")
        return redirect(request.referrer)
    
    # Fetch items from eBay API
    ebay = Ebay_24(API_KEY, term)
    items_from_api = ebay.fetch()

    # Clear any existing items that match the search term (if you want to update the list every time)
    # Item.query.filter(Item.title.ilike(f'%{term}%')).delete(synchronize_session=False)
    # db.session.commit()

    # Filter and add new items to the database
    for item_data in items_from_api:
        # Check if the item already exists in the database
        existing_item = Item.query.filter_by(title=item_data['title'], condition=item_data['condition']).first()
        if not existing_item:
            new_item = Item(
                title=item_data['title'],
                condition=item_data['condition'],
                image_url=item_data['image_url']
            )
            db.session.add(new_item)
    db.session.commit()

    # Query database for items matching the search term
    items = Item.query.filter(Item.title.ilike(f'%{term}%')).limit(10).all()

    item_users = {}
    for item in items:
        # Get users offering this item
        users_offering = OfferedItem.query.filter_by(item_id=item.id).all()
        item_users[item.id] = [user.user for user in users_offering]  # Create a list of users for each item

    # Render items on a template
    return render_template('items/search.html', items=items, item_users=item_users)


@app.route('/trade-items')
def list_items():
    """Display the user's offered and requested items."""
    if (g.user == None):
        flash("You must log in first.")
        form = LoginForm()
        return render_template('users/login.html', form=form)
    
    user = g.user
    
    offered_items = OfferedItem.query.filter_by(user_id=user.id).all()
    requested_items = RequestedItem.query.filter_by(user_id=user.id).all()

    return render_template('users/item_lists.html', offered_items=offered_items, requested_items=requested_items)
    

@app.route('/initiate-trade', methods=['POST'])
def initiate_trade():
    """Initiate a trade between the current user and another user."""
    if (g.user == None):
        flash("You must log in first.")
        form = LoginForm()
        return render_template('users/login.html', form=form)
    
    data = request.get_json()
    your_item_id = data.get('your_item_id')
    their_item_id = data.get('their_item_id')
    print(f"{your_item_id}")
    print(f"{their_item_id}")
    if not your_item_id or not their_item_id:
        return jsonify({"success": False, "error": "Both items must be selected."}), 400
    
    # Check if the requested item is already in the current user's requested list
    existing_requested_item = RequestedItem.query.filter_by(
        item_id=their_item_id, user_id=g.user.id).first()

    # If the item is not in the user's requested list, add it
    if not existing_requested_item:
        new_requested_item = RequestedItem(
            user_id=g.user.id,
            item_id=their_item_id
        )
        db.session.add(new_requested_item)
        db.session.commit()

        # Set requested_item_id to the ID of the newly created RequestedItem
        requested_item_id = new_requested_item.id
    else:
        # Use the existing requested item
        requested_item_id = existing_requested_item.id

    # Ensure that 'your_item_id' belongs to the current user
    your_item = OfferedItem.query.filter_by(user_id=g.user.id, id=your_item_id).first()
    if not your_item:
        return jsonify({"success": False, "error": "The item you're offering doesn't belong to you."}), 400

    # Ensure that 'their_item_id' belongs to the other user (not the current user)
    their_item = OfferedItem.query.filter(OfferedItem.id == their_item_id, OfferedItem.user_id != g.user.id).first()
    if not their_item:
        return jsonify({"success": False, "error": "The other user's item was not found or already traded."}), 400

    # Create the trade record
    trade = Trade(
        item_offered_id=your_item_id,
        item_requested_id=requested_item_id,
        status='Pending'
    )
    
    db.session.add(trade)
    db.session.commit()

    return jsonify({"success": True})

######################################################
# General user routes:

# @app.route('/users')

@app.route('/user/<int:user_id>')
def user_profile(user_id):
    """Display the user's profile and their offered items."""
    if (g.user == None):
        flash("You must log in first.")
        form = LoginForm()
        return render_template('users/login.html', form=form)

    other_user = User.query.get(user_id)
    if not other_user:
        return "User not found", 404

    curr_user = g.user
    offered_items = OfferedItem.query.filter_by(user_id=user_id).all()
    requested_items = RequestedItem.query.filter_by(user_id=user_id).all()

    return render_template('users/user_profile.html', curr_user=curr_user, other_user=other_user, offered_items=offered_items, requested_items=requested_items)


@app.route('/remove-item', methods=['DELETE'])
def remove_item():
    """Remove an item from the offered or requested list."""
    if (g.user == None):
        flash("You must log in first.")
        form = LoginForm()
        return render_template('users/login.html', form=form)

    # Get the item ID and type from the request body
    data = request.get_json()
    item_id = data.get('item_id')
    item_type = data.get('item_type')  # Expecting either "offered" or "requested"

    if item_id is None or item_type is None:
        return jsonify({"success": False, "error": "Item ID and type are required."}), 400

    # Depending on the type, remove the item from the appropriate model
    if item_type == "offered":
        offered_item = OfferedItem.query.filter_by(item_id=item_id, user_id=g.user.id).first()
        if offered_item:
            db.session.delete(offered_item)
            db.session.commit()
            return jsonify({"success": True})

    elif item_type == "requested":
        requested_item = RequestedItem.query.filter_by(item_id=item_id, user_id=g.user.id).first()
        if requested_item:
            db.session.delete(requested_item)
            db.session.commit()
            return jsonify({"success": True})

    return jsonify({"success": False, "error": "Item not found in the specified list."}), 404


@app.route('/user/<int:other_user_id>/trade-items')
def trade_items(other_user_id):
    """Display trade items for the other user."""
    if (g.user == None):
        flash("You must log in first.")
        form = LoginForm()
        return render_template('users/login.html', form=form)
    
    # Get the current user
    current_user_id = g.user.id

    # Fetch the other user based on the provided ID
    other_user = User.query.get(other_user_id)

    # Check if the other user exists
    if not other_user:
        return "User not found", 404

    # Get offered items for the current user and the other user
    user_offered_items = OfferedItem.query.filter_by(user_id=current_user_id).all()
    other_user_offered_items = OfferedItem.query.filter_by(user_id=other_user_id).all()

    # Render the trade items template with the user data
    return render_template('users/trade_items.html', user_offered_items=user_offered_items, other_user=other_user, other_user_offered_items=other_user_offered_items)


@app.route('/user/pending-trades')
def pending_trades():
    """Show all pending trades involving the current user."""
    if (g.user == None):
        flash("You must log in first.")
        form = LoginForm()
        return render_template('users/login.html', form=form)

    trades = Trade.query.filter(
        (Trade.offered_item.has(user_id=g.user.id)) | 
        (Trade.requested_item.has(user_id=g.user.id))
    ).all()

    return render_template('users/pending_trades.html', trades=trades)


@app.route('/accept-trade/<int:trade_id>', methods=['POST'])
def accept_trade(trade_id):
    """Accept a pending trade."""
    if (g.user == None):
        flash("You must log in first.")
        form = LoginForm()
        return render_template('users/login.html', form=form)
    
    trade = Trade.query.get(trade_id)

    if not trade or trade.status != 'Pending':
        return jsonify({"success": False, "error": "Trade not found or already processed."}), 404

    trade.status = 'Accepted'
    db.session.commit()

    return jsonify({"success": True, "message": "Trade accepted!"})

@app.route('/reject-trade/<int:trade_id>', methods=['POST'])
def reject_trade(trade_id):
    """Reject a pending trade."""
    if (g.user == None):
        flash("You must log in first.")
        form = LoginForm()
        return render_template('users/login.html', form=form)
    
    trade = Trade.query.get(trade_id)

    if not trade or trade.status != 'Pending':
        return jsonify({"success": False, "error": "Trade not found or already processed."}), 404

    trade.status = 'Rejected'
    db.session.commit()

    return jsonify({"success": True, "message": "Trade rejected!"})


@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_profile(user_id):
    """Displays the form to edit the User's Profile information."""
    if (g.user == None):
        flash("You must log in first.")
        form = LoginForm()
        return render_template('users/login.html', form=form)
    
    user = User.query.get_or_404(user_id)

    if user_id != g.user.id:
        flash("You dont have permission to edit this profile.", "danger")
        return redirect(url_for('user_profile', user_id=g.user.id))

    form = EditProfileForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.image_url = form.image_url.data if form.image_url.data else None
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_profile', user_id=user.id))

    return render_template('users/edit_profile.html', form=form, user=user)

