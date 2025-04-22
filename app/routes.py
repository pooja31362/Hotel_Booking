from flask import Blueprint, render_template, request, redirect, url_for
from .models import Hotel, Room, Booking
from . import db
from flask import jsonify

main = Blueprint('main', __name__)


@main.route('/')
def home():
    hotels = Hotel.query.all()
    cities = list(set([hotel.location for hotel in hotels]))  # Unique city list
    return render_template('home.html', hotels=hotels, cities=cities)


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

@main.route('/suggest')
def suggest():
    q = request.args.get('q', '')
    if not q:
        return jsonify([])

    hotels = Hotel.query.filter(
        Hotel.name.ilike(f'%{q}%') | Hotel.location.ilike(f'%{q}%') | Hotel.description.ilike(f'%{q}%')
    ).limit(10).all()

    suggestions = list(set(
        [hotel.name for hotel in hotels] +
        [hotel.location for hotel in hotels]
    ))

    return jsonify(suggestions)

@main.route('/book/<int:room_id>', methods=['POST'])
def book_room(room_id):
    name = request.form['name']
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    booking = Booking(user_name=name, room_id=room_id, check_in=check_in, check_out=check_out)
    db.session.add(booking)
    db.session.commit()
    return render_template('booking_confirmation.html', name=name)

