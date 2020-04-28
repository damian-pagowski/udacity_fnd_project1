import sys

def get_all_venues(model):
    venues = model.query.order_by(model.city).all()
    data =  []
    current_city = None
    venue_info = None
    for venue in venues:
        if venue.city != current_city:
            if venue_info != None:
                data.append(venue_info)
            # set new city
            current_city = venue.city
        venue_info = { "city": venue.city, "state": venue.state, "venues": []}
        venue_info['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 666})
    return (data)

def create_venue(model, request, db):
    error = False
    try:
        venue = model()
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
    return {"data": venue, "error" : error}