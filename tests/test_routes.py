import os
import pytest
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User, Item, Trade, db as _db
from flask import session

@pytest.fixture(scope='function')
def client():
    """A test client for the app."""
    app.config['TESTING'] = True
    with app.app_context():
        _db.create_all()  # Create tables
        yield app.test_client()  # This will yield the test client to the tests
        _db.drop_all()  # Drop tables after tests


@pytest.fixture(scope='function')
def db():
    """Set up a new database for each test session."""
    with app.app_context():
        _db.create_all()  # Create tables
        yield _db  # Provide the session for the test
        _db.session.remove()
        _db.drop_all()  # Drop tables after the test


@pytest.fixture
def auth(client):
    """A fixture for simulating user authentication."""
    def signup(username="testuser", password="password", email="testuser@example.com"):
        """Simulate user signup."""

        response = client.get('/signup')
        csrf_token = response.data.decode().split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

        return client.post('/signup', data={
            "username": username,
            "password": password,
            "email": email,
            "csrf_token": csrf_token
        }, follow_redirects=True)

    
    def login():
        """Simulate user login."""
        response = client.get('/login')
        csrf_token = response.data.decode().split('name="csrf_token" type="hidden" value="')[1].split('"')[0]
        client.post('/login', data={
            "username": "testuser",
            "password": "password",
            "csrf_token": csrf_token
        })

    def logout():
        """Simulate a user logout."""
        response = client.get('/logout')
        return response

    return type('Auth', (object,), {'signup': signup, 'login': login, 'logout': logout})


def test_edit_profile_logged_in(client, auth):
    """Test the edit profile route when the user is logged in."""
    
    # Signup the user first
    response = auth.signup()

    # Then login the user
    auth.login()
    
    # Fetch the current user's profile
    user = User.query.first()

    csrf_token = client.get('/user/{}/edit'.format(user.id)).data.decode().split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    # Create valid form data for the profile update
    form_data = {
        "username": "newusername",
        "email": "newemail@example.com",
        "image_url": "http://example.com/new_image.jpg",
        "csrf_token": csrf_token
    }
    
    # Send a POST request to the edit profile route
    response = client.post(f"/user/{user.id}/edit", data=form_data, follow_redirects=True)

    # Check if the request was successful and the profile was updated
    assert response.status_code == 200
    assert b"Profile updated successfully!" in response.data

    # Verify the updated data in the database
    updated_user = User.query.get(user.id)
    assert updated_user.username == "newusername"
    assert updated_user.email == "newemail@example.com"
    assert updated_user.image_url == "http://example.com/new_image.jpg"


def test_edit_profile_not_logged_in(client, auth):
    """Test that the edit profile route redirects when the user is not logged in."""

    auth.signup()
    auth.logout()

    # Fetch the user's profile without logging in
    user = User.query.first()
    
    # Try accessing the edit profile route
    response = client.get(f"/user/{user.id}/edit", follow_redirects=True)
    
    # Check if it redirects to the login page
    assert response.status_code == 200
    assert b"You must log in first." in response.data


def test_edit_profile_permission_denied(client, auth, db):
    """Test that a user cannot edit another user's profile."""

    # Signup as user 2 then logout
    auth.signup(username="user2", password="password", email="user2@example.com")
    auth.logout()
    user2 = User.query.filter_by(username="user2").first()

    # Signup and login as user 1
    auth.signup()
    user = User.query.filter_by(username="testuser").first()
    
    csrf_token = client.get('/user/{}/edit'.format(user.id)).data.decode().split('name="csrf_token" type="hidden" value="')[1].split('"')[0]

    form_data = {
        "username": "newusername",
        "email": "newemail@example.com",
        "image_url": "http://example.com/new_image.jpg",
        "csrf_token": csrf_token
    }

    # Try to edit the second user's profile while logged in as the first user
    response = client.post(f"/user/{user2.id}/edit", data=form_data, follow_redirects=True)

    print(f"Final route: {response.request.path}")

    # Check for permission denied message
    assert response.status_code == 200
    assert b"You dont have permission to edit this profile." in response.data


def test_add_offered_item_logged_in(client, auth, db):
    """Test adding an offered item while logged in."""
    
    # Sign up and log the user in
    auth.signup()

    # Add a new item to the database
    item = Item(title="Test Item", condition="New", image_url="http://example.com/test.jpg")
    db.session.add(item)
    db.session.commit()

    # Send a request to add the item to the offered items list
    response = client.post("/add-offered-item", json={"item_id": item.id}, follow_redirects=True)
    
    # Check if the request was successful
    assert response.status_code == 200
    assert b"success" in response.data


def test_add_offered_item_not_logged_in(client, db):
    """Test that adding an offered item redirects when not logged in."""
    
    # Add a new item to the database
    item = Item(title="Test Item", condition="New", image_url="http://example.com/test.jpg")
    db.session.add(item)
    db.session.commit()

    # Try to add the item without logging in
    response = client.post("/add-offered-item", json={"item_id": item.id}, follow_redirects=True)

    # Check if it redirects to the login page
    assert response.status_code == 200
    assert b"You must log in first." in response.data


def test_accept_trade_logged_in(client, auth, db):
    """Test accepting a trade while logged in."""
    
    # Signup the user and log in.
    auth.signup()

    # Create a trade in 'Pending' status
    trade = Trade(item_offered_id=1, item_requested_id=2, status="Pending")
    db.session.add(trade)
    db.session.commit()

    # Send a request to accept the trade
    response = client.post(f"/accept-trade/{trade.id}", follow_redirects=True)

    # Check if the request was successful
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] == True

    # Verify the trade status is updated to 'Accepted'
    updated_trade = Trade.query.get(trade.id)
    assert updated_trade.status == "Accepted"


def test_accept_trade_not_logged_in(client, db):
    """Test that accepting a trade redirects when not logged in."""

    # Create a trade in 'Pending' status
    trade = Trade(item_offered_id=1, item_requested_id=2, status="Pending")
    db.session.add(trade)
    db.session.commit()

    # Try to accept the trade without logging in
    response = client.post(f"/accept-trade/{trade.id}", follow_redirects=True)

    # Check if it redirects to the login page
    assert response.status_code == 200
    assert b"You must log in first." in response.data
