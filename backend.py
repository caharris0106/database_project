from flask import Flask, flash, redirect, request, url_for, session, logging
from flask import render_template, request
from flask_mail import Mail, Message
from wtforms import Form
import requests
import sqlite3
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import random
import json
g_api='AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8'

app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'booklistsender1000@gmail.com'
app.config['MAIL_PASSWORD'] = 'Reccos:0106'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

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

class LoginForm(Form):

    #Choice of Username
    username = StringField('username', [validators.Length(min=4, max=25)])
    # Choice of Password
    password = PasswordField('Password', [validators.InputRequired()])

class UserDB():
    """This Class deals with registration"""
    # Create users Table if not already there
    def __init__(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT, name TEXT)")
        conn.commit()
        conn.close()

    # Find Out if the registering user already has an account, registers them if they dont
    def new_user(self, username, email, password, name):
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        check_existing = cur.execute("SELECT * FROM users WHERE username=? OR email=?",(username,email)).fetchone()
        if check_existing == None:
            cur.execute("INSERT INTO users VALUES (NULL, ?,?,?,?)",(username, email, password, name))
            conn.commit()
            conn.close()
            return True
        else:
            return False

    # Finds the user for the login page, verifies the password
    def find_user(self, username, password):
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        result = cur.execute("SELECT password FROM users WHERE username=?",(username,)).fetchone()
        if result:
            return sha256_crypt.verify(password, result[0])#[3])
        else:
            return False

    def grab_info(self, username):
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        # Gets the user id, username, email
        user_row = cur.execute("SELECT id,username,email FROM users where username=?", (username,)).fetchone()
        conn.commit()
        conn.close()
        return user_row

class BooksDB():
    '''This Class Deals with the book Table'''
    def __init__(self):
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS books (id INT, username TEXT, email TEXT, book Text, authors TEXT, googleID TEXT)")
        conn.commit()
        conn.close()

    def grab_info(self, username):
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        # Gets the user id, username, email
        user_row = cur.execute("SELECT id,username,email FROM users where username=?", (username,)).fetchone()
        conn.commit()
        conn.close()
        return user_row

    def insert_book(self, id, username, email, book, authors, googleID):
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        book_indb = cur.execute("SELECT * from books WHERE book=? AND username=?",(book,username)).fetchone()
        if book_indb==None:
            # Insert into Books, id, username, email, book, authors, glink
            cur.execute("INSERT INTO books VALUES (?,?,?,?,?,?)", (id, username, email, book, authors, googleID))
            conn.commit()
            conn.close()
            return True
        else:
            return False
    def delete_book(self, book, username):
        conn=sqlite3.connect("users.db")
        cur = conn.cursor()
        book_indb = cur.execute("SELECT * from books WHERE book=? AND username=?",(book,username)).fetchone()
        if book_indb!=None:
            # Insert into Books, id, username, email, book, authors, glink
            cur.execute("DELETE FROM books WHERE username=? AND book=?", (username, book))
            conn.commit()
            conn.close()
            return True
        else:
            return False
    def create_json(self, username):
        # Return a Json File from books db for display
        conn=sqlite3.connect('users.db')
        cur=conn.cursor()
        jfile = cur.execute('SELECT book, authors, googleID FROM books WHERE username=?', (username,)).fetchall()
        books = dict(total=0, items=list())
        for book, authors, googleID in jfile:
            books['items'].append(dict(book=book,authors=authors, googleID=googleID))
            books['total'] +=1
        return books


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Make New User
        db = UserDB()
        if db.new_user(username, email, password, name):
            flash("You Are Now Registered and can Login", "Success")
        else:
            flash("Email or Username in Use Already")
            return render_template('register.html', form=form)
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route("/login", methods=['GET','POST'])
def login():
    session.clear()
    form = LoginForm(request.form)
    if request.method == 'POST':
        # Get Form Fields:
        username = form.username.data
        password_candidate = form.password.data
        db = UserDB()
        if db.find_user(username, password_candidate):
            session['logged_in'] = True
            session['username'] = username

            flash("Logged in as {}!".format(username))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Username Or Password')

    return render_template('login.html', form=form)

