from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)
    
    # Load configurations, initialize extensions, etc.
    app.config.from_object('config.Config')
    
    db.init_app(app)

    # Import and register blueprints, routes, etc.
    with app.app_context():
        from . import routes  # Import your routes here

    return app