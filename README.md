# spendingbyBAMIDELE
#### Video Demo:  https://youtu.be/2Z49gGAvryU?si=-xt2hXLesSJwvzfz
#### Description:
spending by BAMIDELE is a web application designed with HTML, CSS, Javascript, Python, SQL, Flask, Jinja and Bootstrap
I initialized and concluded the application on codespaces, my project folder contains some files, including an app.py,
helpers.py, README.md, transactions.db files and flask_session, static and templates folders.

I started out this project with the aim to be rendered on smart watches to provide users with a quick glance of their "spentToday", but considering the ease of rendering as a webapplication compared to a smartwatch, (and also considering a rendering centering around the knowledge I gained in cs50). I prepared this web application for desktop use.

In my app.py file i began with some important imports including SQL from cs50, for my database management.
Flask, redirect, render_template, request, session from flask for purposes of rerouting from templates to templates, session management, user identification and more.
imghdr to verify that users include an actual image file, whether jpg, png or similar when registering, which isn't compulsory, but just to prevent uploading of files other than static visual files.
check_password_hash and generate_password_hash from werkzeug.security to scramble users password upon registeration as well as verify the password in cases of user login.
Also another significant import is the secure_filename import from werkzeug.utils module used to ensure that the filename received from the user is a safe filename. Removing any potentially dangerous characters, such as slashes or special symbols, which could be used to traverse directories or execute commands. This is particularly useful because of the data accepting nature of my web application from users to be stored on my server. It helps to prevent any security issues related to file handling.

While implementing my webapp, i made provision for the submission of an image file by registrants, to set as a profile photo
considering the load to be posed on my database from several image files, i opted for a cloud option, google drive, i navigated through the Google drive API
documentation (https://developers.google.com/drive/api/guides/about-sdk), and started implementing, i did some OAUTH things, set some keys and even downloaded a credentials.json and token.json file
to my project folder, then tried to connect my application to Google Drive, after several attempts i couldm't get past it, there was an issue with some keys not matching from my web application and Google's authorization system
when i looked into it, i observed that everytime i run flask run, a new id is dynamically generated, and on the API end, a dedicated id is required to be stated to be authorized, i eventually gave up on integrating google Drive's API
, i would later implement this idea with a simpler approach.

The final imports are some custom functions from my helpers.py file, generate_filename that accepts two argument variables(username, original_filename) and generates a unique filename by getting the current time with the datetime.now() function, then using the os.path and excluding the file's extension, extracts the original filename which has prior been santized( with the secure_filename function), creates a newfilename formatted (username, time, extension) and then returns the new_filename. apology (based of Week 9's Pset, renders apology in respective error situations).
login_required(which is not my intellectual property, restricts certain actions or routing until a session is established).
ngn, function formats numbers to my local currency, i used this in several of my html files.

The line15 in app.py app.jinja_env.filters["ngn"] = ngn shows the adding of a filter named "ngn" which uses function ngn from helpers.py to process data.

the preceeding line of code is the application configuration, app = Flask(__name__)

Followed by some session configurations to use filesystem (instead of signed cookies)

Then the cs50 library's configuration to use SQLite database as db = SQL("sqlite:///transactions.db")

next is the setting up of a function to modify every response from my Flask application to prevent caching. The @app.after_request decorator does the registering of functions to be run.


after then does the routing begin, with index function being the first
displaying the dashboard of the current logged in user
I proceed with explicit queries to probe my db for the current username ,
balance information,
spent today, where which i encountered some issues with rendering (internal server error) where a user logs in with no value for "spent today"  my query returned "NONE" since my today variable accepts only digits, i encountered an issue with value assigning to the variable, so i prepared a failsafe with a simple if conditional on line 59 of my app.py.
And also profilePhoto


Followed by the more verbose functions withdraw and deposit
Withdraw consists of several checks like if the user does or not provide
1. an amount
2. ''  ''    that is digit
3. ''  ''    that is < or =  to '0'
4. and more important checks, implemented with if conditionals
I then proceeded with adding the successful withdrawal to the database
with db.execute(explicit SQL statements).
Finally updating the users balance on the users table and then returning redirect or rendering my html if visited via GET.

In def deposit():
I queried my database for the current balance of the user then
Several conditionals to check for proper usage,
a conversion of the request.form.get value to be deposited to an integer
after a successful deposit, the new available balance is calculated
Still under deposit, i generate a default value for the description of the deposit, by concatenating select values from the submitted form. That is assigned to the variable if the user chooses not to add a description noted with the (optional) placeholder.
Following are the SQL statements to insert the successful deposit into the transactions table and update the balance column on the users tableenclosed in db.execute()
then rerouting, provision is made for POST and GET.

in the history function
Queries to probe the db for the current username, then the transaction history of select user, returned as a list of dictionaries, followed by an indexing into each row in the list and assigning several values from key-value pairs,concatenated to a single variable which would now be a new key-value pair. as seen on line 230 in app.py.

the idea of moneyIn and moneyOut is to filter transactions history based on the category column of my table, whether inward or outward transfer, achieved also with some SQL queries ORDER-ed by date and time in DESC-ending order.

