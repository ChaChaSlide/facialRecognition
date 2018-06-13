from flask import Flask, request, abort, jsonify, send_from_directory, url_for
import os
from google.cloud import storage
import karios_interface

app = Flask(__name__)

CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']

file_name_counter = 0

database = {787468: {"access_areas": ['r45', 'c23', 'd5'], 'name': 'Kevin Muppattayil'}}


@app.route('/')
def index():
    return 'Hello World'


@app.route('/Upload', methods=['POST'])
def upload():
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

        if kairos_interface.enroll(blob.public_url):
            if 'name' in request.headers:
                database[request.headers['user_id']] = {'name': request.headers["name"],
                                                        'access_areas': room_list}
            else:
                database[request.headers['user_id']] = {'name': None,
                                                        'access_areas': room_list}
            response_json = {'status':'success'}
        else:
            response_json = {'status': 'failed'}

    elif request.headers["action"].lower() == 'recognize':
        confidences = karios_interface.recognize(blob.public_url)
        if not confidences or not confidences[0] in database:
            response_json = {'status': 'failed'}
        elif request.header['room_id'] in database[confidences[0][0]]['access_areas']:
            response_json = {'status': 'success', 'access': 'granted', 'username': database[confidences[0][0]]['name']}

        else:
            response_json = {'status': 'success', 'access': 'denied', 'username': database[confidences[0][0]]['name']}
    else:
        abort(406)

    return jsonify(response_json), 200


@app.route('/images/<image_id>')
def hosted_image(image_id):
    return send_from_directory('./static/', image_id), 200

if __name__ == '__main__':
    app.run()
