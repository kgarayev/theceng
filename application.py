import os
import json
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from flask_mail import Mail, Message
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps


# Configure application
app = Flask(__name__,
            static_url_path="",
            static_folder=".")


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Make sure mail default sender is set
#if not os.environ.get("MAIL_DEFAULT_SENDER"):
#    raise RuntimeError("MAIL_DEFAULT_SENDER not set")

# Make sure mail username is set
#if not os.environ.get("MAIL_DEFAULT_RECIPIENT"):
#    raise RuntimeError("MAIL_DEFAULT_RECIPIENT not set")

# Make sure default sender is set
#if not os.environ.get("MAIL_DEFAULT_SENDER"):
#    raise RuntimeError("MAIL_DEFAULT_SENDER not set")

# Make sure mail password is set
#if not os.environ.get("MAIL_PASSWORD"):
#    raise RuntimeError("MAIL_PASSWORD not set")

# setting up email configurations

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configuring the database

# all services offered - list of dictionaries

# create products and prices in stripe if not already created

# list of all products and prices in stripe (list of dicts)

# require login function

# format value as GBP function


# index route
@app.route("/")
def index():

    return render_template("index.html")

# index/home route
@app.route("/home")
def home():

    return render_template("index.html")

# about the webiste and services offered
@app.route("/about")
def about():

    return render_template("about.html")



# potentially more functionality to expand the website - more interaction



# potentially more functionality to expand the website - more interaction


# display the services offered


# display the basket of chosen services



# checkout to pay


# if the payment succeeds


# if the payment is cancelled



# delete an item from the basket


# clear all basket in one go


# contact page functionality



# register the user


# login the registered user. If not registered - offer link to register or return apology

# log the current user out


# viewing account and editing it



# changing the password



# deleting account completely


# handling errors
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__== '__main__':
    app.run(port=4242)