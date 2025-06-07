from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
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

# Detajet e makinës dhe rezervimi
@main.route('/car/<int:car_id>', methods=['GET', 'POST'])
def car_detail(car_id):
    car = Car.query.options(joinedload(Car.images)).get_or_404(car_id)

    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        customer_surname = request.form.get('customer_surname', '').strip()
        customer_id_number = request.form.get('customer_id_number', '').strip()
        customer_license_number = request.form.get('customer_license_number', '').strip()
        customer_email = request.form.get('customer_email', '').strip()
        customer_phone = request.form.get('customer_phone', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()

        # Validimi i të dhënave
        if not all([customer_name, customer_surname, customer_id_number, customer_license_number, 
                   customer_email, customer_phone, start_date_str, end_date_str]):
            flash('Ju lutem plotësoni të gjitha fushat e kërkuara.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            if start_date > end_date:
                flash('Data e fillimit duhet të jetë para datës së mbarimit.', 'danger')
                return redirect(url_for('main.car_detail', car_id=car_id))

            if start_date < datetime.today().date():
                flash('Data e fillimit nuk mund të jetë në të kaluarën.', 'danger')
                return redirect(url_for('main.car_detail', car_id=car_id))
        except ValueError:
            flash('Format i gabuar i datës. Ju lutem përdorni YYYY-MM-DD.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        # Kontrolli për konflikt në rezervime
        conflicts = Reservation.query.filter(
            Reservation.car_id == car_id,
            Reservation.end_date >= start_date,
            Reservation.start_date <= end_date,
            Reservation.status != 'cancelled'  # Mos merr parasysh rezervimet e anuluara
        ).all()

        if conflicts:
            flash('Makina është e rezervuar në këtë periudhë.', 'danger')
            return redirect(url_for('main.car_detail', car_id=car_id))

        # Llogaritja e totalit të çmimit
        days = (end_date - start_date).days + 1
        total_price = days * car.price_per_day

        # Krijimi i rezervimit
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
            status='confirmed'  # Shto statusin e rezervimit
        )
        db.session.add(new_reservation)
        db.session.commit()

        flash(f'Rezervimi u krye me sukses! Totali: {total_price:.2f} € për {days} ditë.', 'success')
        return redirect(url_for('main.home'))

    # Merr rezervimet ekzistuese për të shfaqur datat e zëna
    reservations = Reservation.query.filter(
        Reservation.car_id == car_id,
        Reservation.status != 'cancelled'
    ).all()
    
    reserved_dates = []
    for r in reservations:
        current = r.start_date
        while current <= r.end_date:
            reserved_dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)

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