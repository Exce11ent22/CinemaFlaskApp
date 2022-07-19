from sqlalchemy import UniqueConstraint

from app import db


# catalog
class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False, unique=True)


# catalog
class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50), nullable=False, unique=True)


# extendable catalog
class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    rel_date = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    countries = db.Column(db.Text)
    genres = db.Column(db.Text)


class MovieAndCountry(db.Model):
    __tablename__ = 'movie_and_country'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))

    movie = db.relationship('Movie')
    country = db.relationship('Country')
    __table_args__ = (UniqueConstraint('movie_id', 'country_id', name='movie_and_country_uc'), )


class MovieAndGenre(db.Model):
    __tablename__ = 'movie_and_genre'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))

    movie = db.relationship('Movie')
    genre = db.relationship('Genre')
    __table_args__ = (UniqueConstraint('movie_id', 'genre_id', name='movie_and_genre_uc'), )


# catalog
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


# catalog
class CinemaHall(db.Model):
    __tablename__ = 'cinema_hall'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    seats = db.Column(db.Integer, nullable=False)
    rows = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50))


class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    cinema_hall_id = db.Column(db.Integer, db.ForeignKey('cinema_hall.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    cinema_hall = db.relationship('CinemaHall')
    movie = db.relationship('Movie')


class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    seat = db.Column(db.Integer, nullable=False)
    sold = db.Column(db.Boolean, default=False)

    session = db.relationship('Session')


class TicketsAndUsers(db.Model):
    __tablename__ = 'tickets_and_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    ticket_id = db.Column(db.Integer, nullable=False)
    __table_args__ = (UniqueConstraint('ticket_id', 'user_id', name='tickets_and_users_uc'),)


if __name__ == '__main__':
    db.create_all()
    db.session.commit()
