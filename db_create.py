from app import app, db
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation
from logging_config import logger

def create():
    with app.app_context():
        db.create_all()
        
        admin = User.query.filter_by(username="admin").first()
        
        if not admin:
            admin_user = User(
                first_name="Admin",
                last_name="User",
                username="admin",
                password="admin123",  
                contact_number="0000000000",
                role="admin"
            )
            
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Admin user created with username='admin' and password='admin123'")
            

        # ✅ Test Parking Lot
        if not ParkingLot.query.first():
            test_lot = ParkingLot(
                prime_location_name="IITM Main Gate",
                address="Main Gate Parking, IIT Madras, Chennai",
                pin_code="600036",
                price_per_hour=25.0,
                max_spots=50
            )
            db.session.add(test_lot)
            db.session.commit()
            logger.info("Test parking lot added.")

        # ✅ Test Parking Spot
        lot = ParkingLot.query.first()
        if lot and not ParkingSpot.query.first():
            test_spot = ParkingSpot(lot_id=lot.id)
            db.session.add(test_spot)
            db.session.commit()
            logger.info(f"Test parking spot added for lot ID {lot.id}")
        else:
            logger.info("Parking spot already exists or lot missing.")

        # ✅ Test User
        if not User.query.filter_by(username="test_user").first():
            test_user = User(
                first_name="Test",
                last_name="User",
                username="test_user",
                password="test1234",
                contact_number="9876543210"
            )
            db.session.add(test_user)
            db.session.commit()
            logger.info("Test user added.")
        else:
            logger.info("Test user already exists.")

        # ✅ Dummy Reservation
        user = User.query.filter_by(username="test_user").first()
        spot = ParkingSpot.query.first()

        if user and spot and not Reservation.query.filter_by(user_id=user.id, spot_id=spot.id).first():
            dummy_reservation = Reservation(
                user_id=user.id,
                spot_id=spot.id,
                vehicle_no="TN10AB1234"
                # parking_timestamp is auto-filled
            )
            db.session.add(dummy_reservation)
            db.session.commit()
            logger.info(f"Dummy reservation created for user {user.username} at spot ID {spot.id}")
        else:
            logger.info("Dummy reservation already exists or missing user/spot.")

def test():
    with app.app_context():
        username = 'test_user'
        first_name = db.session.query(User.first_name).filter_by(username=username).scalar()
        print(first_name)
        
create()
#test()