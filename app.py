from flask import Flask, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1> Welcome! </h1>"

@app.route('/hello')
def hello_fxn():
    return "Hello Yomnorik!"

@app.route('/user/<name>')
def greet(name):
    return f"""Hi there, {name}! How're you doing?\n\n Here's a link to go back: <a href = "{url_for('home')}"> Go back from here :) </a>"""


if __name__ == "__main__":
    app.run(debug=True)