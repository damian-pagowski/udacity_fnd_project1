import sys
from flask import flash

class VenuesController(models, db):

def get_all_venues(model):
    venues = model.query.order_by(model.city).all()
    data = []
    current_city = None
    venue_info = None
    for venue in venues:
        if venue.city != current_city:
            if venue_info != None:
                data.append(venue_info)
            # set new city
            current_city = venue.city
        venue_info = {"city": venue.city, "state": venue.state, "venues": []}
        venue_info['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 666})
    return (data)


def create_venue(venueModel,  request, db):
    error = False
    venue = None
    try:
        venue = venueModel()
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        genres_form_data = request.form.getlist('genres')
        venue.genres = ','.join(genres_form_data)
        venue.facebook_link = request.form['facebook_link']
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if not error:
        flash(f'Venue {venue.name} was created.')
    if error:
        flash(f'An error occurred. Venue {venue.name} could not be created.')
        venue = None
    return venue


def search_for_venues(model, searchPhrase):
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    return {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
def get_venue_by_id(venueModel, showModel, artistModel, id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = venueModel.query.get(id)
    upcoming_shows_query = db.session.query(showModel).join(artistModel).filter(showModel.venue_id == venue_id).filter(showModel.start_time > datetime.now()).all()
    upcoming_shows = []

    past_shows_query = db.session.query(showModel).join(artistModel).filter(showModel.venue_id == venue_id).filter(showModel.start_time < datetime.now()).all()
    past_shows = []

    for show in past_shows_query:
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    for show in upcoming_shows_query:
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    return {
        "id": 3,
        "name": "Park Square Live Music & Coffee",
        "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "past_shows": [{
            "artist_id": 5,
            "artist_name": "Matt Quevedo",
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": "2019-06-15T23:00:00.000Z"
        }],
        "upcoming_shows": [{
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-15T20:00:00.000Z"
        }],
        "past_shows_count": 1,
        "upcoming_shows_count": 1,
    }


def remove_venue(model, id, db):
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    try:
        venue = model.query.get(id)
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash(f'An error occurred. Venue {venue_id} could not be deleted.')
    if not error:
        flash(f'Venue {venue_id} was successfully deleted.')
