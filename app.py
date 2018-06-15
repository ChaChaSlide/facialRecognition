from flask import Flask, request, abort, jsonify, send_from_directory, url_for
import os
from google.cloud import storage
import karios_interface

app = Flask(__name__)

CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']

file_name_counter = 0

database = {'787468': {"access_areas": ['r45', 'c23', 'd5'], 'name': 'Kevin Muppattayil'}}


@app.route('/')
def index():
    return 'Hello World'


@app.route('/Upload', methods=['POST'])
def upload():
    """ Stores and serves image, then registers user or checks credentials.
        Request:
            Headers:
                room_id: required,
                    if action == 'recognize': room to with access is requested
                    if action == 'enroll': comma separated list of rooms
                action: required, either 'recognize' or 'enroll'
                name: optional for enroll, name to be enrolled defaults None
                user_id: required for enroll, the identifying id of the new user
            Body: the image file tags as 'file'

        Response JSON:
            status: if the action was successful
                enroll will return failed on failed enrollment
                recognize is return failed if not in gallery or database
                success otherwise
            message: informational message
            access: 'Granted'  or 'Denied'
            name: the name in the database or null
    """
    if not request.files:
        abort(406, 'no file sent')
    if not 'room_id' in request.headers or not 'action' in request.headers:
        abort(406, 'invalid headers')

    image = request.files['file']
    global file_name_counter
    filename = 'image_' + str(file_name_counter) + '.' + image.filename.rsplit('.', 1)[1].lower()
    file_name_counter += 1

    gcs = storage.Client()
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.blob(filename)
    blob.upload_from_file(image)

    response_json = {}
    if request.headers["action"].lower() == 'enroll':
        if not request.headers["user_id"]:
            abort(406, 'invalid headers')

        room_list = str(request.headers["room_id"]).split()
        global database

        if request.headers['user_id'] in database:
            response_json = {'status': 'failed', 'message': 'user_id already exists'}
        elif karios_interface.enroll(blob.public_url, request.headers['user_id']):
            if 'name' in request.headers:
                database[request.headers['user_id']] = {'name': request.headers["name"],
                                                        'access_areas': room_list}
            else:
                database[request.headers['user_id']] = {'name': None,
                                                        'access_areas': room_list}
            response_json = {'status': 'success'}
        else:
            response_json = {'status': 'failed'}

    elif request.headers["action"].lower() == 'recognize':
        confidences = karios_interface.recognize(blob.public_url)
        if not confidences:
            response_json = {'status': 'failed', 'message': 'not recognized'}
        elif not confidences[0][0] in database:
            response_json = {'status': 'failed', 'message': 'not in database'}

        elif request.headers['room_id'] in database[confidences[0][0]]['access_areas']:
            response_json = {'status': 'success', 'access': 'granted', 'username': database[confidences[0][0]]['name']}

        else:
            response_json = {'status': 'success', 'access': 'denied', 'username': database[confidences[0][0]]['name']}
    else:
        abort(406)

    return jsonify(response_json), 200


@app.route('/RemoveAll', methods=['DELETE'])
def remove_all_users():
    global database
    #if karios_interface.remove_all():
    database.clear()
    return jsonify({'status': 'success'}), 200


@app.route('remove/<user_id>', methods=['DELETE'])
def remove_user(user_id):
    global database
    if user_id not in database:
        abort(404, 'user id not found in database')
    #if karios_interface.remove(user_id):
    database.pop(user_id)
    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    app.run()
