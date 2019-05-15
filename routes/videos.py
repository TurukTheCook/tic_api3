from flask import Blueprint, jsonify, request
from werkzeug import secure_filename
from sqlalchemy import exc
from datetime import datetime, timedelta
import magic
import re

# personal imports
from models import User, UserSchema, Video, Video_Format, VideoSchema, VideoFormatSchema
from app import app, db
from routes.auth import token_optional, token_required

#######################################
### STARTING TO DEFINE ROUTES HERE ####
#######################################
videos_api = Blueprint('videos_api', __name__)

# get all videos
@videos_api.route('/videos', methods=['GET'])
def getVideos():
    return ''

# get user's videos
@videos_api.route('/user/<int:userId>/videos', methods=['GET'])
def getUserVideos(userId):
    return ''

# create new video
@videos_api.route('/user/<int:userId>/video', methods=['POST'])
@token_required
def createVideo(current_user, userId):
    # TODO: request.file,  get mimetype, apply regex ^video to catch type video, etc..
    # see: http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
    # and: https://werkzeug.palletsprojects.com/en/0.14.x/datastructures/#werkzeug.datastructures.FileStorage
    # and: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
    ### user verif
    user = User.query.filter_by(id=userId).first()

    if not user:
        return jsonify({
            'message': 'User not found',
        }), 404
    
    if (current_user is None or current_user.id != user.id):
        return jsonify({
            'message': 'Forbidden',
        }), 403

    ### file form verif
    if ('source' not in request.files or
        request.files['source'].filename == ''):
        return jsonify({
            'message': 'Bad request',
            'code': 10020, # no file 
            'data': ''
        }), 400

    file = request.files['source']
    data = request.get_json() or request.form
    name = data.get('name')

    ### file mimetype check and save to storage
    pattern = re.compile(r'^video\/')
    file_mimetype = magic.from_buffer(file.read(1024), mime=True)

    if pattern.match(file_mimetype):
        file_path = secure_filename(user.username + '_' + str(datetime.utcnow()) + '_' + file.filename)
        file.save(app.config['UPLOAD_FOLDER'] + file_path)
    else:
        return jsonify({
            'message': 'Bad request',
            'code': 10021, # wrong file type
            'data': ''
        }), 400

    ## save to db
    try:
        newVideo = Video(
            name = name or secure_filename(file.filename),
            source = (app.config['UPLOAD_FOLDER'] + file_path),
            user_id = user.id,
            created_at = datetime.utcnow()
        )
        db.session.add(newVideo)
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

    schema = VideoSchema(only=('id', 'name', 'source', 'view', 'enabled', 'user', 'formats', 'created_at'))
    output = schema.dump(newVideo).data

    return jsonify({
        'message': 'OK',
        'data': output
    }), 201

# encoding video
@videos_api.route('/video/<int:videoId>', methods=['PATCH'])
def encodeVideo(videoId):
    return ''

# update video
@videos_api.route('/video/<int:videoId>', methods=['PUT'])
def updateVideo(videoId):
    return ''

# create a new video
@videos_api.route('/video/<int:videoId>', methods=['DELETE'])
def deleteVideo(videoId):
    return ''