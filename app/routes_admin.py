import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session, flash
from werkzeug.utils import secure_filename
from app import db
from app.models import Car, CarImage, Reservation
from app.models import ReservationHistory
admin = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin.route('/')
def dashboard():
    cars = Car.query.all()
    reservations = Reservation.query.all()
    return render_template('admin/dashboard.html', cars=cars, reservations=reservations)
@admin.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        # Merr brand dhe model dhe krijo emrin e plotë
        brand = request.form.get('brand', '').strip()
        model = request.form.get('model', '').strip()

        if not brand or not model:
            flash('Brendi dhe modeli janë të detyrueshëm.', 'danger')
            return redirect(url_for('admin.add_car'))

        name = f"{brand} {model}"

        # Përshkrimi
        description = request.form.get('description')

        # Çmimi për ditë
        try:
            price_per_day = float(request.form.get('price_per_day'))
        except (ValueError, TypeError):
            flash('Çmimi për ditë duhet të jetë numër valid.', 'danger')
            return redirect(url_for('admin.add_car'))

        # Opsionale ose me default
        try:
            fuel_level = float(request.form.get('fuel_level', 100.0))
        except (ValueError, TypeError):
            fuel_level = 100.0

        try:
            km_driven = float(request.form.get('km_driven', 0))
        except (ValueError, TypeError):
            km_driven = 0

        fuel_type = request.form.get('fuel_type')
        kilometers = request.form.get('kilometers')
        green_card_valid = request.form.get('green_card_valid') == 'true'
        production_year = request.form.get('production_year')

        # Krijo objektin Car
        car = Car(
        brand=brand,  # Përdor brand në vend të name
        model=model,  # Shto model sepse është i nevojshëm
        description=description,
        price_per_day=price_per_day,
        fuel_level=fuel_level,
        km_driven=km_driven,
        fuel_type=fuel_type,
        green_card_valid=green_card_valid,  # Ndrysho nga green_card_year në green_card_valid
        production_year=production_year
        )

        db.session.add(car)
        db.session.commit()  # për të pasur car.id

        # Ngarko imazhet nëse ekzistojnë
        if 'images' in request.files:
            images = request.files.getlist('images')
            upload_folder = os.path.join(current_app.root_path, 'static/uploads')
            os.makedirs(upload_folder, exist_ok=True)

            for img in images:
                if img and allowed_file(img.filename):
                    filename = secure_filename(img.filename)
                    img.save(os.path.join(upload_folder, filename))

                    new_image = CarImage(car_id=car.id, image_filename=filename)
                    db.session.add(new_image)
            db.session.commit()

        flash('Makina u shtua me sukses!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/add_car.html')


@admin.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        try:
            # Përditëso të dhënat bazë të makinës
            car.brand = request.form.get('brand', car.brand)
            car.model = request.form.get('model', car.model)
            car.description = request.form.get('description', car.description)
            car.price_per_day = float(request.form.get('price_per_day', car.price_per_day))
            car.fuel_type = request.form.get('fuel_type', car.fuel_type)
            car.km_driven = float(request.form.get('km_driven', car.km_driven))
            
            # Trajto green_card_valid si boolean
            green_card_valid = request.form.get('green_card_valid')
            car.green_card_valid = green_card_valid.lower() == 'true' if green_card_valid else car.green_card_valid
            
            car.production_year = int(request.form.get('production_year', car.production_year))
            
            # Përditëso fuel_level nëse është dhënë
            fuel_level = request.form.get('fuel_level')
            if fuel_level is not None:
                car.fuel_level = float(fuel_level)
            
            db.session.commit()
            flash('Makina u përditësua me sukses!', 'success')
            return redirect(url_for('main.car_detail', car_id=car.id))
        
        except (ValueError, KeyError) as e:
            db.session.rollback()
            flash(f'Gabim gjatë përditësimit: {str(e)}', 'danger')
        # Fshi fotot e selektuara
        if 'delete_images' in request.form:
            images_to_delete = request.form.getlist('delete_images')
            for image_id in images_to_delete:
                image = CarImage.query.get(image_id)
                if image:
                    try:
                        # Fshi fotot nga sistemi i skedarëve
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image.image_filename)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        # Fshi rekordin nga databaza
                        db.session.delete(image)
                    except Exception as e:
                        current_app.logger.error(f'Gabim gjatë fshirjes së fotos: {e}')
                        continue

        # Upload new images
        if 'images' in request.files:
            images = request.files.getlist('images')
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)

            for img in images:
                if img and allowed_file(img.filename):
                    filename = secure_filename(img.filename)
                    img.save(os.path.join(upload_folder, filename))
                    new_image = CarImage(car_id=car.id, image_filename=filename)
                    db.session.add(new_image)

        db.session.commit()
        flash('Makina u përditësua me sukses!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_car.html', car=car)

