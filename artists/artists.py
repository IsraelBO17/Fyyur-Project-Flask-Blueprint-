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
from forms import ArtistForm
from datetime import datetime
from filters import format_datetime

#----------------------------------------------------------------------------#
# Artist BluePrint.
#----------------------------------------------------------------------------#
artists_bp = Blueprint('artists_bp', __name__)


#----------------------------------------------------------------------------#
# Display list of Artists.
#----------------------------------------------------------------------------#
@artists_bp.route('/artists')
def artists():
    artists = Artist.query.all()
    return render_template('pages/artists.html', artists=artists)


#----------------------------------------------------------------------------#
# Search for an Artist.
#----------------------------------------------------------------------------#
@artists_bp.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(artists),
        "data": []
    }

    for artist in artists:
        response['data'].append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": artist
        })

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


#----------------------------------------------------------------------------#
# Displays an Artist's details.
#----------------------------------------------------------------------------#
@artists_bp.route('/artists/<int:artist_id>')
def show_artist(artist_id):    
    real_data = Artist.query.get(artist_id)
    real_data.genres = json.loads(real_data.genres)
    today = datetime.now()

    shows = Show.query.join(Artist).filter(Show.artist_id == artist_id).all()
    past_shows = []
    upcoming_shows = []

    for show in shows:
        if show.start_time > today:
            upcoming_shows.append({
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": format_datetime(str(show.start_time))
            })
        else:
            past_shows.append({
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": format_datetime(str(show.start_time))
            })

    real_data.past_shows = past_shows
    real_data.upcoming_shows = upcoming_shows
    real_data.past_shows_count = len(past_shows)
    real_data.upcoming_shows_count = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=real_data)


#----------------------------------------------------------------------------#
# Renders Form for creating an Artist.
#----------------------------------------------------------------------------#
@artists_bp.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


#----------------------------------------------------------------------------#
# Create an Artist.
#----------------------------------------------------------------------------#
@artists_bp.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        form = ArtistForm(request.form)
        if form.validate_on_submit():
            new_artist = Artist(
                name = form.name.data,
                city = form.city.data,
                state = form.state.data,
                phone = form.phone.data,
                image_link = form.image_link.data,
                facebook_link = form.facebook_link.data,
                genres = json.dumps(form.genres.data),
                website = form.website_link.data,
                seeking_venue = form.seeking_venue.data,
                seeking_description = form.seeking_description.data
            )

            db.session.add(new_artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        else:
            for field, message in form.errors.items():
                flash(f'Invalid input in {field} field. --> ({message})')

    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash(f'An error occured. Artist could not be listed.')
    finally:
        db.session.close()
        return render_template('pages/home.html')


#----------------------------------------------------------------------------#
# Renders Form for updating an Artist.
#----------------------------------------------------------------------------#
@artists_bp.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    
    return render_template('forms/edit_artist.html', form=form, artist=artist)


#----------------------------------------------------------------------------#
# Update Artist details. (Not functioning)
#----------------------------------------------------------------------------#
@artists_bp.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    return redirect(url_for('show_artist', artist_id=artist_id))