from flask import Flask, request, abort, jsonify, send_from_directory, url_for
app = Flask(__name__)

file_name_counter = 0


@app.route('/')
def index():
    return 'Hello World'


@app.route('/Upload', methods=['GET', 'POST'])
def upload():
    if not request.files or not request.headers["user_id"] or not request.headers["room_id"] or not request.headers["action"]:
        abort(400)

    data = {"user_id": request.headers["user_id"],
            "room_id": request.headers["room_id"],
            "action": request.headers["action"]}

    image = request.files['file']
    global file_name_counter
    filename = 'image_' + str(file_name_counter) + '.' + image.filename.rsplit('.', 1)[1].lower()
    file_name_counter += 1
    image.save('static\\' + filename)

    data["image_id"] = url_for('hosted_image', image_id=filename)
    print(data)
    return jsonify({'status': 'success', 'image_id': filename}), 200


@app.route('/images/<image_id>')
def hosted_image(image_id):
    return send_from_directory('static/', image_id), 200


if __name__ == '__main__':
    app.run()
