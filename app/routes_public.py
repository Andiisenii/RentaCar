import app
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Car, Reservation
from app import db
from datetime import datetime


public = Blueprint('main', __name__)

@public.route('/')
def home():
    cars = Car.query.all()
    return render_template('public/home.html', cars=cars)
import re
from flask import flash, redirect, url_for, request, render_template
from datetime import datetime
from yourapp.models import Car, Reservation
from yourapp import db

@public.route('/car/<int:car_id>', methods=['GET', 'POST'])
def car_detail(car_id):
    car = Car.query.get_or_404(car_id)

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_surname = request.form['customer_surname']
        customer_email = request.form['customer_email']
        customer_phone = request.form['customer_phone']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']

        # Kontroll bazik për email me regex të thjeshtë
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, customer_email):
            flash('Email-i nuk është në format të saktë.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        # Kontroll bazik për telefon (numra dhe +, -, hapësira)
        phone_pattern = r'^[\d\s\+\-\(\)]+$'
        if not re.match(phone_pattern, customer_phone):
            flash('Numri i telefonit është i pasaktë.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        # Kontrollo nëse datat janë të dhëna dhe në formatin e saktë
        if not start_date_str or not end_date_str:
            flash('Ju lutem zgjidhni datat e fillimit dhe përfundimit.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash('Format datash është i gabuar.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        if end_date < start_date:
            flash('Data e përfundimit duhet të jetë pas datës së fillimit.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        # Kontrollo nëse datat janë të lira
        existing_reservations = Reservation.query.filter(
            Reservation.car_id == car_id,
            Reservation.end_date >= start_date,
            Reservation.start_date <= end_date
        ).all()

        if existing_reservations:
            flash('Datat e rezervuara janë zënë. Ju lutem zgjidhni data të tjera.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        # Llogarit çmimin
        days = (end_date - start_date).days + 1
        total_price = days * car.price_per_day

        new_reservation = Reservation(
            car_id=car_id,
            customer_name=customer_name,
            customer_surname=customer_surname,
            customer_id_number='',         # bosh, nëse nuk përdoret
            customer_license_number='',    # bosh, nëse nuk përdoret
            customer_email=customer_email,
            customer_phone=customer_phone,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status='confirmed'
        )

        db.session.add(new_reservation)
        db.session.commit()

        flash(f'Rezervimi u bë me sukses! Totali: {total_price} EUR', 'success')
        return redirect(url_for('main.home'))

    return render_template('public/car_detail.html', car=car)
