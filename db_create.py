from app import app,db
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot


with app.app_context():
    db.create_all() 
    
    #Test Lot
    if not ParkingLot.query.first():
        test_lot = ParkingLot(
            prime_location_name = "IITM Main Gate",
            address = "Main Gate Parking, IIT Madras, Chennai",
            pin_code = "600036",
            price_per_hour = 25.0,
            max_spots = 50
        ) 
        
        db.session.add(test_lot)
        db.session.commit()
        print(f"✅ Test parking lot added.")
    
    #Test Spot
    lot = ParkingLot.query.first()
    if lot:
        test_spot = ParkingSpot(lot_id=lot.id)
        db.session.add(test_spot)
        db.session.commit()
        print(f"✅ Test parking spot added for lot ID {lot.id}")
    else:
        print("⚠️ No ParkingLot found — skipping test spot creation.")