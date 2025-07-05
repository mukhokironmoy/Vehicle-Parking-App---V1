from flask import Flask, url_for, render_template, request, redirect, abort
from extensions import db
from logging_config import logger, user_test_reference
from flask_login import login_user, login_required, current_user, logout_user
import os
from dotenv import load_dotenv

load_dotenv()

#app config
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#db instance
db.init_app(app)

#importing models
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot

#importing login manager
from extensions import login_manager
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

'''----------------------------------------------------------------------------------------------------------------------------------------------'''
#root 
@app.route('/') 
def home():
    return "<h1> This is the root page. </h1>"

'''----------------------------------------------------------------------------------------------------------------------------------------------'''
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
                login_user(user)
                
                #render dashboard
                if user.role == "admin":
                    logger.info(f"\nAdmin login")
                    return redirect(url_for('admin_dashboard'))
                else:                
                    logger.info(f"\nUser login: \nUsername- {username}\n")
                    return redirect(url_for('user_dashboard',username=current_user.username))
            
            else:
                logger.info(f"\nInvalid login: User entered wrong password\nAttempted by: {username}\n")
                error = "Incorrect Username or Password. Please try again."
                return render_template('login.html', error=error)
                
        else:
            logger.info(f"\nInvalid login: Username '{username}' does not exist.\n")
            error = "Incorrect Username or Password. Please try again."
            return render_template('login.html', error=error)

'''----------------------------------------------------------------------------------------------------------------------------------------------'''
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

        #Create and commit user
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

'''----------------------------------------------------------------------------------------------------------------------------------------------'''
#admin dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    #check access
    if current_user.role != "admin":
        logger.warning(f"\nILLEGAL ROUTE ACCESS : {current_user.username} tried to access admin dashboard.\n")
        return redirect(url_for('user_dashboard',username=current_user.username))
        
    
    return render_template('admin_dashboard.html')

'''----------------------------------------------------------------------------------------------------------------------------------------------'''
#admin/parking lot route
@app.route('/admin/parking-lots')
@login_required
def admin_parking_lots():
    #check access
    if current_user.role != "admin":
        logger.warning(f"\nILLEGAL ROUTE ACCESS : {current_user.username} tried to access admin/parking-lots.\n")
        return redirect(url_for('user_dashboard',username=current_user.username))

    #query lot data
    lots = ParkingLot.query.all()
    
    lot_data = []

    for lot in lots:
        #calculate available and occupied spots for each lot
        available_spots = sum(1 for spot in lot.spots if spot.status == "A")
        occupied_spots = sum(1 for spot in lot.spots if spot.status == "O")
        
        #append data
        lot_data.append(
            {"lot":lot,
            "available": available_spots,
            "occupied": occupied_spots} 
            )
           
    return render_template("admin_parking_lots.html", lot_data=lot_data)

'''----------------------------------------------------------------------------------------------------------------------------------------------'''
#create parking lot
@app.route('/admin/parking-lots/create', methods=["GET", "POST"])
@login_required
def create_parking_lot():
    #check access
    if current_user.role != "admin":
        logger.warning(f"\nILLEGAL ROUTE ACCESS : {current_user.username} tried to access admin/parking-lots.\n")
        return redirect(url_for('user_dashboard',username=current_user.username))

    if request.method == "GET":
        return render_template('create_parking_lot.html')
    
    elif request.method == "POST":
        prime_location_name = request.form.get("prime_location_name", "").strip()
        address = request.form.get("address", "").strip()
        pin_code = request.form.get("pin_code", "").strip()
        price_per_hour = request.form.get("price_per_hour", "").strip()
        max_spots = request.form.get("max_spots", "").strip()
        
        #initialise empty error message
        errors  = []
        
        #validation 1 : check if any fields empty
        if not all([prime_location_name, address, pin_code, price_per_hour, max_spots]):
            errors.append("Please fill in all fields.")
        
        #validation 2 : pin code validity
        if not pin_code.isdigit() or len(pin_code) != 6:
            errors.append("Pin code must be exactly 6 digits.\n")
        
        #validation 3 : price per hour validity
        try: 
            price_per_hour = float(price_per_hour)
            if price_per_hour <= 0:
                raise ValueError
        except ValueError:
            errors.append("Price per hour must be a non zero positive number.\n")
        
        #validation 4 : max spots validity
        try: 
            max_spots = int(max_spots)
            if max_spots <= 0:
                raise ValueError
        except ValueError:
            errors.append("Max Spots must be a non zero positive number.\n")
            
        if errors:
            return render_template("create_parking_lot.html", error="<br>".join(errors))

        
        #create parking lot instance
        new_lot = ParkingLot(
            prime_location_name = prime_location_name,
            address = address,
            pin_code = pin_code,
            price_per_hour = price_per_hour,
            max_spots = max_spots
        )
        
        #add lot to database
        try:
            db.session.add(new_lot)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error = f"Something went wrong in saving your data :(\n"
            logger.exception("Failed to create parking lot due to DB error.")
            return render_template('create_parking_lot.html', error=error)
        
        #auto create spots for new lot
        spots=[]
        for i in range(max_spots):
            new_spot =  ParkingSpot(
                lot_id = new_lot.id,
                status = "A"
            )
            
            spots.append(new_spot)
            
        #add spots to database
        try:
            db.session.add_all(spots)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error = f"Something went wrong in saving your data :(\n"
            logger.exception("Failed to create parking spots for this lot due to DB error.")
            return render_template('create_parking_lot.html', error=error)
        

        logger.info(f"New parking lot created: Lot id = {new_lot.id} Location = {prime_location_name} Total Spots = {max_spots}")
        return render_template('create_parking_lot_success.html', id=new_lot.id, prime_location_name=prime_location_name, address=address, pin_code=pin_code, price_per_hour=price_per_hour, max_spots=max_spots)

