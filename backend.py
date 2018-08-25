from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('homepage.html')

# @app.route('/name')
# def name():
#     return 'Cody'

# @app.route('/hello/')
# @app.route('/hello/<name>')
# def hello(name=None):
#     return render_template('hello.html', name=name)

# @app.route('/home')
# def crud():
#     return render_template('homepage.html')

if __name__ == '__main__':
    app.run()

g_api='AIzaSyAvHykLgaS8U3WrOp48sbNcI_lAtBmLyD8'
