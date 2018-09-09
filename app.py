from flask import Flask, flash, redirect, request, url_for, session, render_template
from flask_mail import Mail, Message
from flask_session import Session
from flask_sslify import SSLify
from wtforms import Form
import requests
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy
import random
import json
import os

g_api='AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8'

# Instantiate flask and flask mail
app = Flask(__name__)

if 'DYNO' in os.environ:
    sslify = SSLify(app)

# Configure session type, and permanence
app.secret_key = os.urandom(24)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = 3600
app.config["SESSION_COOKIE_SECURE"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vmlfkxjbhtupoc:f7eda27955cdafac485d8d163a6b8cae5a9d4bd53a2cef3b29a2645bfe0fda1f@ec2-54-204-46-60.compute-1.amazonaws.com:5432/d99b7oie922v8a'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure App for mail, secret_key, and postres URI
app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'booklistsender1000@gmail.com'
app.config['MAIL_PASSWORD'] = 'Reccos:0106'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:paperclip@localhost:5433/books'
# Instantiate SQLALCHEMY
db = SQLAlchemy(app)
Session(app)

# Class Used to take user input from register.html
class RegisterForm(Form):
    #Name of Person
    name = StringField('Name', [validators.Length(min=1, max=50)])

    #Choice of Username
    username = StringField('username', [validators.Length(min=4, max=25)])

    # Email of Person
    email = StringField('Email', [
    validators.Length(min=6, max=50),
    validators.Email(message='Enter a Valid Email')
    ])

    # Password and it confirmation
    password = PasswordField('Password', [
    validators.InputRequired(),
    validators.EqualTo('confirm', message='Passwords dont match')
    ])
    confirm = PasswordField('Confirm Password')

# Class for Login Form
class LoginForm(Form):

    #Choice of Username
    username = StringField('username', [validators.Length(min=4, max=25)])
    # Choice of Password
    password = PasswordField('Password', [validators.InputRequired()])

# WT-Forms Class for Changing Password
class ChangePassForm(Form):

    # Choice of Password
    password_old = PasswordField('Password', [validators.InputRequired()])

    password_new = PasswordField('Password', [
    validators.InputRequired(),
    validators.EqualTo('confirm', message='Passwords dont match')
    ])

    confirm_new = PasswordField('Confirm Password')


# WT-Forms for Deleteing acount
class DeleteAccountForm(Form):

    password = PasswordField('Password', [validators.InputRequired()])


# Class for Object Relational Mapper of user Table
class User(db.Model):
    '''
    'user' table has a name, username, email, password column
    The first column is a primary key(Integer)
    '''


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def __init__(self, name, username, email, password):
        __table_args__ = {'extend_existing': True}
        self.name = name
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

# Class for Object Relational Mapper for books table
class Books(db.Model):
    '''
    Class Books takes in a user_id, username, email, title of a book,
    the others of the book, and an ID from google Books

    The first column is the primary key
    '''
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False)
    book = db.Column(db.String(256), nullable=False)
    authors = db.Column(db.String(256), nullable=False)
    googleID = db.Column(db.String(256), nullable=False)

    def __init__(self, user_id, username, email, book, authors, googleID):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.book = book
        self.authors = authors
        self.googleID = googleID

    def __repr__(self):
        return '<User %r>' % self.username


@app.route("/register", methods=['GET', 'POST'])
def register():
    '''Registers User With wt-form'''
    # Instantiate wt-form for registration
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        # Take data from the form from register.html
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Check if the username or email is already used
        user_count = User.query.filter_by(username=username).count()
        email_count = User.query.filter_by(email=email).count()

        if user_count==0 and email_count==0:
            # If the database doesnt contain the username and email,
            # Add the information to teh user table
            db.session.add(User(name=name, username=username, email=email, password=password))
            db.session.commit()
            flash("You Are Registered and Can Log In")
            return redirect(url_for('login'))
        else:
            flash("Username or Email Already in Use")

    return render_template('register.html', form=form)


@app.route("/login", methods=['GET','POST'])
def login():
    '''Function To Login a user who is registered'''

    # Clear the Session, No user is logged in
    session.clear()

    # Instantiate wt-form for logging in
    form = LoginForm(request.form)
    if request.method == 'POST':

        # Set variables for form data
        username = form.username.data
        password = form.password.data

        # Checks to see if the user is in the user Table
        find_username = User.query.filter_by(username=username).first()
        if find_username == None:
            flash("Invalid Username Or Password")
        else:
            # Verify Password with passlib
            if sha256_crypt.verify(password,find_username.password):

                # Logs the User in with flask-session
                session['logged_in'] = True
                session['username'] = username
                # Takes the user to homepage
                return redirect(url_for('home'))
            else:
                flash("Invalid Username Or Password")

    return render_template('login.html', form=form)


@app.route("/")
def home():
    ''' Page Displaying Up to 40 Books from google API '''
    return render_template('home.html', books=requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
            'python' +
             "&maxResults=40&key=AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8").json(), session=session)

