import os
import sys
from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash, abort
from flask import current_app as app
from application.models import Venue, Show, Booking
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#from app import app, db
import flask_login
from application.database import db
from flask_uploads import UploadSet, IMAGES
from flask_login import login_user, logout_user, current_user, login_required
from application.forms import VenueForm, ShowForm, BookingForm
#from flask_uploads import secure_filename
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps


images = UploadSet('images', IMAGES)

# Create a blueprint for the routes
routes = Blueprint('routes', __name__)

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        current_user = flask_login.current_user
        if not current_user.is_authenticated or current_user.is_admin != 1:
            return abort(403)
        return func(*args, **kwargs)
    return decorated_view

def user_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        current_user = flask_login.current_user
        if not current_user.is_authenticated or current_user.is_admin == 1:
            return abort(403)
        return func(*args, **kwargs)
    return decorated_view

@routes.route('/')
def home():
    return render_template("home.html", now=datetime.now())

# Route for the index page
@routes.route('/index')
def index():
    return render_template('index.html',now=datetime.now())

# Route for displaying all venues
@routes.route('/venues')
def venues():
    venues = Venue.query.all()
    return render_template('venue.html', venues=venues,now=datetime.now())
# Route for admin dashboard to create,edit, delete venues/shows

@routes.route('/admin_dashboard', methods = ['GET', 'POST'])
@admin_required
def admin_dashboard():
    venues = Venue.query.all()
    shows = Show.query.all()

    return render_template('admin_dashboard.html', venues=venues, shows=shows, now =datetime.now())

@routes.route('/user_dashboard', methods = ['GET', 'POST'])
@user_required
def user_dashboard():
    venues = Venue.query.all()
    shows = Show.query.all()

    return render_template('user_dashboard.html', venues=venues, shows=shows, now =datetime.now())

# Route for creating a new venue
@routes.route('/create_venue', methods=['GET', 'POST'])
@admin_required
def create_venue():
    form = VenueForm()
    if form.validate_on_submit():
        venue = Venue(name=form.name.data, place=form.place.data, capacity=form.capacity.data)
        db.session.add(venue)
        db.session.commit()
        flash('Venue created successfully!', 'success')
        return redirect(url_for('routes.admin_dashboard'))
    return render_template('create_venue.html', form=form,now=datetime.now())

# Route for editing a venue
@routes.route('/venue/edit/<int:id>', methods=['GET', 'POST'])
@admin_required

def edit_venue(id):
    venue = Venue.query.get(id)
    if request.method == 'POST':
        venue.name = request.form['name']
        venue.place = request.form['place']
        venue.capacity = request.form['capacity']
        db.session.commit()
        flash('Venue updated successfully!')
        return redirect(url_for('routes.venues'))
    return render_template('edit_venue.html', venue=venue,now=datetime.now())

# Route for deleting a venue
@routes.route('/venue/delete/<int:id>', methods=['GET', 'POST'])
@admin_required

def delete_venue(id):
    venue = Venue.query.get(id)
    if request.method == 'POST':
        db.session.delete(venue)
        db.session.commit()
        flash('Venue deleted successfully!')
        return redirect(url_for('routes.venues'))
    return render_template('delete_venue.html', venue=venue,now=datetime.now())

# Route for displaying all shows
@routes.route('/shows')
def shows():
    shows = Show.query.all()
     # create a list to store  show details with venue names
    show_details = []
    
    for show in shows:
        
        venue = Venue.query.get(show.venue_id)
                
        show_detail = {
            'id' : show.id,
            'Name': show.name,
            'Rating' : show.rating,
            'Tag' : show.tags,
            'ticket_Price': show.ticket_price,
            'venue_name': venue}
        show_details.append(show_detail)   
    return render_template('shows.html', show_details=show_details,now=datetime.now())


# Route for creating a new show
# Route for editing a show
@routes.route('/create_show', methods=['GET', 'POST'])
def create_show():
    form = ShowForm()
    if form.validate_on_submit():
        # create show
        show = Show(name=form.name.data, rating=form.rating.data, tags=form.tags.data, 
                    ticket_price=form.ticket_price.data, venue_id=form.venue.data)
        
        # save image file
        if form.image.data:
            filename = images.save(form.image.data)
            show.image_path = filename
        
        db.session.add(show)
        db.session.commit()
        flash('Show created successfully!', 'success')
        return redirect(url_for('routes.shows'))
    else:
        flash('Invalid form input!', 'danger')
        
    return render_template('create_show.html', form=form, show={}, now=datetime.now())


# Route for editing a show
@routes.route('/show/edit/<int:id>', methods=['GET', 'POST'])
@admin_required

