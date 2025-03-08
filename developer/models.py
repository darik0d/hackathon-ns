from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {"id": self.self.id, "username": self.username, "email": self.email, "created_at": self.created_at,
                "updated_at": self.updated_at}