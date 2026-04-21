from flask import Flask, render_template, request, redirect, url_for, Blueprint
from database.db import users

auth = Blueprint('auth', __name__)

#------------------------------login route-------------------------------       
@auth.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users.find_one({"email": email})
        

        if user and user["password"] == password:
            if user["role"]=="admin":
                return redirect(url_for("admin.admin_das",user_id=str(user["_id"]),name=str(user["name"])))
            elif user["role"]=="employee":
                return redirect(url_for("attendance.employee_dashboard", user_id=str(user["_id"]), name=str(user["name"])))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")