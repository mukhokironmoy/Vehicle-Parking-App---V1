from extensions import db
from .parking_spot import ParkingSpot

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(300), nullable = False)
    pin_code = db.Column(db.String(10), nullable = False)
    price_per_hour = db.Column(db.Float, nullable = False)
    max_spots = db.Column(db.Integer, nullable = False)
    
    spots = db.relationship(ParkingSpot, backref="lot", lazy=True)