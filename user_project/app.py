from flask import Flask
from config import Config
from routes import init_routes
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

init_routes(app)

def create_database():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    create_database()
    app.run(debug=True)