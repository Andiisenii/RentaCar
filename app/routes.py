from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify, abort
from app.models import Car, Reservation, CarImage
from app import db
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
import os

main = Blueprint('main', __name__)

# Vendos gjuhën default në sesion
@main.before_app_request
def set_language():
    if 'lang' not in session:
        session['lang'] = 'sq'

# Ndërrimi i gjuhës
@main.route('/change_language/<lang_code>')
def change_language(lang_code):
    if lang_code in ['sq', 'mk', 'en']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('main.home'))

# Ballina
@main.route('/')
def home():
    cars = Car.query.options(joinedload(Car.images)).all()
    return render_template('main/home.html', cars=cars)

# Rreth Nesh
@main.route('/about')
def about():
    return render_template('main/about.html')

# Kontakti
@main.route('/contact')
def contact():
    return render_template('main/contact.html')


@main.route('/car/<int:car_id>', methods=['GET', 'POST'])
def car_detail(car_id):
    car = Car.query.get_or_404(car_id)

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_surname = request.form['customer_surname']
        customer_id_number = request.form['customer_id_number']
        customer_license_number = request.form['customer_license_number']
        customer_email = request.form['customer_email']
        customer_phone = request.form['customer_phone']
        date_range = request.form['date_range']  # Shembull: "2025-06-08 - 2025-06-10"

        try:
            start_str, end_str = [d.strip() for d in date_range.split('-')]
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except Exception:
            flash('Formati i datave është i pasaktë. Ju lutem zgjidhni datat sërish.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        if end_date < start_date:
            flash('Data e përfundimit duhet të jetë pas datës së fillimit.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        existing_reservations = Reservation.query.filter(
            Reservation.car_id == car_id,
            Reservation.end_date >= start_date,
            Reservation.start_date <= end_date
        ).all()

        if existing_reservations:
            flash('Këto data janë të zëna. Ju lutem provoni data të tjera.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        days = (end_date - start_date).days + 1
        total_price = days * car.price_per_day

        new_reservation = Reservation(
            car_id=car_id,
            customer_name=customer_name,
            customer_surname=customer_surname,
            customer_id_number=customer_id_number,
            customer_license_number=customer_license_number,
            customer_email=customer_email,
            customer_phone=customer_phone,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status='confirmed'
        )

        db.session.add(new_reservation)
        db.session.commit()

        flash(f'Rezervimi u bë me sukses! Totali: {total_price:.2f} EUR', 'success')
        return redirect(url_for('main.home'))

    # ✅ Merr të gjitha rezervimet ekzistuese për këtë veturë për t’i dërguar në template
    reservations = Reservation.query.filter_by(car_id=car_id).all()
    reserved_dates = [
        {
            'start': r.start_date.strftime('%Y-%m-%d'),
            'end': r.end_date.strftime('%Y-%m-%d')
        }
        for r in reservations
    ]

    # ✅ Dërgo edhe reserved_dates në template
    return render_template('main/car_detail.html', car=car, reserved_dates=reserved_dates)


# Fshij foto të makinës
@main.route('/delete_image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    if request.method != 'POST':
        abort(405)  # Method Not Allowed
    
    image = CarImage.query.get_or_404(image_id)
    car_id = image.car_id
    
    try:
        # Fshi foto nga sistemi i skedarëve
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, image.image_filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            current_app.logger.info(f'Fshihet foto: {file_path}')
        
        # Fshi nga databaza
        db.session.delete(image)
        db.session.commit()
        flash('Fotoja u fshi me sukses!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Gabim gjatë fshirjes: {str(e)}')
        flash('Gabim gjatë fshirjes së fotos', 'danger')
    
    return redirect(url_for('main.car_detail', car_id=car_id))
@main.route('/reserved_dates/<int:car_id>')
def reserved_dates(car_id):
    from app.models import Reservation
    from datetime import timedelta
    reserved = Reservation.query.filter_by(car_id=car_id).all()
    dates = []

    for res in reserved:
        start = res.start_date
        end = res.end_date
        delta = (end - start).days
        for i in range(delta + 1):
            dates.append((start + timedelta(days=i)).strftime('%Y-%m-%d'))

    return jsonify(dates)

# Shtoni këtë rrugë për të kontrolluar strukturën
@main.route('/check_db')
def check_db():
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    
    tables = inspector.get_table_names()
    car_columns = inspector.get_columns('car')
    car_image_columns = inspector.get_columns('car_image')
    
    return {
        'tables': tables,
        'car_columns': [c['name'] for c in car_columns],
        'car_image_columns': [c['name'] for c in car_image_columns]
    }