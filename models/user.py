from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .reservation import Reservation



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(100), nullable = False)
    last_name = db.Column(db.String(100), nullable = False)
    username = db.Column(db.String(100), unique = True, nullable = False)
    _password = db.Column("password", db.String(200), nullable = False)
    contact_number = db.Column(db.String(20))
    role = db.Column(db.String(10), nullable=False, default="user")
    
    reservations = db.relationship("Reservation", backref="user", lazy="dynamic")
    
    @property
    def password(self):
        raise AttributeError("Password is write-only.")
    
    @password.setter
    def password(self, plain_password):
        from werkzeug.security import generate_password_hash
        self._password = generate_password_hash(plain_password)
        
    def check_password(self, password_input):
        from werkzeug.security import check_password_hash
        return check_password_hash(self._password, password_input)