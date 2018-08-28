from flask import Flask, flash, redirect, request, url_for, session, logging
from flask import render_template, request
from wtforms import Form
import sqlite3
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

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

class UserDB():
    """Here We want to Create the User Database"""
    def __init__(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT, name TEXT)")
        conn.commit()
        conn.close()

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
            # cur.execute("INSERT INTO users VALUES (NULL, ?,?,?,?)",(username, email, password, name))
            return False
        # conn.commit()
        # conn.close()

    def find_user(self, username, password):
        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        result = cur.execute("SELECT * FROM users WHERE username=?",(username,)).fetchone()
        if result:
            return sha256_crypt.verify(password, result[3])
        else:
            return False



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
    if request.method == 'POST':
        # Get Form Fields:
        username = request.form.get('uname')
        password_candidate = request.form.get('password')
        db = UserDB()
        if db.find_user(username, password_candidate):
            return redirect(url_for('home'))
        else:
            flash('Invalid Username')



    return render_template('login.html')

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
    username='doorman'
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    check_existing = cur.execute("SELECT * FROM users").fetchall()# WHERE username=?",(username,)).fetchall()
    # WHERE username=?",(username,))

    print(check_existing)
    # x = sha256_crypt.verify('llabtoof', rows)

# g_api='AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8'
