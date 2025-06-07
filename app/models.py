from app import db
from datetime import datetime

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=True)
    price_per_day = db.Column(db.Float, nullable=False)
    fuel_level = db.Column(db.Float, nullable=False, default=100.0)
    km_driven = db.Column(db.Float, nullable=True, default=0.0)
    green_card_valid = db.Column(db.Boolean, default=True)  # Changed to boolean
    fuel_type = db.Column(db.String(50), nullable=False) 
    production_year = db.Column(db.Integer)
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100), nullable=False)
    reservations = db.relationship('Reservation', backref='car', lazy=True)
    transmission = db.Column(db.String(20))  
    seats = db.Column(db.Integer)         
    
    # Relationships
    reservations = db.relationship('Reservation', backref='car', lazy=True)
    images = db.relationship('CarImage', back_populates='car', cascade='all, delete-orphan')

class CarImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)

    car = db.relationship('Car', back_populates='images')

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_surname = db.Column(db.String(100), nullable=False)
    customer_id_number = db.Column(db.String(15), nullable=False)
    customer_license_number = db.Column(db.String(50), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReservationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id', name='fk_reservationhistory_car_id'), nullable=False)

    customer_name = db.Column(db.String(100))
    action = db.Column(db.String(20))  # 'reserved' ose 'deleted'
    action_date = db.Column(db.DateTime, default=datetime.utcnow)

    car = db.relationship('Car', backref=db.backref('history_entries', lazy=True))