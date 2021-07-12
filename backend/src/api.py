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
'''
@TODO implement endpoint DONE
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


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


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


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


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


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


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


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


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


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
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_failed(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error
    })


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
