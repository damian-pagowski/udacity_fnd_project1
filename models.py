from app import db


class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref="venue", lazy=True)

    def __init__(self, name, city, state, address, phone, image_link, facebook_link, genres, seeking_talent=False, seeking_description=""):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.image_link = image_link
        self.facebook_link = facebook_link
        self.genres = genres
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "address": self.address,
            "phone": self.phone,
            "image_link": self.image_link,
            "facebook_link":  self.facebook_link,
            "genres": self.genres.split(","),
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description
        }

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref="artist", lazy=True)

    def __init__(self, name, city, state, phone, image_link, facebook_link, genres, seeking_venue=False, seeking_description=""):
        self.name = name
        self.city = city
        self.state = state
        self.phone = phone
        self.genres = genres
        self.image_link = image_link
        self.facebook_link = facebook_link
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "name": self.name,
            "id": self.id,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "genres": self.genres.split(","),
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description
        }


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, artist_id, venue_id, start_time):
        self.artist_id = artist_id
        self.venue_id = venue_id
        self.start_time = start_time

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "artist_id": self.artist_id,
            "venue_id": self.venue_id,
            "start_time": self.start_time,

        }
