from flask import render_template, request, redirect, url_for, flash
from models import db, User

def init_routes(app):
    @app.route("/")
    def home():
        users = User.query.all()
        return render_template("home.html", user=users)

    @app.route("/add", methods=["GET", "POST"])
    def add_user():
        if request.method == "POST":
            username = request.form.get("username")
            email = request.form["email"]
            if username or email:
                new_user = User(username=username, email=email)
                db.session.add(new_user)
                db.sessio.commit()
                flash("User added successfully!", "success")
                return redirect(url_for("home"))
        return render_template("add_user.html")

    @app.route("/delete/<int:user_id>")
    def delete_user(user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash("User deleted successfully!", "success")
        return redirect(url_for("home"))

    @app.route("/update/<int:user_id>", methods=["GET", "POST"])
    def update_user(user_id):
        user = User.query.get(user_id)
        if request.method == "POST" and user:
            user.username = request.form.get("username")
            user.email = request.form.get("email")
            db.session.commit()
            flash("User updated successfully!", "success")
            return redirect(url_for("home"))
        return render_template("update_user.html", user=user)