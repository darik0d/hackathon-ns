from flask import Flask
from config import Config
from routes import init_routes
from models import db

apps = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

init_routes(app)

def create_database():
    with app.app_context():
        db.create_all()

if name == "main":
    create_database()
    app.run(debug=True)