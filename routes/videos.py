from flask import Blueprint, jsonify, request
from sqlalchemy import exc
from datetime import datetime, timedelta
import re

# personal imports
from models import User, UserSchema, Video, Video_Format
from app import db
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
def createVideo(userId):
    # TODO: request.file,  get mimetype, apply regex ^video to catch type video, etc..
    # see: http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
    # and: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
    return ''

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