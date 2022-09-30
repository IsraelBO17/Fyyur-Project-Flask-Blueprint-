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
from forms import ShowForm
from datetime import datetime
from filters import format_datetime

#----------------------------------------------------------------------------#
# Shows BluePrint.
#----------------------------------------------------------------------------#
shows_bp = Blueprint('shows_bp', __name__)


#----------------------------------------------------------------------------#
# Display list of Shows.
#----------------------------------------------------------------------------#
@shows_bp.route('/shows')
def shows():
    shows = Show.query.all()
    real_data = []

    for show in shows:
        real_data.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })

    return render_template('pages/shows.html', shows=real_data)

#----------------------------------------------------------------------------#
# Renders Form for creating a Show.
#----------------------------------------------------------------------------#
@shows_bp.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


#----------------------------------------------------------------------------#
# Creates a new Show.
#----------------------------------------------------------------------------#
@shows_bp.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False

    try:
        form = ShowForm(request.form)
        if form.validate_on_submit():
            new_show = Show(
                start_time = form.start_time.data,
                venue_id = form.venue_id.data,
                artist_id = form.artist_id.data
            )

            db.session.add(new_show)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!')
        else:
            for field, message in form.errors.items():
                flash(f'Invalid input in {field} field. --> ({message})')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash(f'An error occured. Show could not be listed.')
    finally:
        db.session.close()
        return render_template('pages/home.html')