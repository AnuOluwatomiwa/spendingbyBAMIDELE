import datetime
import os

from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def generate_filename(username, original_filename):
    # Get the current time
    time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Extract the extension from the original filename
    _, extension = os.path.splitext(original_filename)

    # Create the new filename
    new_filename = "{}_{}{}".format(username, time, extension)

    return new_filename


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# Custom filter for formatting to my local currency
def ngn(value):
    return f"₦{(value):,.2f}"
