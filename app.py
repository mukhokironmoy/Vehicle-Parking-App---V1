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

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not first_name or not last_name or not username or not password:
            error = "Please do not leave any fields empty!"
            return render_template('register.html', error=error)
        
        return render_template('hello.html', first_name=first_name, last_name=last_name,username=username, password=password)
    
    
if __name__ == "__main__":
    app.run(debug=True)