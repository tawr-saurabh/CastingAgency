import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .database.models import Movies, Actors
from auth.auth import AuthError, requires_auth

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)

# -------------------------------------------------------------#
# GET CONTROLLERS
# -------------------------------------------------------------#

    @app.route('/movies', methods=["GET"])
    @requires_auth('get:movies')
    def moviedata():
        movie_data = Movies.query.all()
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
            'movies': actor_list,
            'total movies': len(actor_list)
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
    def delete_movie(actor_id):
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

    return app


APP = create_app()

# ----------------------------------------------------------------------------#
# Launch
# ----------------------------------------------------------------------------#
if __name__ == '__main__':
    APP.run()