'''----------------------------------------------------------------------------------------------------------------------------------------------'''
#edit parking lot
@app.route('/admin/parking-lots/edit/<int:lot_id>', methods=["GET", "POST"])
@login_required
def edit_parking_lot(lot_id):
    # Check access
    if current_user.role != "admin":
        logger.warning(f"\nILLEGAL ROUTE ACCESS: {current_user.username} tried to access edit parking lot page.\n")
        return redirect(url_for('user_dashboard', username=current_user.username))
 
    #Query the lot
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        logger.warning(f"\nParking lot with lot id = {lot_id} was not found.\n")
        abort(404, description=f"Parking lot with lot id = {lot_id} was not found")
        
    if request.method == "GET":
        #render edit page with prefilled data
        return render_template('edit_parking_lot.html', lot=lot)
    
    elif request.method == "POST":
        prime_location_name = request.form.get("prime_location_name", "").strip()
        address = request.form.get("address", "").strip()
        pin_code = request.form.get("pin_code", "").strip()
        price_per_hour = request.form.get("price_per_hour", "").strip()
        max_spots = request.form.get("max_spots", "").strip()
        
        #initialise empty error message
        errors  = []
        
        #validation 1 : check if any fields empty
        if not all([prime_location_name, address, pin_code, price_per_hour, max_spots]):
            errors.append("Please fill in all fields.")
        
        #validation 2 : pin code validity
        if not pin_code.isdigit() or len(pin_code) != 6:
            errors.append("Pin code must be exactly 6 digits.\n")
        
        #validation 3 : price per hour validity
        try: 
            price_per_hour = float(price_per_hour)
            if price_per_hour <= 0:
                raise ValueError
        except ValueError:
            errors.append("Price per hour must be a non zero positive number.\n")
        
        #validation 4 : max spots validity
        try: 
            max_spots = int(max_spots)
            if max_spots <= 0:
                raise ValueError
        except ValueError:
            errors.append("Max Spots must be a non zero positive number.\n")
            
        if errors:
            return render_template("edit_parking_lot.html", lot=lot, error="<br>".join(errors))
        
        
        #update fields with new values
        lot.prime_location_name = prime_location_name
        lot.address = address
        lot.pin_code = pin_code
        lot.price_per_hour = price_per_hour
        lot.max_spots = max_spots
        
        #commit to database
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.exception("Failed to update parking lot due to DB error.")
            error = "Something went wrong saving your changes. Please try again."
            return render_template("edit_parking_lot.html", lot=lot, error=error)

        #return updated data
        logger.info(f"Parking lot updated: ID {lot.id}")
        return redirect(url_for("admin_parking_lots"))

'''----------------------------------------------------------------------------------------------------------------------------------------------'''
#delete parking lot
@app.route('/admin/parking-lots/delete/<int:lot_id>', methods=["POST"])
def delete_parking_lot(lot_id):
    # Check access
    if current_user.role != "admin":
        logger.warning(f"\nILLEGAL ROUTE ACCESS: {current_user.username} tried to DELETE parking lot.\n")
        return redirect(url_for('user_dashboard', username=current_user.username))
    
    # Fetch the parking lot
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        logger.warning(f"\nParking lot with id={lot_id} not found for deletion.\n")
        abort(404, description=f"Parking lot with ID {lot_id} not found.")
 
    try:
        #delete all spots related to this lot
        for spot in lot.spots:
            db.session.delete(spot)
        
        #delete the lot itself
        db.session.delete(lot)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.exception("Error while deleting parking lot and spots.")
        error = "Something went wrong while deleting the parking lot."
        # Optionally, redirect back with error (or flash)
        return redirect(url_for("admin_parking_lots"))
    
    logger.info(f"Parking lot ID {lot_id} and all spots deleted by {current_user.username}.")
    return redirect(url_for("admin_parking_lots"))
'''----------------------------------------------------------------------------------------------------------------------------------------------'''
#user dashboard
@app.route('/<username>/dashboard')
@login_required
def user_dashboard(username):
    if username != current_user.username:
        logger.warning(f"\nILLEGAL ROUTE ACCESS : {username} tried to access {current_user.username} dashboard.\n")
        if current_user.role == "admin":
            return redirect(url_for(f'admin_dashboard'))            
        return redirect(url_for('user_dashboard',username=current_user.username))

        
    return render_template('user_dashboard.html', first_name=current_user.first_name)

'''----------------------------------------------------------------------------------------------------------------------------------------------'''
#logout route
@app.route('/logout')
@login_required
def logout():
    logger.info(f"User logout: \nUsername- {current_user.username}")
    logout_user()
    return redirect(url_for('login'))


@app.after_request
def add_cache_control_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

         
'''----------------------------------------------------------------------------------------------------------------------------------------------'''
#main function   
if __name__ == "__main__":
    logger.info("🚀 Flask app is starting...")
    app.run(debug=True)