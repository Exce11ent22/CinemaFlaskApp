import math
from datetime import datetime

from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_required, current_user

from app import db
from app.cinema_module.models import Movie, Session, CinemaHall, Ticket, TicketsAndUsers

cinema = Blueprint('cinema', __name__)


@cinema.route('/profile')
@login_required
def profile():
    tau = TicketsAndUsers.query.filter_by(user_id=current_user.id).all()
    return render_template('for_users/profile.html', user=current_user, tau=tau, ticket=Ticket, session=Session, movie=Movie)


@cinema.route('/sessions', methods=['GET', 'POST'])
@login_required
def sessions():
    title = None
    if request.method == 'POST':
        title = request.form['title']
    all_sessions = Session.query.order_by(Session.date).all()
    sessions = []
    for session in all_sessions:
        if session.date >= datetime.now():
            if title:
                movie = Movie.query.filter_by(id=session.movie_id, title=title).first()
                if movie:
                    sessions.append(session)
            else:
                sessions.append(session)
    return render_template('for_users/sessions.html', sessions=sessions, movie=Movie, hall=CinemaHall)


@cinema.route('/buy_tickets/<int:id>')
@login_required
def buy_ticket(id):
    tickets = Ticket.query.filter_by(session_id=id).all()
    session = Session.query.get(id)
    hall = CinemaHall.query.get(session.cinema_hall_id)
    tickets = chunks(tickets, hall.rows)
    return render_template('for_users/buy_ticket.html', tickets=tickets, session=session, movie=Movie, hall=CinemaHall)


@cinema.route('/ticket/<int:id>/<int:row>')
@login_required
def ticket(id, row):
    ticket = Ticket.query.get(id)
    if ticket.sold:
        flash('The ticket has already sold')
        return redirect(url_for('cinema.sessions'))
    ticket.sold = True
    try:
        el = TicketsAndUsers(user_id=current_user.id, ticket_id=ticket.id)
        db.session.add(el)
        db.session.commit()
    except:
        flash('Something wrong while transaction')
    return render_template('for_users/ticket.html', ticket=ticket, row=row, session=Session)


@cinema.route('/movie/<int:id>')
@login_required
def movie(id):
    movie = Movie.query.get(id)
    return render_template('for_users/movie.html', movie=movie)


@cinema.route('/admin/sessions', methods=['GET', 'POST'])
@login_required
def admin_sessions():
    if not current_user.is_admin:
        return redirect(url_for('auth.become_an_admin'))
    if request.method == 'POST':
        date = datetime.strptime(
            request.form['date'],
            '%Y-%m-%dT%H:%M')
        hall_id = int(request.form['hall_id'])
        movie_id = int(request.form['movie_id'])
        price = int(request.form['price'])
        movie = Movie.query.get(int(request.form['movie_id']))
        hall = CinemaHall.query.get(int(request.form['hall_id']))
        if not (movie and hall):
            flash('Movie or hall does not exist')
            return redirect(url_for('cinema.admin_sessions'))
        session = Session(date=date, cinema_hall_id=hall_id, movie_id=movie_id, price=price)
        try:
            db.session.add(session)
            db.session.commit()
        except:
            flash('Something Wrong')
            return redirect(url_for('cinema.admin_sessions'))
        make_tickets(session)
    sessions = Session.query.all()
    return render_template('for_admins/sessions.html', sessions=sessions, movie=Movie, hall=CinemaHall)


