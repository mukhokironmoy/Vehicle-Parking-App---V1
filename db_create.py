from app import app, db
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation

with app.app_context():
    db.create_all()

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
        print("✅ Test parking lot added.")

    # ✅ Test Parking Spot
    lot = ParkingLot.query.first()
    if lot and not ParkingSpot.query.first():
        test_spot = ParkingSpot(lot_id=lot.id)
        db.session.add(test_spot)
        db.session.commit()
        print(f"✅ Test parking spot added for lot ID {lot.id}")
    else:
        print("⚠️ Parking spot already exists or lot missing.")

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
        print("✅ Test user added.")
    else:
        print("⚠️ Test user already exists.")

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
        print(f"✅ Dummy reservation created for user {user.username} at spot ID {spot.id}")
    else:
        print("⚠️ Dummy reservation already exists or missing user/spot.")