Line 266 initializes the routing to the login function, which starts by clearing whichever session exists in the browser initially.
Followed by important conditionals to check for proper login usage, such as username and pass' existence. Line 295 in app.py notes the current user logged in, and if requested via GET redirection to my login.html template, otherwise "/".

My register function commences on line 305 in app.py, for the purpose of registering a new user,
kicking off with assigning a default value for the image expected to be uploaded by the registrant, and deliberately declared outside any loop, to exempt it from being constrained by any conditional. The following are specific conditionals to check proper usage of the registration form
Then the function declares a list of all existing usernames, then checks it against the username provided by the registrant to ensure uniqueness of every username.
If line 331 in app.py doesn't execute, then username and (hashed)password variables are created, followed by a check if the user uploads any image file on line 338 of app.py i used the imghdr on line 340 in app.py to check the image upload validity, with indexing into the file content and assigning the binary format of the image to my variable, using the secure_filename function imported from werkzeug.utils on line 6 in app.py to sanitize the image name, then reading the file into memory, i implemented a logic to generate a unique name for each user's profilePhoto file with a custom function i created "generate_filename()" which accepts two argvs and generates a unique filename.

I was able to accept image files from user as profile photo and limit type
 if request.files.get("profile_photo"):
            # handle the image upload
            file = request.files['profile_photo']
            #Fetching original filename
            original_filename = file.filename
            file_data = file.read()

        new_filename = generate_filename(username, original_filename)

        with open(f'profilePhoto/{new_filename}', 'wb') as f:
            f.write(file_data)

I also had to learn more in order to correctly pass my filename and route containing the user's uploaded images to render it back in my index.html

On line 349, with file open in "write binary" mode, the image is read into memory.
Where a user uploads anything other than an image file, i used the error code 415 which i learnt is for unsupported media type, this HTTP status code indicates that the server refuses to accept the request, usually because the payload format is supposedly in an unsupported format for this method on the target resource.

After a successful image file acceptance follows the entry of the image name into the 'profilePhoto' column of the users table, with the statement starting on line 355 in app.py


On line 367 is the beginning of my "forgot" routing and function which is for changing password for a profile, after some essential identity confirmations like double checking the new password, the new password is hashed and the script is updated in the hash column of the respective user.
line 383 in app.py commences the SQL statement to update the user info on the table, followed by the routing depending on approach method, which is either GET or POST.

Then the logout function runs the session.clear()

In the case of my index function in app.py
the spent_today variable which assumes the result of an SQL query, returned and passed None, into my ngn function in helpers.py, where a float was expected triggering an error that i fixed with a conditional, this error was because the query couldn't return a value, because the design was to return a float representing the transaction value for the day, with no transaction recorded yet, an error was triggered.

I also added the convenience of visibility, in the case of my history table and similar, with succinct queries like SELECT * FROM transactions ORDER BY date DESC, time DESC;, ensuring a more usable transaction table

Next is my helpers.py file, initializing with several important imports like csv for database purposes, datetime, requests and more..

starts with an helper function defined as apology that accepts a message and error code, used in rendering apology messages in cases of improper usage.

on line 40 in helpers.py is the aforementioned generate_filename function for uniquely naming profilePhoto files uploaded by registrants.

line 53 in helpers.py shows the initialization of a decorator limiting access to routes to only after session initialization.

the final function defined here is the filter for formatting text to my local currency

I learnt about legibility standards from https://www.w3.org/TR/UNDERSTANDING-WCAG20/visual-audio-contrast-contrast.html

my transactions.db file contains the database that runs the webapplication, majorly to provide information rendered via sections like, spent_today, available_balance, history, moneyIn, moneyOut and also keeping track of user identity, passwords and balance update with schema
CREATE TABLE sqlite_sequence(name,seq);
    this table automatically initializes in a flask application

CREATE TABLE transactions
(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, date DATE,
username TEXT NOT NULL, moneyIn NUMERIC,
moneyOut NUMERIC, category TEXT NOT NULL,
to_from TEXT NOT NULL, description TEXT NOT NULL, time TIME, balance NUMERIC NOT NULL);

CREATE TABLE users
(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
username TEXT NOT NULL, hash TEXT NOT NULL,
balance NUMERIC DEFAULT 10000.00,
profilePhoto TEXT DEFAULT 'static/profilePhoto/profilePhoto.svg');

In the templates subfolder there are multiple html files
1. apology.html
2. deposit.html
3. forgot.html
4. history.html
5. index.html
6. layout.html
7. login.html
8. moneyIn.html
9. moneyOut.html
10. register.html
11. withdraw.html

all except 6. being an extension of layout.html, containing the structure and orientation of the visibles to be rendered to users.


In my static folder, images are present here, in several formats, including png and jpg.
Also a favicon subdirectory that contains the favicon files for my project
Also my script which has been linked to my layout.html file exists in this folder as script.js, where in i got elements that display balanceby class, then created a toggleBalance function, whose purpose is to hide and unhide financial information, using an eventListener to wait for onclick.
we have my styles.css containing the external styling for my html files
