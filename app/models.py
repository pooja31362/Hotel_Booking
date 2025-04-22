from . import db
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer

class Hotel(db.Model):
    __tablename__ = 'Hotel'  # Explicit table name match
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    rooms = db.relationship('Room', backref='hotel', lazy=True)

class Room(db.Model):
    __tablename__ = 'Room'  # Match case with your DB
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('Hotel.id'), nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)

class Booking(db.Model):
    __tablename__ = 'Booking'  # Optional but good for consistency
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('Room.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    # 🪄 Email Verification Token Generator
    def get_verification_token(self, secret_key, expires_sec=3600):
        s = URLSafeTimedSerializer(secret_key)
        return s.dumps(self.email, salt='email-confirm')

    @staticmethod
    def verify_token(token, secret_key, max_age=3600):
        s = URLSafeTimedSerializer(secret_key)
        try:
            email = s.loads(token, salt='email-confirm', max_age=max_age)
        except Exception:
            return None
        return email