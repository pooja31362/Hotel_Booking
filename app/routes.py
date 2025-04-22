from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Hotel, Room, Booking, User
from . import db, mail

main = Blueprint('main', __name__)

@main.route('/')
def home():
    hotels = Hotel.query.all()
    cities = list(set([hotel.location for hotel in hotels]))
    return render_template('home.html', hotels=hotels, cities=cities)

@main.route('/suggest')
def suggest():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])
    hotels = Hotel.query.filter(
        Hotel.name.ilike(f'%{q}%') | Hotel.location.ilike(f'%{q}%') | Hotel.description.ilike(f'%{q}%')
    ).limit(10).all()
    suggestions = list(set(
        [hotel.name for hotel in hotels] + [hotel.location for hotel in hotels]
    ))
    return jsonify(suggestions)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if not user.is_verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('main.login'))
            login_user(user)
            return redirect(url_for('main.profile'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("Passwords don't match", 'danger')
            return render_template('signup.html')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists", 'danger')
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, phone=phone, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        token = new_user.get_verification_token(current_app.config['SECRET_KEY'])
        verification_link = url_for('main.verify_email', token=token, _external=True)

        msg = Message("Confirm your HotelEase Account",
                      sender="yourappemail@gmail.com",
                      recipients=[email])
        msg.body = f'''Hi {username},\n\nWelcome to HotelEase! Please click the link below to verify your account:\n\n{verification_link}\n\nThis link will expire in 1 hour.\n\nIf you didn’t sign up, ignore this email.'''
        mail.send(msg)

        flash("Signup successful! Please verify your email to log in.", "info")
        return redirect(url_for('main.login'))

    return render_template('signup.html')

@main.route('/verify/<token>')
def verify_email(token):
    email = User.verify_token(token, current_app.config['SECRET_KEY'])
    if email is None:
        flash("Verification link is invalid or expired.", "danger")
        return redirect(url_for('main.login'))
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_verified = True
        db.session.commit()
        flash("Your email has been verified! You can now log in.", "success")
    return redirect(url_for('main.login'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/profile')
@login_required
def profile():
    bookings = Booking.query.join(Room).join(Hotel).filter(Booking.user_name == current_user.username).all()
    hotels = Hotel.query.all()
    cities = list(set([hotel.location for hotel in hotels]))
    return render_template('profile.html', user=current_user, bookings=bookings, cities=cities)

@main.route('/generate_bill/<int:booking_id>')
@login_required
def generate_bill(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    room = Room.query.get(booking.room_id)
    hotel = Hotel.query.get(room.hotel_id)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"HotelEase Booking Invoice")
    p.drawString(100, 730, f"Name: {booking.user_name}")
    p.drawString(100, 710, f"Hotel: {hotel.name} ({hotel.location})")
    p.drawString(100, 690, f"Room: {room.room_type}")
    p.drawString(100, 670, f"Price: ₹{room.price:.2f}")
    p.drawString(100, 650, f"Check-In: {booking.check_in}")
    p.drawString(100, 630, f"Check-Out: {booking.check_out}")
    p.drawString(100, 610, f"Thank you for booking with HotelEase!")
    p.showPage()
    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"bill_booking_{booking_id}.pdf", mimetype='application/pdf')



@main.route('/hotels')
def hotel_list():
    city = request.args.get('city')
    if city:
        hotels = Hotel.query.filter_by(location=city).all()
    else:
        hotels = Hotel.query.all()
    return render_template('hotel_list.html', hotels=hotels)


@main.route('/hotel/<int:hotel_id>')
def hotel_detail(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    return render_template('hotel_detail.html', hotel=hotel)

@main.route('/book/<int:room_id>', methods=['POST'])
def book_room(room_id):
    name = request.form['name']
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    booking = Booking(user_name=name, room_id=room_id, check_in=check_in, check_out=check_out)
    db.session.add(booking)
    db.session.commit()
    return render_template('booking_confirmation.html', name=name)

