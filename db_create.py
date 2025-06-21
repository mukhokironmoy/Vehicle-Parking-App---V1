from app import app,db
from models.user import User
from models.parking_lot import ParkingLot

with app.app_context():
    db.create_all() 