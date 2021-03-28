import os
import json
import stripe
from datetime import datetime
import requests
import sqlite3
import psycopg2
import urlparse
import sqlalchemy

from cs50 import SQL
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


urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.getenv("DATABASE_URL"))
conn = psycopg2.connect(
 database=url.path[1:],
 user=url.username,
 password=url.password,
 host=url.hostname,
 port=url.port
)


# Make sure mail default sender is set
if not os.environ.get("MAIL_DEFAULT_SENDER"):
    raise RuntimeError("MAIL_DEFAULT_SENDER not set")

# Make sure mail username is set
if not os.environ.get("MAIL_DEFAULT_RECIPIENT"):
    raise RuntimeError("MAIL_DEFAULT_RECIPIENT not set")

# Make sure default sender is set
if not os.environ.get("MAIL_DEFAULT_SENDER"):
    raise RuntimeError("MAIL_DEFAULT_SENDER not set")

# Make sure mail password is set
if not os.environ.get("MAIL_PASSWORD"):
    raise RuntimeError("MAIL_PASSWORD not set")

stripe.api_key = os.getenv("API_KEY")

# setting up email configurations
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
default_recipient = os.getenv("MAIL_DEFAULT_RECIPIENT")
app.config["MAIL_PORT"] = 465
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True

mail = Mail(app)


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
db = SQL(os.getenv("DATABASE_URL"))

# start
class SQL(object):
    def __init__(self, url):
        try:
            self.engine = sqlalchemy.create_engine(url)
        except Exception as e:
            raise RuntimeError(e)
    def execute(self, text, *multiparams, **params):
        try:
            statement = sqlalchemy.text(text).bindparams(*multiparams, **params)
            result = self.engine.execute(str(statement.compile(compile_kwargs={"literal_binds": True})))
            # SELECT
            if result.returns_rows:
                rows = result.fetchall()
                return [dict(row) for row in rows]
            # INSERT
            elif result.lastrowid is not None:
                return result.lastrowid
            # DELETE, UPDATE
            else:
                return result.rowcount
        except sqlalchemy.exc.IntegrityError:
            return None
        except Exception as e:
            raise RuntimeError(e)
# end

# all services offered - list of dictionaries
all_services = db.execute("SELECT * FROM services")

# create products and prices in stripe if not already created
for item in all_services:

    product_name = item["product"]
    product_id = str(item["id"])
    product_price = item["price"]*100

    all_products = stripe.Product.list()

    if len(all_products) == 0:
        stripe.Product.create(
            id = product_id,
            name = product_name
            )
        stripe.Price.create(
            currency = "gbp",
            product = product_id,
            unit_amount = product_price,
            )
    elif not any(d['id'] == product_id for d in all_products):
        stripe.Product.create(
            id = product_id,
            name = product_name
            )
        stripe.Price.create(
            currency = "gbp",
            product = product_id,
            unit_amount = product_price,
            )
    else:
        continue

# list of all products and prices in stripe (list of dicts)
all_products = stripe.Product.list()
all_prices = stripe.Price.list()


# require login function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# format value as GBP function
def gbp(value):
    return f"£{value:,.2f}"

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
#@app.route("/roadmap")
# @login_required
#def roadmap():

#   return render_template("roadmap.html")



# potentially more functionality to expand the website - more interaction
#@app.route("/eligibility", methods=["POST", "GET"])
#@login_required
#def eligibility():

#    return render_template("eligibility.html")


# display the services offered
@app.route("/services", methods=["GET"])
def services():
    services = db.execute("SELECT * FROM services")
    return render_template("services.html", services=services)


# display the basket of chosen services
@app.route("/basket", methods=["GET", "POST"])
def basket():

    # Ensure basket exists
    if "basket" not in session:
        session["basket"] = []

    # POST
    if request.method == "POST":
        id = request.form.get("id")

        if id:
            session["basket"].append(id)
            return redirect("/basket")

    # GET
    else:
        services = db.execute("SELECT * FROM services WHERE id IN (?)", session["basket"])
        total = db.execute("SELECT SUM(price) FROM services WHERE id IN (?)", session["basket"])
        return render_template("basket.html", services=services, total = total)




# checkout to pay
@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():

    if request.method == "GET":
        services = db.execute("SELECT * FROM services WHERE id IN (?)", session["basket"])
        total = db.execute("SELECT SUM(price) FROM services WHERE id IN (?)", session["basket"])
        return render_template("checkout.html", services=services, total = total)

    return render_template("checkout.html")


# if the payment succeeds
@app.route("/success")
def success():

    return render_template("success.html")


# if the payment is cancelled
@app.route("/cancel")
def cancel():

    return render_template("cancel.html")



