from flask import Flask, request, abort, jsonify
import requests
import os
app = Flask(__name__)

file_name_counter = 0


@app.route('/')
def index():
    return 'Hello World'


@app.route('/Upload', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        if not request.files:
            abort(400)

        data = {"user_id": request.headers["user_id"],
                "room_id": request.headers["room_id"],
                "action": request.headers["action"]}

        print(data)
        image = request.files['file']
        image.save('C:\\Users\\kevin.muppattayil\\Documents', ('image_' + str(file_name_counter)))

    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    app.run()
