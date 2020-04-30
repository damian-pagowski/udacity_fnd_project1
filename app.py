#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from models import *
from flask_migrate import Migrate
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
import datetime


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    # @TODO FIX!!!
#   date = dateutil.parser.parse(value)
#   if format == 'full':
#       format="EEEE MMMM, d, y 'at' h:mma"
#   elif format == 'medium':
#       format="EE MM, dd, y h:mma"
#   return babel.dates.format_datetime(date, format)
    return "2020/1/1"


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
def get_unique_cities_states():
    cities = []
    for venue in Venue.query.distinct(Venue.city):
        cities.append({"city": venue.city, "state": venue.state})
    return cities


def get_upcoming_shows(venue_id):
    now = datetime.datetime.now()
    # print(venue_id)
    # print(now)
    # .filter(Show.start_time > now)
    shows = Show.query.filter(Show.venue_id == venue_id)
    return list(map(Show.format, shows))


def get_past_shows(venue_id):
    now = datetime.datetime.now
    # filter(Show.start_time < now)
    shows = Show.query.filter(Show.venue_id == venue_id)
    return list(map(Show.format, shows))


@app.route('/venues')
def venues():
    city_state_data = get_unique_cities_states()
    response = []
    for city_state in city_state_data:
        data = city_state
        data['venues'] = []
        venues_in_city = Venue.query.filter(Venue.city == city_state["city"])
        for venue in venues_in_city:
            upcoming = get_upcoming_shows(venue.id)
            num_upcoming_shows = len(upcoming)
            data['venues'].append(
                {"name": venue.name, "id": venue.id, "num_upcoming_shows": num_upcoming_shows})
        response.append(data)
    # return jsonify(response)
    return render_template('pages/venues.html', areas=response)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_phrase = request.form["search_term"]
    matching_venues = Venue.query.filter(Venue.name.contains(search_phrase))
    response = {
    "count": 0,
    "data": []
    }
    for venue in matching_venues:
        upcoming = get_upcoming_shows(venue.id)
        num_upcoming_shows = len(upcoming)
        response['count'] += 1
        response['data'].append(
            {"name": venue.name, "id": venue.id, "num_upcoming_shows": num_upcoming_shows})
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


def format_shows(shows):
    data = []
    for show in shows:
        show_formatted = {}
        show_formatted["artist_id"] = show["artist_id"]
        show_formatted["start_time"] = show["start_time"]
        artist_id = show["artist_id"]
        artist = Artist.query.get(artist_id)
        show_formatted["artist_name"] = artist["name"]
        show_formatted["artist_image_link"] = artist["image_link"]
        data.append(show_formatted)
    return data


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    result = Venue.query.get(venue_id).format()
    # upcoming shows
    upcoming_shows = get_upcoming_shows(venue_id)
    upcoming_shows_formatted = format_shows(upcoming_shows)
    result["upcoming_shows"] = upcoming_shows_formatted
    num_upcoming_shows = len(upcoming_shows)
    result['num_upcoming_shows'] = num_upcoming_shows
    # past shows
    past_shows = get_past_shows(venue_id)
    past_shows_formatted = format_shows(past_shows)
    result["past_shows"] = past_shows_formatted
    past_shows_count = len(past_shows)
    result['past_shows_count'] = past_shows_count
    # return jsonify(result)
    return render_template('pages/show_venue.html', venue=result)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # extract data from from
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres_form_data = request.form.getlist('genres')
    image_link = request.form.getlist("image_link")
    genres = ','.join(genres_form_data)
    facebook_link = request.form['facebook_link']
    # insert Venue to DB
    venue = Venue(name, city, state, address, phone,
                  image_link, facebook_link, genres)
    try:
        venue.insert()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('Venue ' + request.form['name'] + ' could not be listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.get(venue_id).delete()
        return jsonify({"status": "venue deleted"})
    except:
        return jsonify({"status": "failed to delete venue"})

#  Artists
#  ----------------------------------------------------------------

def get_upcoming_shows_by_artist_id(id):
    shows = Show.query.filter(Show.artist_id == id)
    return list(map(Show.format, shows))

def get_post_shows_by_artist_id(id):
    shows = Show.query.filter(Show.artist_id == id)
    return list(map(Show.format, shows))

@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = []
    for each in artists:
        artist = each.format()
        artist_min_info = {}

        artist_min_info["id"] = artist["id"]
        artist_min_info["name"] = artist["name"]
    
        data.append(artist_min_info)
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
        # artists = Artist.query.filter(Artist.name.contains(search_phrase))
# 
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    result = artist.format()
    # upcoming shows
    upcoming_shows = get_upcoming_shows_by_artist_id(artist_id)
    upcoming_shows_formatted = format_shows(upcoming_shows)
    result["upcoming_shows"] = upcoming_shows_formatted
    num_upcoming_shows = len(upcoming_shows)
    result['num_upcoming_shows'] = num_upcoming_shows
    # past shows
    past_shows = get_post_shows_by_artist_id(artist_id)
    past_shows_formatted = format_shows(past_shows)
    result["past_shows"] = past_shows_formatted
    past_shows_count = len(past_shows)
    result['past_shows_count'] = past_shows_count
    # return jsonify(result)
    return render_template('pages/show_artist.html', artist=result)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
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
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
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
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
     # extract data from from
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres_form_data = request.form.getlist('genres')
    genres = ','.join(genres_form_data)
    image_link =    request.form["image_link"]
    facebook_link = request.form['facebook_link']
    # insert Venue to DB
    artist = Artist( name, city, state, phone, image_link, facebook_link, genres)
    try:
        artist.insert()
        flash('artist ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('artist ' + request.form['name'] + ' could not be listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
