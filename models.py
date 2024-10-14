from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    image_url = db.Column(db.String(200), nullable=True, default='/static/images/default_profile_pic.jpg')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"
    
    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.
        
        Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username,
                    email=email,
                    password=hashed_pwd
        )
        
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        
        If can't find matching user (or if password is wrong), returns False."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
            
        return False

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    condition = db.Column(db.String(50))
    image_url = db.Column(db.String(500))
    

class OfferedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    user = db.relationship('User', backref=db.backref('offered_items', lazy=True))
    item = db.relationship('Item')  


class RequestedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    user = db.relationship('User', backref=db.backref('requested_items', lazy=True))
    item = db.relationship('Item')
    

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_offered_id = db.Column(db.Integer, db.ForeignKey('offered_item.id'))
    item_requested_id = db.Column(db.Integer, db.ForeignKey('requested_item.id'))
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    offered_item = db.relationship('OfferedItem', foreign_keys=[item_offered_id])
    requested_item = db.relationship('RequestedItem', foreign_keys=[item_requested_id])

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)