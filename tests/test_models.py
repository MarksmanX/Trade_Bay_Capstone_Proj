import os
import pytest
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User, Item, OfferedItem, RequestedItem, Trade, db as _db

@pytest.fixture(scope='module')
def test_client():
    """A test client for the app."""
    with app.app_context():
        _db.create_all()
        yield app.test_client() 
        _db.drop_all()

@pytest.fixture(scope='function')
def db():
    """Set up a new database for each test session."""
    with app.app_context():
        _db.create_all()  # Create tables
        yield _db  # Provide the session for the test
        _db.session.remove()
        _db.drop_all()  # Drop tables after the test


@pytest.fixture
def init_database(db):
    """Initialize the database with a test user and item."""
    user = User.signup(username="testuser", email="test@test.com", password="password")
    db.session.add(user)
    db.session.commit()
    
    item1 = Item(title="Item 1", condition="New", image_url="https://example.com/image1.jpg")
    item2 = Item(title="Item 2", condition="Used", image_url="https://example.com/image2.jpg")
    db.session.add_all([item1, item2])
    db.session.commit()
    
    yield db  # This allows tests to access the database

    db.drop_all()  # Clean up after tests

def test_user_model(init_database):
    """Test basic User model functionality."""
    # Check that the user exists in the database
    user = User.query.filter_by(username="testuser").first()
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@test.com"
    assert user.password != "password"  # Password should be hashed

def test_user_signup(init_database, db):
    """Test the signup method of the User model."""
    user = User.signup(username="newuser", email="new@test.com", password="newpassword")
    db.session.add(user)
    db.session.commit()

    saved_user = User.query.filter_by(username="newuser").first()
    assert saved_user is not None
    assert saved_user.username == "newuser"
    assert saved_user.email == "new@test.com"
    assert saved_user.password != "newpassword"  # Password should be hashed

def test_user_authenticate(init_database):
    """Test the authenticate method of the User model."""
    user = User.authenticate(username="testuser", password="password")
    assert user is not None
    assert user.username == "testuser"

    invalid_user = User.authenticate(username="wronguser", password="password")
    assert invalid_user is False

    invalid_password = User.authenticate(username="testuser", password="wrongpassword")
    assert invalid_password is False

def test_item_model(init_database):
    """Test basic Item model functionality."""
    item = Item.query.filter_by(title="Item 1").first()
    assert item is not None
    assert item.title == "Item 1"
    assert item.condition == "New"
    assert item.image_url == "https://example.com/image1.jpg"

def test_offered_item(init_database, db):
    """Test the OfferedItem model."""
    user = User.query.filter_by(username="testuser").first()
    item = Item.query.filter_by(title="Item 1").first()

    offered_item = OfferedItem(user_id=user.id, item_id=item.id)
    db.session.add(offered_item)
    db.session.commit()

    saved_offered_item = OfferedItem.query.filter_by(user_id=user.id).first()
    assert saved_offered_item is not None
    assert saved_offered_item.item.title == "Item 1"

def test_requested_item(init_database,db):
    """Test the RequestedItem model."""
    user = User.query.filter_by(username="testuser").first()
    item = Item.query.filter_by(title="Item 2").first()

    requested_item = RequestedItem(user_id=user.id, item_id=item.id)
    db.session.add(requested_item)
    db.session.commit()

    saved_requested_item = RequestedItem.query.filter_by(user_id=user.id).first()
    assert saved_requested_item is not None
    assert saved_requested_item.item.title == "Item 2"

def test_trade_model(init_database, db):
    """Test the Trade model."""
    user = User.query.filter_by(username="testuser").first()
    item1 = Item.query.filter_by(title="Item 1").first()
    item2 = Item.query.filter_by(title="Item 2").first()

    # Create offered and requested items
    offered_item = OfferedItem(user_id=user.id, item_id=item1.id)
    requested_item = RequestedItem(user_id=user.id, item_id=item2.id)
    db.session.add_all([offered_item, requested_item])
    db.session.commit()

    # Create trade
    trade = Trade(item_offered_id=offered_item.id, item_requested_id=requested_item.id)
    db.session.add(trade)
    db.session.commit()

    saved_trade = Trade.query.first()
    assert saved_trade is not None
    assert saved_trade.offered_item.item.title == "Item 1"
    assert saved_trade.requested_item.item.title == "Item 2"
    assert saved_trade.status == "Pending"