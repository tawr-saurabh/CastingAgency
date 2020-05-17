import os
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, abort, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect

import constants as constants
from auth import requires_auth

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# os.environ['AUTH0_CLIENT_ID'] = constants.AUTH0_CLIENT_ID
# os.environ['AUTH0_CLIENT_SECRET'] = constants.AUTH0_CLIENT_SECRET
# os.environ['AUTH0_CALLBACK_URL'] = constants.AUTH0_CALLBACK_URL
# os.environ['AUTH0_DOMAIN'] = constants.AUTH0_DOMAIN
# os.environ['AUTH0_AUDIENCE'] = constants.AUTH0_AUDIENCE
# os.environ['SECRET_KEY'] = constants.SECRET_KEY

AUTH0_CLIENT_ID = os.environ.get('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = os.environ.get('AUTH0_CLIENT_SECRET')
AUTH0_CALLBACK_URL = os.environ.get('AUTH0_CALLBACK_URL')
AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
AUTH0_BASE_URL = os.environ.get('AUTH0_BASE_URL')
AUTH0_AUDIENCE = os.environ.get('AUTH0_AUDIENCE')
SECRET_KEY = os.environ.get('SECRET_KEY')

#database_name = "casting_agency"
database_path = os.environ.get('DATABASE_URL')

db = SQLAlchemy()

app = Flask(__name__)
app.secret_key = constants.SECRET_KEY
app.debug = True

app.config["SQLALCHEMY_DATABASE_URI"] = database_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.app = app
db.init_app(app)
CORS(app, resources={
    r'/*': {'origins': '*'}
})
oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    audience=AUTH0_AUDIENCE,
    response_type='token',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    redirect_url=AUTH0_CALLBACK_URL,
    access_token_url=AUTH0_BASE_URL + "/oauth/token",
    authorize_url=AUTH0_BASE_URL + "/authorize?" #+ 'audience=' + AUTH0_AUDIENCE + '&' + 'response_type=token&' + 'client_id=' + AUTH0_CLIENT_ID + '&' + 'redirect_uri=' + AUTH0_CALLBACK_URL
)


# -------------------------------------------------------------#
# Movies
# Have title and release date
# -------------------------------------------------------------#
class Movies(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.String(255), nullable=False)

    # actors = db.relationship('actors', backref='movie_list', lazy=True)

    def __init__(self, title, release_date):
        self.title = title
        self.release_date = release_date

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
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date}


# -------------------------------------------------------------#
# Actors
# Have name, age and gender
# -------------------------------------------------------------#


class Actors(db.Model):
    __tablename__ = 'actors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    age = db.Column(db.String(255))
    gender = db.Column(db.String(255))

    # movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

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
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender}


db.create_all()


#
# -------------------------------------------------------------#
# GET CONTROLLERS
# -------------------------------------------------------------#
@app.route('/login')
def login():
    link = AUTH0_BASE_URL + '/authorize?' + 'audience=' + AUTH0_AUDIENCE + '&' + 'response_type=token&' + 'client_id=' + AUTH0_CLIENT_ID + '&' + 'redirect_uri=' + AUTH0_CALLBACK_URL
    return redirect(link)#auth0.authorize_redirect(audience=AUTH0_AUDIENCE, redirect_uri=AUTH0_CALLBACK_URL)


@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    return redirect(AUTH0_BASE_URL + '/v2/logout?')


@app.route('/callback')
def callback_handler():
    # token = auth0.authorize_access_token()
    # print(token)
    # resp = auth0.get('userinfo')
    # print(resp.json())
    return jsonify({
        'token': ''
    })


@app.route('/movies', methods=["GET"])
@requires_auth('get:movies')
def moviedata():
    movie_data = Movies.query.all()
    # print(movie_data)
    movie_list = []
    for movie in movie_data:
        movie_list.append(movie.format())
    return jsonify({
        'success': True,
        'movies': movie_list,
        'total movies': len(movie_list)
    })


@app.route('/actors', methods=["GET"])
@requires_auth('get:actors')
def actorList():
    actor_data = Actors.query.all()
    actor_list = []
    for actor in actor_data:
        actor_list.append(actor.format())
    return jsonify({
        'success': True,
        'actors': actor_list,
        'total actors': len(actor_list)
    })


