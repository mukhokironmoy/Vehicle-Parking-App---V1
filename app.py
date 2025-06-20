from flask import Flask, url_for, render_template, request
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

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "yomnorik" and password == "pw":
            return render_template('hello.html', name=username, password=password)
        else:
            return render_template('login.html', caution = "Username or Password is incorrect. Please try again." )

if __name__ == "__main__":
    app.run(debug=True)