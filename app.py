from flask import Flask, request, abort, jsonify, send_from_directory, url_for
import os
app = Flask(__name__)

app.config['SERVER_NAME'] = 'infosys-facial-recognition.appspot.com'

file_name_counter = 0

database = {787468: {"access_areas": ['r45', 'c23', 'd5'], 'name': 'Kevin Muppattayil'}}


@app.route('/')
def index():
    return 'Hello World'


@app.route('/Upload', methods=['POST'])
def upload():
    if not request.files or not request.headers["room_id"] or not request.headers["action"]:
        abort(402)

    image = request.files['file']
    global file_name_counter
    filename = 'image_' + str(file_name_counter) + '.' + image.filename.rsplit('.', 1)[1].lower()
    file_name_counter += 1
    image.save('static\\' + filename)

    if request.headers["action"].lower() == 'enroll':
        if not request.headers["user_id"]:
            abort(402)
        print('http://' + app.config['SERVER_NAME'] + url_for('hosted_image', image_id=filename))
        global database
        if request.headers['name']:
            database[request.headers['user_id']] = {'name': request.headers["name"],
                                                    'access_areas': request.headers['room_id']}
        else:
            database[request.headers['user_id']] = {'name': None,
                                                    'access_areas': request.headers['room_id']}
        return jsonify({'status': 'success', 'user_id': request.headers['user_id']}), 200

    elif request.headers["action"].lower() == 'recognize':
        print('http://' + url_for('hosted_image', image_id=filename))
    else:
        abort(402)

    return jsonify({'status': 'success', 'image_id': filename}), 200


@app.route('/images/<image_id>')
def hosted_image(image_id):
    return send_from_directory('static/', image_id), 200


if __name__ == '__main__':
    app.run()
