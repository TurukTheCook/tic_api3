from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from functools import wraps
from datetime import datetime, timedelta
import jwt
import re

# personal imports
from models import User, UserSchema, Token
from app import app, db, flask_bcrypt

# token decorators
# 1st blocks workflow and return error if no token of wrong token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-token')

        if token is None:
            return jsonify({
                'message': 'Unauthorized',
            }), 401

        try: 
            decoded = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id = decoded['id']).first()
        except:
            return jsonify({
                'message': 'Unauthorized',
            }), 401

        return f(current_user, *args, **kwargs)

    return decorated

# 2nd return no error on missing token 
def token_optional(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-token')

        if token is None:
            current_user = None
            return f(current_user, *args, **kwargs)

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id = data['id']).first()
        except:
            return jsonify({
                'message': 'Unauthorized',
            }), 401

        return f(current_user, *args, **kwargs)

    return decorated

#######################################
### STARTING TO DEFINE ROUTES HERE ####
#######################################
users_api = Blueprint('users_api', __name__)

# auth
@users_api.route('/auth', methods=['POST'])
def auth():
    data = request.get_json() or request.form
    login = data.get('login')
    password = data.get('password')

    pattern = re.compile(r'[a-zA-Z0-9_-]*')
    
    if (
        login is None or type(login) is not str or
        password is None or type(password) is not str
        ):
        return jsonify({
            'message': 'Bad request',
            'code': 10001,
            'data': ''
        }), 400

    if pattern.fullmatch(login):
        user = User.query.filter_by(username = login).first()
    else:
        user = User.query.filter_by(email = login).first()

    if not user:
        return jsonify({
            'message': 'Not found',
        }), 404

    if flask_bcrypt.check_password_hash(user.password, password):
        token = jwt.encode({'id': user.id}, app.config['SECRET_KEY']).decode('utf-8')

        return jsonify({
            'message': 'OK',
            'data' : token
        }), 200

    return jsonify({
        'message': 'Bad request',
        'code': 10010, # password doesn't match
        'data': ''
    }), 400

# get all users
@users_api.route('/users', methods=['GET'])
def getUsers():
    query_params = request.args
    page = query_params.get('page', type=int)
    perPage = query_params.get('perPage', type=int)

    paginate = User.query.paginate(page = page, per_page = perPage, error_out = False) # if error_out = False, page and perPage defauls to 1 & 20 respectivly
    users = paginate.items
    total = paginate.pages # total of pages for parameter perPage

    if not users:
        users = [] # possible options here: return empty array, or return 404 not found ? not sure

    schema = UserSchema(only=('id', 'username', 'pseudo', 'created_at'), many=True)
    output = schema.dump(users).data

    return jsonify({
        'message': 'OK',
        'data': output,
        'pager': {
            'current': page,
            'total': total
        }
    })

# get one user
@users_api.route('/user/<int:id>', methods=['GET'])
@token_optional
def getUser(current_user, id):
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({
            'message': 'Not found',
        }), 404

    if current_user is not None and current_user.id == user.id:
        schema = UserSchema(only=('id', 'username', 'pseudo', 'email', 'created_at', 'password'))
    else :
        schema = UserSchema(only=('id', 'username', 'pseudo', 'created_at'))

    output = schema.dump(user).data

    return jsonify({
        'message': 'OK',
        'data': output
    }), 200

# create a new user
@users_api.route('/user', methods=['POST'])
def createUser():
    data = request.get_json() or request.form
    username = data.get('username')
    pseudo = data.get('pseudo')
    email = data.get('email')
    password = data.get('password')

    pattern = re.compile(r'[a-zA-Z0-9_-]*')

    if (
        data is None or
        username is None or type(username) is not str or pattern.fullmatch(username) is None or
        pseudo and (type(pseudo) is not str or pattern.fullmatch(pseudo) is None) or
        email is None or type(email) is not str or
        password is None or type(password) is not str
        ):
        return jsonify({
            'message': 'Bad request',
            'code': 10001,
            'data': ''
        }), 400

    try:
        newUser = User(
            username = username,
            pseudo = pseudo or None,
            email = email,
            password = flask_bcrypt.generate_password_hash(password, rounds=10).decode('utf-8'),
            created_at = datetime.utcnow()
        )
        db.session.add(newUser)
        db.session.commit()
    except exc.IntegrityError as err:
        db.session.rollback()
        return jsonify({
            'message': 'Bad request',
            'data': err.args
        }), 400
    except Exception as err:
        db.session.rollback()
        return jsonify({
            'message': 'Internal server error',
            'data': err.args
        }), 500

    schema = UserSchema(only=('id', 'username', 'pseudo', 'email', 'created_at'))
    output = schema.dump(newUser).data

    return jsonify({
        'message': 'OK',
        'data': output
    }), 201

# delete a user
@users_api.route('/user/<int:id>', methods=['DELETE'])
@token_required
def deleteUser(current_user, id):
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({
            'message': 'Not found',
        }), 404

    if current_user.id != user.id:
        return jsonify({
            'message': 'Forbidden',
        }), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({}), 204

# modify a user
@users_api.route('/user/<int:id>', methods=['PUT'])
@token_required
def modifyUser(current_user, id):
    user = User.query.filter_by(id=id).first()

    if not user:
        return jsonify({
            'message': 'Not found',
        }), 404
    
    if current_user.id != user.id:
        return jsonify({
            'message': 'Forbidden',
        }), 403
    
    data = request.get_json() or request.form
    username = data.get('username')
    pseudo = data.get('pseudo')
    email = data.get('email')
    password = data.get('password')

    pattern = re.compile(r'[a-zA-Z0-9_-]*')

    if (
        data is None or
        username is None or type(username) is not str or pattern.fullmatch(username) is None or
        pseudo and (type(pseudo) is not str or pattern.fullmatch(pseudo) is None) or
        email is None or
        password is None
        ):
        return jsonify({
            'message': 'Bad request',
            'code': 10001,
            'data': ''
        }), 400

    try:
        user.username = username
        user.pseudo = pseudo or None
        user.email = email
        user.password = flask_bcrypt.generate_password_hash(password, rounds=10).decode('utf-8')
        db.session.commit()
    except exc.IntegrityError as err:
        db.session.rollback()
        return jsonify({
            'message': 'Bad request',
            'data': err.args
        }), 400
    except Exception as err:
        db.session.rollback()
        return jsonify({
            'message': 'Internal server error',
            'data': err.args
        }), 500

    schema = UserSchema(only=('id', 'username', 'pseudo', 'email', 'created_at'))
    output = schema.dump(user).data

    return jsonify({
        'message': 'OK',
        'data': output
    }), 201