# stripe checkout page
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():

    # assigning the price ids
    price_1 = all_prices["data"][0]["id"]
    price_2 = all_prices["data"][1]["id"]

    # creating a stripe checkout session
    session = stripe.checkout.Session.create(
        payment_method_types = ["card"],
        line_items=[{"price":price_2, "adjustable_quantity": {"enabled": True,"minimum": 0, "maximum": 1,}, "quantity":1}, {"price":price_1, "adjustable_quantity": {"enabled": True,"minimum": 0, "maximum": 10,}, "quantity":1}],
        mode = "payment",
        success_url = "https://theceng.herokuapp.com/success",
        cancel_url = "https://theceng.herokuapp.com/cancel",
    )
    return jsonify(id=session.id)


# delete an item from the basket
@app.route("/delete", methods=["GET", "POST"])
def delete():

    # POST
    if request.method == "POST":
        id = request.form.get("id")

        try:
            while True:
                session["basket"].remove(id)
        except ValueError:
            pass

        return redirect("/basket")

    # GET
    else:
        return redirect("/basket")


# clear all basket in one go
@app.route("/clear", methods=["GET", "POST"])
def clear():

    # POST
    if request.method == "POST":
        session["basket"].clear()

        return redirect("/basket")

    # GET
    else:
        return redirect("/basket")


# contact page functionality
@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        # fetch the written message
        message=request.form.get("message")

        # fetch the email
        user_email=request.form.get("email")

        # fetch the first name
        name=request.form.get("firstname")

        # fetch the last name
        surname=request.form.get("lastname")

        # fetch the message subject
        message_subject=request.form.get("subject")

        # Query database for username
        check = db.execute("SELECT * FROM contacts WHERE Email = ?", user_email)

        # add the person into contacts if not in there already
        if len(check) == 0:
            db.execute("INSERT INTO contacts (Name, Surname, Email) VALUES(?, ?, ?)", name, surname, user_email)


        # create an inbound message to the personal email
        inbound = f"Sender name: {name} {surname}. \nSender email: {user_email}. \n\n\n\nMessage: {message}"
        msg_in = Message(message_subject, recipients=[default_recipient])
        msg_in.body=inbound
        mail.send(msg_in)

        # create an outbound message to the sender (confirmation of the receipt of the message)
        outbound = f"Dear {name} {surname}, \n\nThanks for contacting TheCEng! We will get back to you soon! \n\nHave a great day! \nTheCEng Team. \n\n\n\n\nMessage you wrote to us: \n\nSubject: {message_subject} \n\n{message}."
        msg_out = Message("Thank you for getting in touch!", recipients=[user_email])
        msg_out.body = outbound
        mail.send(msg_out)

        if len(user_email):
            return render_template("sent.html")
        else:
            return redirect("/contact")

    else:
        return render_template("contact.html")



# register the user
@app.route("/register", methods=["GET", "POST"])
def register():

    # check the cookies
    if "user_id" not in session:
        session["user_id"] = []

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Forget any user_id
        session["user_id"].clear()

        # Query database for username
        check = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        if len(check) != 0:
            return render_template("register.html", apology = "Email already registered.")

        hashed_pw = generate_password_hash(request.form.get("password"))

        # Query database for username
        db.execute("INSERT INTO users (email, hash) VALUES(?, ?)", request.form.get("email"), hashed_pw)

        return render_template("registered.html", registered = "Successfully registered!")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



# login the registered user. If not registered - offer link to register or return apology
@app.route("/login", methods=["GET", "POST"])
def login():

    # check cookies
    if "user_id" not in session:
        session["user_id"] = []

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Forget any user_id
        session["user_id"].clear()

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", apology = "Invalid email and/or password.")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return render_template("apology.html", apology = "Successfully logged in!")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



# log the current user out
@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# viewing account and editing it
@app.route("/account")
@login_required
def account():

    # fetching the user id from cookies
    id_number = session["user_id"]

    # displaying the email (username)
    email = db.execute("SELECT email FROM users WHERE id = ?", id_number)[0]["email"]

    return render_template("account.html", email = email)




# changing the password
@app.route("/password", methods=["GET", "POST"])
@login_required
def password():

    # user id number form the cookies
    id_number = session["user_id"]

    # searching for the email in the database
    email = db.execute("SELECT email FROM users WHERE id = ?", id_number)[0]["email"]

    if request.method == "POST":

        # Query database
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)

        # Ensure old password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            return render_template("account.html", apology = "Old password invalid.")


        # Ensure password was submitted
        if request.form.get("password") != request.form.get("rpassword"):
            return render_template("account.html", apology = "Passwords do not match.")

        hashed_pw = generate_password_hash(request.form.get("password"))

        # change password
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed_pw, id_number)

        return render_template("account.html", apology = "Password changed.")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("account.html", email = email)





# deleting account completely
@app.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_account():

    # user id number from cookies
    id_number = session["user_id"]

    if request.method == "POST":

        # deleting user from the database
        db.execute("DELETE FROM users WHERE id=?", id_number)
        session["user_id"].clear()
        return render_template("apology.html", apology = "Account deleted.")

    else:
        # clearing cookies
        session["user_id"].clear()
        return redirect("/")



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