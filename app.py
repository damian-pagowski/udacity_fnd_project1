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
    search_phrase = request.form["search_term"]
    matching_artist = Artist.query.filter(Artist.name.contains(search_phrase))
    response = {
    "count": 0,
    "data": []
    }
    for artist in matching_artist:
        upcoming = get_upcoming_shows(artist.id)
        num_upcoming_shows = len(upcoming)
        response['count'] += 1
        response['data'].append(
            {"name": artist.name, "id": artist.id, "num_upcoming_shows": num_upcoming_shows})
    # return jsonify(response)  
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
    artist = Artist.query.get(artist_id)
    data = artist.format()  
    form = ArtistForm()
    return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)

    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    genres_form_data = request.form.getlist('genres')
    artist.genres = ','.join(genres_form_data)
    artist. image_link =    request.form["image_link"]
    artist.facebook_link = request.form['facebook_link']
    # update DB
    try:
        artist.update()
        flash('artist ' + request.form['name'] + ' was successfully updated!')
    except:
        flash('artist ' + request.form['name'] + ' could not be updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    data = venue.format()
    return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    genres_form_data = request.form.getlist('genres')
    venue.genres = ','.join(genres_form_data)
    venue. image_link =    request.form["image_link"]
    venue.facebook_link = request.form['facebook_link']
    # update DB
    try:
        venue.update()
        flash('venue ' + request.form['name'] + ' was successfully updated!')
    except:
        flash('venue ' + request.form['name'] + ' could not be updated!')
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
    shows = list(map(Show.format, Show.query.all()))
    data = []
    for show_data in shows:
        show = {}
        show["start_time"] = show_data["start_time"]
        venue_id = show_data["venue_id"]
        show["venue_id"] = venue_id
        venue = Venue.format(Venue.query.get(venue_id))
        show["venue_name"] = venue["name"]
        artist_id = show_data["artist_id"]
        show["artist_id"] = artist_id
        artist = Artist.format(Artist.query.get(artist_id))
        show["artist_name"] = artist["name"]
        show["artist_image_link"] = artist["image_link"]
        data.append(show)
    # return jsonify(data)  
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Show( artist_id, venue_id, start_time)
    try:
        show.insert()
        flash('show was successfully listed!')
    except:
        flash('show  could not be listed!')
    # return render_template('pages/home.html')
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