# -------------------------------------------------------------#
# PATCH CONTROLLERS
# -------------------------------------------------------------#

@app.route('/movies/<int:movie_id>', methods=['PATCH'])
@requires_auth('patch:movie')
def movie_update(movie_id):
    body = request.get_json()
    try:
        specific_movie = Movies.query.get(movie_id)
        if specific_movie is None:
            abort(404)
        if 'title' in body:
            specific_movie.title = body.get('title')
            specific_movie.release_date = body.get('release_date')
        specific_movie.update()
        return jsonify({
            'success': True,
            'id': specific_movie.id
        })

    except:
        abort(400)


@app.route('/actors/<int:actor_id>', methods=['PATCH'])
@requires_auth('patch:actor')
def actor_update(actor_id):
    body = request.get_json()
    try:
        specific_actor = Actors.query.get(actor_id)
        if specific_actor is None:
            abort(404)
        if 'name' in body:
            specific_actor.name = body.get('name')
            specific_actor.age = body.get('age')
            specific_actor.gender = body.get('gender')
        specific_actor.update()
        return jsonify({
            'success': True,
            'id': specific_actor.id
        })

    except:
        abort(400)


# -------------------------------------------------------------#
# DELETE CONTROLLERS
# -------------------------------------------------------------#

@app.route('/movies/<int:movie_id>', methods=['DELETE'])
@requires_auth('delete:movie')
def delete_movie(movie_id):
    try:
        specific_movie = Movies.query.get(movie_id)
        if specific_movie is None:
            abort(404)
        specific_movie.delete()
        movie_data = Movies.query.all()
        movie_list = []
        for movie in movie_data:
            movie_list.append(movie.format())

        return jsonify({
            'success': True,
            'deleted': specific_movie.id,
            'movies': movie_list,
            'total movies': len(movie_list)
        })

    except:
        abort(422)


@app.route('/actors/<int:actor_id>', methods=['DELETE'])
@requires_auth('delete:actor')
def delete_actor(actor_id):
    try:
        specific_actor = Movies.query.get(actor_id)
        if specific_actor is None:
            abort(404)
        specific_actor.delete()
        actor_data = Actors.query.all()
        actor_list = []
        for actor in actor_data:
            actor_list.append(actor.format())

        return jsonify({
            'success': True,
            'deleted': specific_actor.id,
            'actors': actor_list,
            'total actors': len(actor_list)
        })

    except:
        abort(422)


# -------------------------------------------------------------#
# POST CONTROLLERS
# -------------------------------------------------------------#

@app.route('/movies', methods=['POST'])
@requires_auth('post:movie')
def add_movie():
    body = request.get_json()
    try:
        movie_title = body.get('title')
        movie_release_date = body.get('release_date')

        specific_movie = Movies(title=movie_title, release_date=movie_release_date)
        specific_movie.insert()

        movie_data = Movies.query.all()
        movie_list = []
        for movie in movie_data:
            movie_list.append(movie.format())

        return jsonify({
            'success': True,
            'movies': movie_list,
            'total movies': len(movie_list)
        })

    except:
        abort(422)


@app.route('/actors', methods=['POST'])
@requires_auth('post:actor')
def add_actor():
    body = request.get_json()
    try:
        actor_name = body.get('name')
        actor_age = body.get('age')
        actor_gender = body.get('gender')

        specific_actor = Actors(name=actor_name, age=actor_age, gender=actor_gender)
        specific_actor.insert()

        actor_data = Actors.query.all()
        actor_list = []
        for actor in actor_data:
            actor_list.append(actor.format())

        return jsonify({
            'success': True,
            'movies': actor_list,
            'total movies': len(actor_list)
        })

    except:
        abort(422)


# ----------------------------------------------------------------------------#
# Error Handling
# ----------------------------------------------------------------------------#
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'reason': "resource not found",
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'reason': "unprocessable",
    }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'reason': "bad request",
    }), 400


@app.errorhandler(405)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 405,
        'reason': "method not allowed",
    }), 405


# return app


# APP = create_app()

# ----------------------------------------------------------------------------#
# Launch
# ----------------------------------------------------------------------------#
if __name__ == '__main__':
    app.run()