@admin.route('/delete_car/<int:car_id>')
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    flash('Makina u fshi me sukses!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/reservations')
def view_reservations():
    reservations = Reservation.query.all()
    return render_template('admin/reservations.html', reservations=reservations)

@admin.route('/reservations/manual/add', methods=['GET', 'POST'])
def add_manual_reservation():
    cars = Car.query.all()

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_surname = request.form['customer_surname']
        customer_id_number = request.form['customer_id_number']
        customer_license_number = request.form['customer_license_number']
        customer_email = request.form['customer_email']
        customer_phone = request.form['customer_phone']
        car_id = request.form['car_id']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        total_price = float(request.form['total_price'])

        new_reservation = Reservation(
            customer_name=customer_name,
            customer_surname=customer_surname,
            customer_id_number=customer_id_number,
            customer_license_number=customer_license_number,
            customer_email=customer_email,
            customer_phone=customer_phone,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            car_id=car_id,
            status='manual'
        )
        db.session.add(new_reservation)
        db.session.commit()
        flash('Rezervimi manual u shtua me sukses.', 'success')
        return redirect(url_for('admin.view_reservations'))

    return render_template('admin/add_manual_reservation.html', cars=cars)

@admin.route('/delete_reservation/<int:reservation_id>')
def delete_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    db.session.delete(reservation)
    db.session.commit()
    flash('Rezervimi u fshi me sukses!', 'success')
    return redirect(url_for('admin.view_reservations'))

@admin.route('/edit_reservation/<int:reservation_id>', methods=['GET', 'POST'])
def edit_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if request.method == 'POST':
        reservation.customer_name = request.form['customer_name']
        reservation.customer_email = request.form['customer_email']
        reservation.customer_phone = request.form['customer_phone']
        reservation.status = request.form.get('status', reservation.status)

        try:
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        except ValueError:
            flash('Format i datave është i gabuar.', 'danger')
            return redirect(url_for('admin.edit_reservation', reservation_id=reservation_id))

        if end_date < start_date:
            flash('Data e mbarimit duhet të jetë më e madhe ose e barabartë me datën e fillimit.', 'danger')
            return redirect(url_for('admin.edit_reservation', reservation_id=reservation_id))

        reservation.start_date = start_date
        reservation.end_date = end_date

        days = (end_date - start_date).days + 1
        reservation.total_price = days * reservation.car.price_per_day

        db.session.commit()
        flash('Rezervimi u përditësua me sukses.', 'success')
        return redirect(url_for('admin.view_reservations'))

    return render_template('admin/edit_reservation.html', reservation=reservation)
@admin.route('/print_reservation/<int:reservation_id>')
def print_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    contract_data = {
        'pickup_date': '05.06.2025 10:00',
        'return_date': '10.06.2025 18:00',
        'customer_name': 'Filan Fisteku',
        'customer_id': '1234567890123',
        'license_number': 'MK123456',
        'company_representative': 'Agon Agoni',
        'car_brand': 'Toyota',
        'car_model': 'Corolla',
        'license_plate': 'MK-AB-123',
        'chassis_number': 'JT2BF22K6W0123456'
    }
    return render_template('admin/print_reservation.html', reservation=reservation)

admin.route('/admin/car/<int:car_id>/image/<int:image_id>/delete', methods=['POST'])
def delete_car_image(car_id, image_id):
    image = CarImage.query.get_or_404(image_id)
    
    # Fshi foton nga sistemi i skedarëve
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image.image_filename))
    except Exception as e:
        flash('Gabim gjatë fshirjes së fotos', 'error')
    
    # Fshi rekordin nga DB
    db.session.delete(image)
    db.session.commit()
    
    flash('Fotoja u fshi me sukses', 'success')
    return redirect(url_for('admin.edit_car', car_id=car_id))

@admin.route('/admin/history')
def view_reservation_history():
    history_entries = ReservationHistory.query.order_by(ReservationHistory.action_date.desc()).all()
    return render_template('admin/history.html', history_entries=history_entries)


# Login për admin
@admin.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Këtu vendos kredencialet manualisht
        if username == 'Aagon' and password == '0101Agon.?':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.view_reservations'))
        else:
            return render_template('admin/login.html', error='Username ose fjalëkalim i pasaktë.')
    return render_template('admin/login.html')


# Logout
@admin.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))

@admin.before_request
def require_login():
    # Mos e kërko login-in për /admin/login
    if request.endpoint and request.endpoint.startswith('admin.') and \
       request.endpoint not in ['admin.admin_login']:
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.admin_login'))