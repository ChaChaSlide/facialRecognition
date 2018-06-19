from flask import Flask, request, abort, jsonify, send_from_directory, url_for
import os
from google.cloud import storage
import karios_interface
from mongo_dal import MongoDAO

app = Flask(__name__)

CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']


@app.route('/')
def index():
    return 'Hello World'


@app.route('/Upload', methods=['POST'])
def upload():
    """ Stores and serves image, then registers user or checks credentials.
        Request--
            Headers--
                room_id-- required,
                    if action == 'recognize': room to with access is requested
                    if action == 'enroll': comma separated list of rooms
                action-- required, either 'recognize' or 'enroll'
                name-- optional for enroll, name to be enrolled defaults None
                user_id-- required for enroll, the identifying id of the new user
            Body-- the image file tags as 'file'

        Response JSON--
            status-- if the action was successful
                enroll will return failed on failed enrollment
                recognize is return failed if not in gallery or database
                success otherwise
            message-- informational message
            access-- 'Granted'  or 'Denied'
            name-- the name in the database or null
    """
    if not request.files:
        abort(406, 'no file sent')
    if 'room_id' not in request.headers or 'action' not in request.headers:
        abort(406, 'invalid headers')

    repo = MongoDAO()

    image = request.files['file']
    filename = 'image_' + str(repo.get_file_counter()) + '.' + image.filename.rsplit('.', 1)[1].lower()

    gcs = storage.Client()
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(filename)
    blob.upload_from_file(image)

    response_json = {}
    if request.headers['action'].lower() == 'enroll':
        if 'user_id' not in request.headers:
            abort(406, 'invalid headers')

        room_list = str(request.headers['room_id']).split(',')
        room_list = [room.strip() for room in room_list]

        if not repo.find_user(request.headers['user_id']):
            if karios_interface.enroll(blob.public_url, request.headers['user_id']):
                if 'name' in request.headers:
                    repo.add_user(request.headers['user_id'], room_list, name=request.headers['name'])
                else:
                    repo.add_user(request.headers['user_id'], room_list)
                response_json = {'status': 'success'}
        else:
            response_json = {'status': 'failed', 'message': 'user_id already exists'}

    elif request.headers['action'].lower() == 'recognize':
        confidences = karios_interface.recognize(blob.public_url)
        if not confidences:
            response_json = {'status': 'failed', 'message': 'not recognized'}
        else:
            user = repo.find_user(confidences[0][0])
            if not user:
                response_json = {'status': 'failed', 'message': 'not in database'}

            elif request.headers['room_id'] in user['access_areas']:
                response_json = {'status': 'success', 'access': 'granted', 'username': user['name']}

            else:
                response_json = {'status': 'success', 'access': 'denied', 'username': user['name']}
    else:
        abort(406)

    blob.delete()

    return jsonify(response_json), 200


@app.route('/RemoveAll', methods=['DELETE'])
def remove_all_users():
    """ Removes all subjects from kairos gallery"""
    repo = MongoDAO()
    if karios_interface.remove_gallery():
        repo.remove_all()
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'failed'}), 200


@app.route('/Remove/<user_id>', methods=['DELETE'])
def remove_user(user_id):
    """ Removes specified user from kairos gallery
        user_id -- in query string as the subject_id in gallery
    """
    repo = MongoDAO()
    if not repo.find_user(user_id):
        abort(404, 'user id not found in database')
    if karios_interface.remove_subject(user_id):
        repo.remove_user(user_id)
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'failed'}), 200


if __name__ == '__main__':
    app.run()
