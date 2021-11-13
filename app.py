import os

from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
if os.path.exists("env.py"):
    import env


# flask
app = Flask(__name__)

# mondodb
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
mongo = PyMongo(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/champion")
def champion():
    chempion_list = list(mongo.db.chempion.find())
    user = mongo.db.users.find_one({"username": session["user"]})
    return render_template("champion.html", chempion_list=chempion_list, user=ObjectId(user["_id"])) 

@app.route("/puppy")
def puppy():
    bully_list = list(mongo.db.bully.find())
    print('Bully list is ', bully_list)
    return render_template("puppy.html", bully_list=bully_list) 

@app.route("/contact")
def contact():
    return render_template("contact.html") 


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("query")
        chempion = list(mongo.db.chempion.find({"$text": {"$search": query}}))
        all_chempion = list(mongo.db.chempion.find())
        print(chempion)
        for chempion in chempion:
            try:
                recipe["user_id"] = mongo.db.users.find_one(
                    {"_id": recipe["user_id"]})["username"]
            except:
                pass
        return render_template("search.html", chempion=chempion)

    return render_template("search.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username").capitalize()))
                return redirect(url_for(
                    "profile", username=session["user"]))

            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET"])
def profile(username):
    if session["user"]:
        return render_template(
            "profile.html", username=username)
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("You've been logged out")
    session.pop("user")
    return redirect(url_for("login"))

@app.route("/add_chempion", methods=["GET", "POST"])
def add_chempion():
    if request.method == "POST":
        user = mongo.db.users.find_one({"username": session["user"]})
        new_chempion = {
            "img": request.form.get("chempion_img"),
            "title": request.form.get("chempion_title"),
            "text": request.form.get("chempion_text"),
            "user_id": ObjectId(user["_id"])
        }
        mongo.db.chempion.insert_one(new_chempion)
        flash("Chempion Successfully Added")
        return redirect(url_for("add_chempion"))

    types = mongo.db.types.find().sort("type", 1)
    return render_template("add_chempion.html", types=types)

@app.route("/edit_chempion/<chempion_id>", methods=["GET", "POST"])
def edit_chempion(chempion_id):
    if request.method == "POST":
        user = mongo.db.users.find_one({"username": session["user"]})
        edit_chempion = {
            "img": request.form.get("chempion_img"),
            "title": request.form.get("chempion_title"),
            "text": request.form.get("chempion_text"),
            "user_id": ObjectId(user["_id"])
        }
        mongo.db.chempion.update({"_id": ObjectId(chempion_id)}, edit_chempion)
        flash("Chmepion Successfully Edited")
    chempion = mongo.db.chempion.find_one({"_id": ObjectId(chempion_id)})
    return render_template("edit_chempion.html", chempion=chempion)


@app.route("/delete_chempion/<chempion_id>")
def delete_chempion(chempion_id):
    mongo.db.chempion.remove({"_id": ObjectId(chempion_id)})
    flash("Chempion Deleted")
    return redirect(url_for("search"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=os.environ.get("DEBUG", False))