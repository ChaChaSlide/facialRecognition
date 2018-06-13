import requests
from flask import Flask, json

app = Flask(__name__)

api_url = "https://api.kairos.com"
app_id = "01d28598"
app_key = "d995adad6b5a3e0bd47a4dc3bcff5202"
gallery = "MyGallery"

headers = {
    'Content-Type': 'application/json',
    "app_id": app_id,
    "app_key": app_key
}

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/recognize')
def recognize(image_url):
    values = {
            'image': image_url,
            'gallery_name': gallery
        }
    request = requests.post('https://api.kairos.com/recognize', data=bytes(json.dumps(values), encoding="utf-8"), headers=headers)
    json_data = json.loads(request.text)
    resultList = []
    try:
        results = json_data['images'][0]
        count = 0
        resultID = []
        resultConfidence = []

        for i in results['candidates']:
           if results['candidates'][count]['confidence'] > .60:
                resultID.append(results['candidates'][0]['subject_id'])
                resultConfidence.append(results['candidates'][0]['confidence'])
           count+=1
        resultList = list(zip(resultID, resultConfidence))
    except KeyError:
        return resultList
    return resultList


@app.route('/enroll')
def enroll(image_url, subject_id):
    values = {
                "image": image_url,
                "subject_id": subject_id,
                "gallery_name": gallery
            }

    request = requests.post('https://api.kairos.com/enroll', data=bytes(json.dumps(values), encoding="utf-8"), headers=headers)
    response_body = json.loads(request.text)
    if len(response_body.keys()) > 1:
        return True
    else:
        return False;

enroll(image_url="http://media.kairos.com/kairos-lizabeth.jpg", subject_id="Elizabeth")
#recognize(image_url="https://storage.googleapis.com/infosys-facial-recognition/image_2.jpg")
if __name__ == '__main__':
    app.run()