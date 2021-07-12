import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from sys import exc_info

from sqlalchemy.sql.expression import delete
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    unfiltered_drinks = Drink.query.all()
    drinks = []
    for drink in unfiltered_drinks:
        drink = drink.short()
        drinks.append(drink)
    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detailes(jwt):
    unfiltered_drinks = Drink.query.all()
    drinks = []
    for drink in unfiltered_drinks:
        drink = drink.long()
        drinks.append(drink)
    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def create_drink(jwt):
    body = request.get_json()
    try:
        title = body.get('title', None)
        recipe_unfiltered = body.get('recipe', None)
        recipe = '['
        for part in recipe_unfiltered:
            if recipe != '[':
                recipe = recipe + ','
            color = part.get('color', None)
            name = part.get('name', None)
            parts = part.get('parts', None)
            if not (color and name and parts != None):
                raise ValueError(
                    'some information is missing from the recipe'
                )
            # newrecipe = '{}"name": "{}", "color": "{}", "parts": {}{}'.format(
                # '{', name, color, parts, '}')
            recipe = recipe + '{}"name":"{}",'.format('{', name)
            recipe = recipe + ' "color":"{}",'.format(color)
            recipe = recipe + ' "parts":"{}"{}'.format(parts, '}')
            # recipe = recipe + newrecipe
        recipe = recipe + ']'
        if not (title and recipe):
            raise ValueError(
                'some information is missing, unable to create drink'
            )
        DID = body.get('id', None)
        if DID == -1 or DID is None:
            drink = Drink(title=title, recipe=recipe)
        else:
            drink = Drink(id=DID, title=title, recipe=recipe)

        drink.insert()
    except ValueError as value_error:
        print(value_error.with_traceback(value_error.__traceback__))
        abort(422)
    return jsonify({
        'success': True,
        'drink': drink.long()
    })


@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    body = request.get_json()
    try:
        title = body.get('title', None)
        recipe_unfiltered = body.get('recipe', None)
        recipe = '['
        for part in recipe_unfiltered:
            if recipe != '[':
                recipe = recipe + ','
            color = part.get('color', None)
            name = part.get('name', None)
            parts = part.get('parts', None)
            if not (color and name and parts != None):
                raise ValueError(
                    'some information is missing from the recipe'
                )
            recipe = recipe + '{}"name":"{}",'.format('{', name)
            recipe = recipe + ' "color":"{}",'.format(color)
            recipe = recipe + ' "parts":"{}"{}'.format(parts, '}')
        recipe = recipe + ']'
        if not (title and recipe):
            raise ValueError(
                'some information is missing, unable to create drink'
            )
        drink.title = title
        drink.recipe = recipe
        drink.update()
    except ValueError as value_error:
        print(value_error.with_traceback(value_error.__traceback__))
        abort(422)

    return jsonify({
        'success': True,
        'drink': drink.long()
    })


@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)

    drink.delete()
    return jsonify({
        'success': True,
        'deleted': drink_id
    })


# Error Handling

# error handling for unprocessable entity
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

# error handling for an entity that can't be found


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

# error handling for authorization errors


@app.errorhandler(AuthError)
def auth_failed(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error
    })
