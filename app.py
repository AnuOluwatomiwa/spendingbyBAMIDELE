from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import imghdr
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import generate_filename, apology, login_required, ngn

# importing drive functions

# Configure application
app = Flask(__name__)

app.jinja_env.filters["ngn"] = ngn

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///transactions.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show user dashboard"""
    # Query for current username
    username_info = db.execute(
        "SELECT username FROM users WHERE id = :id", id=session["user_id"]
    )
    username = username_info[0]["username"]

    # Query for Available Balance
    balance_info = db.execute(
        "SELECT balance FROM users WHERE username = :username", username=username
    )
    balance = balance_info[0]["balance"]
    if balance is None:
        balance = 0

    # Query for Spent today
    spent_today = db.execute(
        "SELECT SUM(moneyOut) AS total FROM transactions WHERE username = :username AND date = CURRENT_DATE",
        username=username,
    )
    today = spent_today[0]["total"]
    if today is None:
        today = 0

    # Query for profilePhoto
    profilePhoto_info = db.execute(
        "SELECT profilePhoto FROM users WHERE id = :id", id=session["user_id"]
    )
    profilePhoto = profilePhoto_info[0]["profilePhoto"]

    # TODO render filename from schema to display profile photo
    return render_template(
        "index.html",
        username=username,
        balance=balance,
        today=today,
        profilePhoto=profilePhoto,
    )


@app.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():
    """withdraw amount"""
    if request.method == "POST":
        # Check if amount is not inputted
        if not request.form.get("amount"):
            return apology("must provide amount", 403)
        if not request.form.get("amount").isdigit():
            return apology("Input amount", 400)
        if int(request.form.get("amount")) <= 0:
            return apology("Input postive amount", 400)
        if not request.form.get("bank"):
            return apology("must provide bank", 403)
        if not request.form.get("receiver"):
            return apology("must provide receiver", 403)
        if not request.form.get("account_number"):
            return apology("must provide account number", 403)

        # Query for current username
        username_info = db.execute(
            "SELECT username FROM users WHERE id = :id", id=session["user_id"]
        )
        username = username_info[0]["username"]

        withdrawal = int(request.form.get("amount"))

        # Check if the user has enough balance
        balance_info = db.execute(
            "SELECT balance FROM users WHERE id = :id", id=session["user_id"]
        )
        balance = balance_info[0]["balance"]
        if withdrawal > balance:
            return apology("Insufficient balance", 403)

        # Add withdrawal to transactions table
        to_from = (
            request.form.get("receiver")
            + "-"
            + request.form.get("account_number")
            + "-"
            + request.form.get("bank")
        )
        description = request.form.get("description")
        if not description:
            description = "Withdrawal to " + to_from
        # Calculate new balance
        newbalance = balance - withdrawal
        db.execute(
            "INSERT INTO transactions (date, username, moneyIn, moneyOut, category, to_from, description, time, balance) VALUES(date('now'), :username, :moneyIn, :moneyOut, :category, :to_from, :description, time('now'), :balance)",
            username=username,
            moneyIn="0",
            moneyOut=withdrawal,
            category="outward transfer",
            to_from=to_from,
            description=description,
            balance=newbalance,
        )
        # Update cash balance after deduction
        db.execute(
            "UPDATE users SET balance = :newbalance WHERE username = :username",
            newbalance=newbalance,
            username=username,
        )

        return redirect("/")

    return render_template("withdraw.html")


