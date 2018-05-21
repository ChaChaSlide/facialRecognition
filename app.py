from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello World everyone!'


if __name__ == '__main__':
    app.run()
