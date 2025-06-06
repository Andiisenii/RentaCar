import app
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Car, Reservation
from app import db
from datetime import datetime
app.config['SQLALCHEMY_ECHO'] = True  # Shfaq query-t SQL në konsol
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Reload automatik i template-ve

public = Blueprint('main', __name__)

@public.route('/')
def home():
    cars = Car.query.all()
    return render_template('public/home.html', cars=cars)

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

        # Optional: meqenëse nuk do numër letërnjoftimi dhe leje, i lëmë bosh ose hiqni këto nga modeli

        # Kontroll datat në format datetime.date
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

        # Nëse nuk dëshiron të kërkosh nr. letërnjoftimi dhe leje drejtimi,
        # duhet t'i hiqësh nga modeli ose i vendos me vlerë bosh ''
        new_reservation = Reservation(
            car_id=car_id,
            customer_name=customer_name,
            customer_surname=customer_surname,
            customer_id_number='',         # bosh, ose vendos valid default
            customer_license_number='',    # bosh, ose vendos valid default
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
        return redirect(url_for('public.home'))

    return render_template('public/car_detail.html', car=car)
