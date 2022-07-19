from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('business_page.html')


from app.authorisation.controllers import auth
from app.cinema_module.controllers import cinema

app.register_blueprint(auth)
app.register_blueprint(cinema)

db.create_all()
