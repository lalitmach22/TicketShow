from .database import db
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, IMAGES
from werkzeug.datastructures import FileStorage
from sqlalchemy import CheckConstraint

images = UploadSet('images', IMAGES)

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String(10),default='user')
    is_admin = db.Column(db.Integer, default=0)
    approved = db.Column(db.Integer, default=0)
    __table_args__ = (
        CheckConstraint("length(password) >= 6 and password like '%\\$%'", name="password_constraint"),
    )
    

    def check_password(self, password):
        return self.password == password

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    place = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, 
                          info={'check_constraint': 'capacity >= 0 and capacity <= 100000'})


    shows = db.relationship('Show', backref='venue', lazy=True)

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False, info={'check_constraint':'rating >= 0 and rating <= 10'})
    tags = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(255))
    ticket_price = db.Column(db.Integer, nullable=False, info={'check_constraint':'ticket_price >= 0 and ticket_price <= 100000'})
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    bookings = db.relationship('Booking', backref='show', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))

def create_models(db):
    db.create_all()
    return User, Venue, Show, Booking