def edit_show(id):
    show = Show.query.get(id)
    if request.method == 'POST':
        show.name = request.form['name']
        show.rating = request.form['rating']
        show.tags = request.form['tags']
        show.ticket_price = request.form['ticket_price']
        db.session.commit()
        flash('Show updated successfully!')
        return redirect(url_for('routes.shows'))
    return render_template('edit_show.html', show=show,now=datetime.now())

# Route for deleting a show
@routes.route('/show/delete/<int:id>', methods=['GET', 'POST'])
@admin_required
def delete_show(id):
    show = Show.query.get(id)
    if request.method == 'POST':
        db.session.delete(show)
        db.session.commit()
        flash('Show deleted successfully!')
        return redirect(url_for('routes.shows'))
    return render_template('delete_show.html', show=show,now=datetime.now())

# Route for creating a booking
@routes.route('/create_booking', methods=['GET', 'POST'])
@user_required

def create_booking():
    form = BookingForm()
    form.show_name.choices = [(s.name, s.name) for s in Show.query.all()]
    form.venue_name.choices = [(v.name, v.name) for v in Venue.query.all()]

    if form.validate_on_submit():
        show_name = form.show_name.data
        venue_name = form.venue_name.data
        quantity = form.quantity.data

        # Get the show object associated with the selected show name
        show = Show.query.filter_by(name=show_name).first()

        # Get the venue object associated with the selected venue name
        venue = Venue.query.filter_by(name=venue_name).first()

        # Check if the selected venue is associated with the selected show
        if venue.id != show.venue_id:
            flash('Please select the correct venue for this show.', 'danger')
            return redirect(url_for('routes.create_booking'))

        # Create a new booking
        booking = Booking(show_id=show.id, venue_id=venue.id, user_id=current_user.id, quantity=quantity)
        db.session.add(booking)
        db.session.commit()

        flash('Booking created successfully!', 'success')
        return redirect(url_for('routes.my_bookings'))

    return render_template('create_booking.html', form=form, now=datetime.now())



# Route for viewing user's bookings
@routes.route('/my_bookings', methods=['GET'])
@user_required
def my_bookings():
    if current_user is None:
        # user is not logged in
        return redirect(url_for('login.login'))

    # get user's bookings from database
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    
    # create a list to store booking details along with show and venue names
    booking_details = []
    
    for booking in bookings:
        show = Show.query.get(booking.show_id)
        venue = Venue.query.get(booking.venue_id)
        #show = session.get(Show, booking.show_id)
        #venue = session.get(Venue, booking.venue_id)
        
        booking_detail = {
            'id' : booking.id,
            'show_name': show.name,
            'venue_name': venue.name,
            'quantity': booking.quantity
        }
        booking_details.append(booking_detail)
      
    return render_template('my_bookings.html', booking_details=booking_details, now=datetime.now())


# Route for deleting a booking
@routes.route('/delete_booking/<int:booking_id>', methods=['POST'])
@user_required
def delete_booking(booking_id):
    # get booking from database
    booking = Booking.query.get(booking_id)
    flash('Confirm you want to delete this booking, this cannot be undone later')
    # check if booking exists and belongs to the current user
    if booking and booking.user_id == current_user.id:
        db.session.delete(booking)
        db.session.commit()
        flash('Booking deleted successfully!', 'success')
    else:
        flash('Booking not found or you are not authorized to delete it!', 'danger')

    return redirect(url_for('routes.my_bookings'))






@routes.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        place = request.form['location']
        rating = request.form.get('rating', None)  # use get() method to set rating to None if not provided
        tags = request.form.get('tag', None)  # use get() method to set tags to None if not provided

        venues = Venue.query.filter(Venue.place == place).all()

        if rating and tags:
            shows = Show.query.filter(Show.name.ilike('%{}%'.format(search_term)), Show.rating == rating, Show.tags == tags).all()
        elif rating:
            shows = Show.query.filter(Show.name.ilike('%{}%'.format(search_term)), Show.rating == rating).all()
        elif tags:
            shows = Show.query.filter(Show.name.ilike('%{}%'.format(search_term)), Show.tags == tags).all()
        else:
            shows = Show.query.filter(Show.name.ilike('%{}%'.format(search_term))).all()

        # Create a dictionary to store the venue information for each show
        show_venues = {}
        for show in shows:
            venue = Venue.query.filter(Venue.id == show.venue_id).first()
            show_venues[show.id] = venue

        return render_template('search_results.html', venues=venues, shows=shows, show_venues=show_venues, now=datetime.now())

    return render_template('search.html', now=datetime.now())



### To test db connectivity
from application.models import User

@routes.route('/test')

def test_db():
   users = User.query.all()
   for user in users:
       print (user.username)
   return render_template('test.html',users=users, now=datetime.now())

def register_routes(app):
    app.register_blueprint(routes)

