import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:Muthupattan1403@hoteldb.cf6me2usaddu.ap-south-1.rds.amazonaws.com/hotel_booking'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "mycutesecretkey123"
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'yourappemail@gmail.com'
    MAIL_PASSWORD = 'yourapppassword'
