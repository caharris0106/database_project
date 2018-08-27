from flask import Flask
from flask import render_template, request
import wtforms import Form
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('homepage.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/register")
def register():
    return render_template('register.html')

class RegistrationForm(Form):


if __name__ == '__main__':
    app.run()

g_api='AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8'
