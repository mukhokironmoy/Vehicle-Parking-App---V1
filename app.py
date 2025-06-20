from flask import Flask, url_for, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1> This is the root page. </h1>"

@app.route('/hello')
def hello_fxn():
    return "Hello Yomnorik!"

@app.route('/user/<name>')
def greet(name):
    return render_template('hello.html', name=name)

if __name__ == "__main__":
    app.run(debug=True)