from flask import Flask, url_for, render_template, request
from extensions import db
from logging_config import logger, user_test_reference
app = Flask(__name__)

#config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#db instance
db.init_app(app)

#importing models
from models.user import User

'''----------------------------------------------------------------------------------------------------------------------------------------------'''
#root 
@app.route('/') 
def home():
    return "<h1> This is the root page. </h1>"

#user landing route
@app.route('/user/<name>') 
def greet(name):
    return render_template('hello.html', name=name)

#login route
@app.route('/login', methods=["POST", "GET"]) 
def login():
    if request.method == "GET":
        return render_template('login.html')
    
    elif request.method == "POST":
        #fetch the entered fields
        username = request.form.get('username')
        password = request.form.get('password')
        
        #fetch from db
        user = User.query.filter_by(username = username).first()
        
        #check if user exists in fetched data
        if user:
            #check if password is correct
            if user.check_password(password):
                
                #render homepage
                first_name = user.first_name
                logger.info(f"\nUser login: Username: {username}\n")
                return render_template('dashboard.html', first_name = first_name)
            
            else:
                logger.info(f"\nInvalid login: User entered wrong password\nAttempted by: {username}\n")
                error = "Incorrect Password. Please try again."
                return render_template('login.html', error=error)
                
        else:
            logger.info(f"\nInvalid login: Username '{username}' does not exist.\n")
            error = "Username does not exist. Please try again."
            return render_template('login.html', error = error)
            
#register route
@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "GET":
        #load the registration page
        return render_template('register.html')
    
    elif request.method == "POST":
        # retrieve from form
        first_name = request.form.get('first_name','').strip()
        last_name = request.form.get('last_name','').strip()
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        contact_number = request.form.get('contact_number','').strip()

        # maintain user test reference log
        user_test_reference(username=username, password=password, debug=app.debug)

        # validation 1: empty fields
        if not first_name or not last_name or not username or not password:
            error = "Please do not leave any fields empty!"
            return render_template('register.html', error=error)

        # validation 2: contact number
        if len(contact_number)!=10 or not contact_number.isdigit() or contact_number[0]=="0":
            error = "Please enter a valid contact number."
            return render_template('register.html', error=error)

        # validation 3: username uniqueness
        username_exists = User.query.filter_by(username=username).first()
        if username_exists:
            error = "Username already exists. Please choose a unique username."
            return render_template("register.html", error=error)

        # ✅ ONLY NOW: Create and commit user
        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
            contact_number=contact_number
        )

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error = f"Something went wrong in saving your data :("
            logger.exception("Registration failed due to DB error.")
            return render_template('register.html', error=error)

        logger.info(f"New user registered: {username}")
        return render_template('registeration_success.html', first_name=first_name, last_name=last_name,username=username, contact_number=contact_number)
        
    
if __name__ == "__main__":
    logger.info("🚀 Flask app is starting...")
    app.run(debug=True)