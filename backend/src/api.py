import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)


# db_drop_and_create_all()


# ROUTES

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    return jsonify({
        'success': 'True',
        'drinks': [drink.short() for drink in drinks]
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()

    return jsonify({
        'success': 'True',
        'drinks': [drink.long() for drink in drinks]
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    data = request.get_json()
    title = data.get('title')
    recipe = data.get('recipe')

    drink = Drink(title=title, recipe=json.dumps(recipe))

    drink.insert()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    data = request.get_json()
    title = data.get('title')
    recipe = data.get('recipe')

    drink = Drink.query.get_or_404(drink_id)

    drink.title = title
    drink.recipe = json.dumps(recipe)
    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.get_or_404(drink_id)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink_id
    })


# Error Handling

@app.errorhandler(422)
def unprocessable(e):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(400)
def bad_request(e):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource Not Found'
    }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }), 405


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500


@app.errorhandler(AuthError)
def internal_server_error(e):
    return jsonify({
        'success': False,
        'error': e.error['code'],
        'message': e.error['description']
    }), e.status_code