@app.route("/search", methods=["GET","POST"])
def search():
    ''' Main Function for searching for books '''
    if request.method=='POST':
        # Checks if Any of the inputs are filled and if they are not sends the user a message
        if not request.form.get("title") and not request.form.get('author') and not request.form.get('isbn'):
            flash("Enter a title, author, isbn")
            return render_template("search.html", session=session)

        # Request from Google API for and author and title
        if request.form.get("author"):
            return render_template("searchResults.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                               request.form.get("title") + "+inauthor:" + request.form.get("author") +
                               "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json())
        # Request from Google API for and isbn and title
        if request.form.get("isbn"):
            return render_template("searchResults.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                               request.form.get("title") + "+isbn:" + request.form.get("isbn") +
                               "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json())
        # Request from Google API for and isbn and title and author
        if request.form.get("author") and request.form.get("isbn"):
            return render_template("searchResults.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                               request.form.get("title") + "+inauthor:" + request.form.get("author") +
                               "isbn:" + request.form.get("isbn") +
                               "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json())
        # Request from Google API for title
        return render_template("searchResults.html", books=requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                    request.form.get("title") +
                    "&key=AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8").json())

    # If No Search is submitted, template for blank search page is rendered
    return render_template("search.html", session=session)

@app.route("/searchResults", methods=["GET","POST"])
def searchResults():
    ''' Function For Rendering template to display all the books from the google API '''
    return render_template("searchResults.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    ''' Function to display the users catalog of books '''
    user = User.query.filter_by(username = session['username']).first()
    all_books = Books.query.filter_by(username = user.username).all()

    # Convert the booklist to a json-type dictionary for display and messaging
    books = dict(total=0, items=list())
    for item in all_books:
        books['items'].append(dict(book=item.book,authors=item.authors, googleID=item.googleID))
        books['total'] +=1

    # Get email from database and leave it in session
    session['email'] = user.email

    # Sends a message to the users email
    if request.method == 'POST':

        msg = Message('Book List', sender = 'booklistsender1000@gmail.com', recipients = [session['email']])

        # Create a Message String for an email to be sent automatically
        message_string = ''
        for item in books['items']:
            message_string += 'Book: '+item['book']+'\n'+'Author(s): '+item['authors']+'\n'+'Google ID: '+item['googleID']+'\n\n'

        # define content of the email
        msg.body = message_string

        # send email
        mail.send(msg)

        flash("Message Sent")
        render_template('dashboard.html', session=session, books=books)

    #Template if no message is sent
    return render_template('dashboard.html', session=session, books=books)

@app.route("/about")
def about():
    return render_template('about.html', session=session)

@app.route("/redir/<title>/<author>/<googleID>")
def redir(title, author, googleID):
    '''
    This Function takes an html "GET" request of the book selected from google query,
    then redirects the user to the dashboard. The user is looked up in the 'user'
    table of the database, some information (user id, email, username) is inserted into
    the books database along with the selected book title, author, and google ID
    '''
    user = User.query.filter_by(username=session['username']).first()
    user_id = user.id
    email = user.email
    book_title = title
    book_id = googleID
    book_author = author.replace('[','').replace(']','').replace('\'','')
    username_id_count = Books.query.filter_by(username=session['username']).count()
    google_id_count = Books.query.filter_by(googleID=book_id).count()
    # Check by googleID if the book is put into the database already
    if username_id_count > 0 and google_id_count>0:
        flash("Youve Alread Added That Book")
        return redirect(url_for('dashboard'))

    db.session.add(Books(user_id=user_id, username=session['username'], email=email, book=book_title, authors=book_author, googleID=book_id))
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route("/remove_book/<title>")
def remove_book(title):
    '''
    This function uses an html 'GET' request with the title of a book,
    and deletes the title from the 'books' table
    '''
    Books.query.filter_by(book=title).delete()
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route("/accountDetails", methods=['GET', 'POST'])
def accountDetails():
    '''
    Account Details displays the users name, username, and email,
    and gives the option to change the password
    '''
    form = ChangePassForm(request.form)
    session['name'] = User.query.filter_by(username=session['username']).first().name
    if request.method == 'POST':
        # Get Form Fields:
        password_old = form.password_old.data
        password_new = sha256_crypt.encrypt(str(form.password_new.data))

        user = User.query.filter_by(username=session['username']).first()

        if sha256_crypt.verify(password_old, user.password):
            user.password = password_new
            db.session.commit()
            flash("Password Changed!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Password")
    return render_template('accountDetails.html', session=session, form=form)


@app.route("/deleteAccount", methods=['GET', 'POST'])
def deleteAccount():
    form = DeleteAccountForm(request.form)
    if request.method == 'POST':
        # Get Form Fields:
        password = form.password.data
        user = User.query.filter_by(username=session['username']).first()
        b_user = Books.query.filter_by(username=session['username']).all()
        if sha256_crypt.verify(password, user.password):
            db.session.delete(user)
            for x in b_user:
                db.session.delete(x)
            db.session.commit()
            flash('Account Deleted')
            return redirect(url_for('login'))
        else:
            flash('Invalid Password')
    return render_template('deleteAccount.html', session=session, form=form)


@app.route("/logout")
def logout():
    session.clear()
    return render_template('home.html', books=requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
            'computer' +
             "&maxResults=40&key=AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8").json())

# catch all other routes that doesn't exist
@app.errorhandler(404)
def page_not_found(e):
    return render_template("pageNotFound.html")


if __name__ == '__main__':
    app.run()