# @app.route("/test")
# def test():
#     if session['logged_in']:
#         return session.username

@app.route("/")
def home():
    return render_template('home.html', books=requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
            'python' +
             "&maxResults=40&key=AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8").json())

@app.route("/search", methods=["GET","POST"])
def search():

    if request.method=='POST':
        
        if not request.form.get("title"):
            flash("Enter a title")

        if request.form.get("author"):
            return render_template("searchResults.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                               request.form.get("title") + "+inauthor:" + request.form.get("author") +
                               "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json())

        if request.form.get("author"):
            return render_template("searchResults.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                               request.form.get("title") + "+isbn:" + request.form.get("isbn") +
                               "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json())

        if request.form.get("author") + request.form.get("isbn"):
            return render_template("searchResults.html", books = requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                               request.form.get("title") + "+inauthor:" + request.form.get("author") +
                               "isbn:" + request.form.get("isbn") +
                               "&key=AIzaSyBtprivgL2dXOf8kxsMHuELzvOAQn-2ZZM").json())

        return render_template("searchResults.html", books=requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
                    request.form.get("title") +
                    "&key=AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8").json())

    return render_template("search.html")

@app.route("/searchResults", methods=["GET","POST"])
def searchResults():
    return render_template("searchResults.html")

@app.route("/dashboard")
def dashboard():
    books = BooksDB().create_json(session['username'])
    # if request.method == 'POST':
    #
    #     msg = Message('Thank you for registration', sender = 'booklistsender1000@gmail.com', recipients = ['caharris0106@gmail.com'])
    #
    #     # define content of the email
    #     msg.body = """Hello and thank you for join us! We hope you enjoy at our site where you can search, read, comment and grade your favourite books. Have fun!"""
    #
    #     # send email
    #     mail.send(msg)
    return render_template('dashboard.html', session=session, books=books)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/redir/<title>/<author>/<googleID>")
def redir(title, author, googleID):
    book_db = BooksDB()
    user_id = book_db.grab_info(session['username'])[0]
    email = book_db.grab_info(session['username'])[2]
    book_title = title
    book_id = googleID
    book_author = author.replace('[','').replace(']','').replace('\'','')
    book_db.insert_book(user_id, session['username'], email, book_title, book_author, book_id)
    return redirect(url_for('dashboard'))

@app.route("/logout")
def logout():
    session.clear()
    # random.choice('abcdefghijklmnopqrstuvwxzy')
    return render_template('home.html', books=requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
            'computer' +
             "&maxResults=40&key=AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8").json())

if __name__ == '__main__':

    app.secret_key = 'secret123'
    app.run(debug=True)
    # conn = sqlite3.connect('users.db')
    # cur = conn.cursor()
    # cur.execute("DROP TABLE books")
    # conn.commit()
    # conn.close()
    # book= 'Principles'
    # book_indb = cur.execute("SELECT * from books WHERE book=?",(book,)).fetchone()
    # if book_indb==None:
    #     # Insert into Books, id, username, email, book, authors, glink
    #     cur.execute("INSERT INTO books VALUES (?,?,?,?,?)", (2, 'a','a',book,'a'))
    #     conn.commit()
    #     conn.close()
    # username='charris52'
    # conn=sqlite3.connect('users.db')
    # cur=conn.cursor()
    # jfile = cur.execute('SELECT book, authors, googleID FROM books WHERE username=?', (username,)).fetchall()
    # file_test = BooksDB().create_json(username)
    # print(file_test)
    # bks=requests.get("https://www.googleapis.com/books/v1/volumes?q=" +
    #         'a' +
    #         "&key=AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8").json()
    # print(type(bks))
    # g_api='AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8'