@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    """Deposit"""
    # Query for current username
    username_info = db.execute(
        "SELECT username FROM users WHERE id = :id", id=session["user_id"]
    )
    username = username_info[0]["username"]

    # Check the user's balance
    balance_info = db.execute(
        "SELECT balance FROM users WHERE id = :id", id=session["user_id"]
    )
    balance = balance_info[0]["balance"]

    if request.method == "POST":
        # Check if amount is not inputted
        if not request.form.get("amount"):
            return apology("must provide amount", 403)
        if not request.form.get("amount").isdigit():
            return apology("Input amount", 400)
        if int(request.form.get("amount")) <= 0:
            return apology("Input postive amount", 400)
        if not request.form.get("bank"):
            return apology("must provide bank", 403)
        if not request.form.get("depositor"):
            return apology("must provide depositor", 403)
        if not request.form.get("account_number"):
            return apology("must provide account number", 403)

        # Calculate new balance
        deposit = int(request.form.get("amount"))
        newbalance = balance + deposit
        # Description
        to_from = (
            request.form.get("depositor")
            + "-"
            + request.form.get("account_number")
            + "-"
            + request.form.get("bank")
        )
        description = request.form.get("description")
        if not description:
            description = "Deposit from " + to_from
        # Update transactions table
        db.execute(
            "INSERT INTO transactions (date, username, moneyIn, moneyOut, category, to_from, description, time, balance) VALUES(date('now'), :username, :moneyIn, :moneyOut, :category, :to_from, :description, time('now'), :balance)",
            username=username,
            moneyIn=deposit,
            moneyOut="0",
            category="inward transfer",
            to_from=to_from,
            description=description,
            balance=newbalance,
        )

        # Add funds to users cash balance
        db.execute(
            "UPDATE users SET balance = :newbalance WHERE username = :username",
            newbalance=newbalance,
            username=username,
        )

        return redirect("/")
    return render_template("deposit.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
     # Query for current username
    username_info = db.execute(
        "SELECT username FROM users WHERE id = :id", id=session["user_id"]
    )
    username = username_info[0]["username"]
    history = db.execute(
        "SELECT * FROM transactions WHERE username = ? ORDER BY date DESC, time DESC",
        username,
    )
    for row in history:
        row["value"] = row["moneyIn"] + row["moneyOut"]
    return render_template("history.html", history=history)


@app.route("/moneyIn")
@login_required
def moneyIn():
    """Show moneyIn from transactions"""
    # Query for current username
    username_info = db.execute(
        "SELECT username FROM users WHERE id = :id", id=session["user_id"]
    )
    username = username_info[0]["username"]
    moneyIn = db.execute(
        "SELECT * FROM transactions WHERE category = 'inward transfer' AND username = ? ORDER BY date DESC, time DESC",
        username,
    )
    return render_template("moneyIn.html", moneyIn=moneyIn)


@app.route("/moneyOut")
@login_required
def moneyOut():
    """Show moneyOut from transactions"""
    # Query for current username
    username_info = db.execute(
        "SELECT username FROM users WHERE id = :id", id=session["user_id"]
    )
    username = username_info[0]["username"]
    moneyOut = db.execute(
        "SELECT * FROM transactions WHERE category = 'outward transfer' AND username = ? ORDER BY date DESC, time DESC",
        username,
    )
    return render_template("moneyOut.html", moneyOut=moneyOut)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    new_filename = "profilePhoto/profilePhoto.svg"

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check if textbox is blank
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Check if password box is blank
        if not request.form.get("password"):
            return apology("must provide password", 400)
        # Check if password is cross-checked
        if not request.form.get("confirmation"):
            return apology("must retype password", 400)
        # Check if passwords match
        if not request.form.get("confirmation") == request.form.get("password"):
            return apology("passwords do not match", 400)

        # Declare a list of existing usernames
        rows = db.execute(
            "SELECT * FROM users WHERE username = :username",
            username=request.form.get("username"),
        )
        if len(rows) > 0:
            return apology("username is already taken!")

        # Create username and password variables
        username = request.form.get("username")
        hashed_password = generate_password_hash(request.form.get("password"))

        # Check if image is uploaded
        if request.files.get("profile_photo"):
            # Check image validity
            if imghdr.what(request.files.get("profile_photo")) is not None:
                # handle the image upload
                file = request.files["profile_photo"]
                # Fetching original filename
                original_filename = secure_filename(file.filename)
                file_data = file.read()

                new_filename = generate_filename(username, original_filename)

                with open(f"static/profilePhoto/{new_filename}", "wb") as f:
                    f.write(file_data)
            else:
                return apology("Upload an image file", 415)

        # Insert new registrant into database
        db.execute(
            "INSERT INTO users (username, hash, profilePhoto) VALUES(:username, :hashed_password, :new_filename)",
            username=username,
            hashed_password=hashed_password,
            new_filename=new_filename,
        )
        return render_template("login.html")

    else:
        return render_template("register.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        # Check if username exists
        # Declare a list of existing usernames
        rows = db.execute("SELECT username FROM users")
        usernames = [row["username"] for row in rows]
        if not request.form.get("username") in usernames:
            return apology("username does not exist!")

        # Check that passwords match
        if not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords do not match", 403)

        # Change Password
        hashed_password = generate_password_hash(request.form.get("password"))
        db.execute(
            "UPDATE users SET hash = :hashed_password WHERE username = :username",
            hashed_password=hashed_password,
            username=request.form.get("username"),
        )
        return render_template("login.html")

    return render_template("forgot.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
