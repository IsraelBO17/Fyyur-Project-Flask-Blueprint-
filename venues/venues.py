import sys
import json
from flask import (
    Flask,
    render_template,
    Blueprint,
    request,
    Response,
    flash,
    redirect,
    url_for
)
from models import *
from forms import VenueForm
from datetime import datetime
from filters import format_datetime

#----------------------------------------------------------------------------#
# Venue BluePrint.
#----------------------------------------------------------------------------#
venues_bp = Blueprint('venues_bp', __name__)


#----------------------------------------------------------------------------#
# Display list of Venues per State and City.
#----------------------------------------------------------------------------#
@venues_bp.route('/venues')
def venues():    
    real_data = []
    venues = Venue.query.all()  # Gets all the venues from the database
    today = datetime.now()  # Present time
    grouped_venues = Venue.query.distinct(Venue.city, Venue.state).all() 

    for grouped_venue in grouped_venues:
        venue_data = []
        for venue in venues:
            if grouped_venue.city == venue.city:
                venue_data.append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len([Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > today)])
                })
        real_data.append({
            "city": grouped_venue.city,
            "state": grouped_venue.state,
            "venues": venue_data
        })

    return render_template('pages/venues.html', areas=real_data)


#----------------------------------------------------------------------------#
# Search for a Venue.
#----------------------------------------------------------------------------#
@venues_bp.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(venues),
        "data": []
    }

    for venue in venues:
        response['data'].append({
            "id": venue.id,
            "name": venue.name,
        })
        
    print(request.endpoint)

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


#----------------------------------------------------------------------------#
# Displays a Venue's details.
#----------------------------------------------------------------------------#
@venues_bp.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    real_data = Venue.query.get(venue_id)
    real_data.genres = json.loads(real_data.genres)
    today = datetime.now()
    
    shows = Show.query.join(Venue).filter(Show.venue_id == venue_id).all()
    past_shows = []
    upcoming_shows = []

    for show in shows:
        if show.start_time > today:
            upcoming_shows.append({
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.start_time))
            })
        else:
            past_shows.append({
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.start_time))
            })

    real_data.past_shows = past_shows
    real_data.upcoming_shows = upcoming_shows
    real_data.past_shows_count = len(past_shows)
    real_data.upcoming_shows_count = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=real_data)


#----------------------------------------------------------------------------#
# Renders Form for creating a Venue.
#----------------------------------------------------------------------------#
@venues_bp.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


#----------------------------------------------------------------------------#
# Creates a Venue.
#----------------------------------------------------------------------------#
@venues_bp.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        form = VenueForm(request.form)
        if form.validate_on_submit():
            new_venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=json.dumps(form.genres.data),
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website=form.website_link.data,
                seeking_talent= form.seeking_talent.data,
                seeking_description = form.seeking_description.data
            )

            db.session.add(new_venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        else:
            for field, message in form.errors.items():
                flash(f'Invalid input in {field} field. --> ({message})')

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash(f'An error occured. Venue could not be listed.')
    finally:
        db.session.close()
        return render_template('pages/home.html')


#----------------------------------------------------------------------------#
# Delete a Venue. (Not functioning)
#----------------------------------------------------------------------------#
@venues_bp.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    return None


#----------------------------------------------------------------------------#
# Renders Form for updating a Venue.
#----------------------------------------------------------------------------#
@venues_bp.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


#----------------------------------------------------------------------------#
# Update Venue details. (Not functioning)
#----------------------------------------------------------------------------#
@venues_bp.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    return redirect(url_for('show_venue', venue_id=venue_id))