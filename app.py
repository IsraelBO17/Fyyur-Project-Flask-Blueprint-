#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import logging
import json
from logging import Formatter, FileHandler
from flask import Flask, render_template
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import *
from artists.artists import artists_bp
from venues.venues import venues_bp
from shows.shows import shows_bp
from filters import format_datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    with app.app_context():
        db.init_app(app)
    return app


app = create_app()
moment = Moment(app)

migrate = Migrate(app, db)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')

#----------------------------------------------------------------------------#
# Blueprint Registration.
#----------------------------------------------------------------------------#
app.register_blueprint(venues_bp)
app.register_blueprint(artists_bp)
app.register_blueprint(shows_bp)

#----------------------------------------------------------------------------#
# Error Handlers.
#----------------------------------------------------------------------------#

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.debug = True
    app.run(host="127.0.0.1", port=8080)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