@cinema.route('/admin/session/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def admin_session_delete(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    session = Session.query.get(id)
    delete_tickets(session)
    try:
        db.session.delete(session)
        db.session.commit()
    except:
        flash('Something Wrong')
    return redirect(url_for('cinema.admin_sessions'))


@cinema.route('/admin/session/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_session_edit(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    session = Session.query.get(id)
    if request.method == 'POST':
        session.date = datetime.strptime(
            request.form['date'],
            '%Y-%m-%dT%H:%M')
        session.cinema_hall_id = int(request.form['hall_id'])
        session.movie_id = int(request.form['movie_id'])
        session.price = int(request.form['price'])
        movie = Movie.query.get(int(request.form['movie_id']))
        hall = CinemaHall.query.get(int(request.form['hall_id']))
        delete_tickets(session)
        make_tickets(session)
        if not (movie and hall):
            flash('Movie or hall does not exist')
            return redirect(url_for('cinema.admin_session_edit', id=session.id))
        try:
            db.session.commit()
        except:
            flash('Something Wrong')
        return redirect(url_for('cinema.admin_sessions'))
    return render_template('for_admins/edit_session.html', session=session, movie=Movie, hall=CinemaHall)


@cinema.route('/admin/movies', methods=['GET', 'POST'])
@login_required
def admin_movies():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    if request.method == 'POST':
        title = request.form['title']
        rel_date = datetime.strptime(
            request.form['rel_date'],
            '%Y-%m-%d')
        duration = int(request.form['duration'])
        genres = request.form['genres']
        countries = request.form['countries']
        movie = Movie(title=title, rel_date=rel_date, duration=duration, genres=genres, countries=countries)
        try:
            db.session.add(movie)
            db.session.commit()
        except:
            flash('Something Wrong')
            return redirect(url_for('cinema.admin_movies'))
    movies = Movie.query.all()
    return render_template('for_admins/movies.html', movies=movies)


@cinema.route('/admin/movies/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def admin_movies_delete(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    movie = Movie.query.get(id)
    try:
        db.session.delete(movie)
        db.session.commit()
    except:
        flash('Something Wrong')
    return redirect(url_for('cinema.admin_movies'))


@cinema.route('/admin/movies/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_movies_edit(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    movie = Movie.query.get(id)
    if request.method == 'POST':
        movie.title = request.form['title']
        movie.rel_date = datetime.strptime(
            request.form['rel_date'],
            '%Y-%m-%d')
        movie.duration = int(request.form['duration'])
        movie.genres = request.form['genres']
        movie.countries = request.form['countries']
        try:
            db.session.commit()
        except:
            flash('Something Wrong')
        return redirect(url_for('cinema.admin_movies'))
    return render_template('for_admins/edit_movie.html', movie=movie)


@cinema.route('/admin/halls', methods=['GET', 'POST'])
@login_required
def admin_halls():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        seats = int(request.form['seats'])
        rows = int(request.form['rows'])
        category = request.form['category']
        hall = CinemaHall(name=name, seats=seats, rows=rows, category=category)
        if seats < rows:
            flash('Must be: seats > rows!')
            return redirect(url_for('cinema.admin_halls'))
        try:
            db.session.add(hall)
            db.session.commit()
        except:
            flash('Something Wrong')
            return redirect(url_for('cinema.admin_halls'))
    halls = CinemaHall.query.all()
    return render_template('for_admins/halls.html', halls=halls)


@cinema.route('/admin/halls/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def admin_hall_delete(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    hall = CinemaHall.query.get(id)
    try:
        db.session.delete(hall)
        db.session.commit()
    except:
        flash('Something Wrong')
    return redirect(url_for('cinema.admin_halls'))


@cinema.route('/admin/halls/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_hall_edit(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    hall = CinemaHall.query.get(id)
    if request.method == 'POST':
        hall.name = request.form['name']
        hall.seats = int(request.form['seats'])
        hall.rows = int(request.form['rows'])
        hall.category = request.form['category']
        try:
            db.session.commit()
        except:
            flash('Something Wrong')
        return redirect(url_for('cinema.admin_halls'))
    return render_template('for_admins/edit_hall.html', hall=hall)


def make_tickets(session):
    hall = CinemaHall.query.get(session.cinema_hall_id)
    try:
        for i in range(hall.seats):
            ticket = Ticket(session_id=session.id, seat=i+1)
            db.session.add(ticket)
        db.session.commit()
    except:
        flash('Cannot make tickets')
        return False


def delete_tickets(session):
    try:
        tickets = Ticket.query.filter_by(session_id=session.id).all()
        for ticket in tickets:
            db.session.delete(ticket)
        db.session.commit()
    except:
        flash('Cannot refresh tickets')
        return False


def chunks(l, r):
    n = math.ceil(len(l) / r)
    return [l[i:i+n] for i in range(0, len(l), n)]
