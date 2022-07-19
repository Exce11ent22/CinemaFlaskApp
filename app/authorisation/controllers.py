from flask import Blueprint, render_template, url_for, flash, request
from flask_login import logout_user, login_user, login_required, current_user
from werkzeug.utils import redirect
from werkzeug.security import check_password_hash, generate_password_hash

import config
from app import db, login_manager
from app.authorisation.models import User

auth = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if not (name and email and password and confirm):
            flash('Please, fill all fields')
        elif password != confirm:
            flash('Passwords are not equal')
        else:
            try:
                hash_pwd = generate_password_hash(password)
                new_user = User(name=name, email=email, password=hash_pwd)
                db.session.add(new_user)
                db.session.commit()
            except:
                flash('Email almost exist or another problem')
                return redirect(url_for('auth.signup'))

            return redirect(url_for('auth.login'))
    return render_template('authorisation/signup.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not (email and password):
            flash('Please fill all fields')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('cinema.sessions'))
        else:
            flash('Email or password is not correct')
    return render_template('authorisation/login.html')


@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@auth.route('/become_an_admin', methods=['GET', 'POST'])
@login_required
def become_an_admin():
    if request.method == 'POST':
        password = request.form['password']
        admin_password = request.form['admin_password']
        if not (password and admin_password):
            flash('Please, fill all fields')
            return render_template('authorisation/become_an_admin.html')

        if not check_password_hash(current_user.password, password) or admin_password != config.admin_secret_key:
            flash(f'{password}, {current_user.password} Password or admin password isn\'t correct')
            return render_template('authorisation/become_an_admin.html')

        user = User.query.filter_by(id=current_user.id).first()
        user.role = User.ADMIN
        try:
            db.session.commit()
        except:
            flash('something wrong')
            return redirect(url_for(become_an_admin))
        return redirect(url_for('cinema.admin_sessions'))

    return render_template('authorisation/become_an_admin.html')
