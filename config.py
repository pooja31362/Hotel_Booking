import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:Muthupattan1403@hoteldb.cf6me2usaddu.ap-south-1.rds.amazonaws.com/hotel_booking'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"