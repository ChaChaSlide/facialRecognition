from urllib.request import Request, urlopen
from flask import Flask, render_template, request, json
app = Flask(__name__)

api_url = "https://api.kairos.com"
app_id = " 01d28598"
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

    request = Request('https://api.kairos.com/recognize', data=bytes(json.dumps(values), encoding="utf-8"), headers=headers)
    response_body = urlopen(request).read()
    result = response_body.decode("utf-8")
    confidence = result.split(",")
    list = []
    for i in range(len(confidence)):
        string = str(confidence[i])
        if string.find("confidence") == -1:
            pass
        else:
            s2 = string.split(":")
            if i == 0:
                s2.pop(0)
                s2.pop(0)
            if string.find("transaction") == 1:
                s2.pop(0)
            if float(s2[1]) >= .60:
                list.append(s2)
        if string.find("subject_id") == -1:
            pass
        else:
            list.append(string)
    print(list)
    return(list);

@app.route('/enroll')
def enroll(image_url, subject_id):
    values = {
                "image": image_url,
                "subject_id": subject_id,
                "gallery_name": gallery
            }

    request = Request('https://api.kairos.com/enroll', data=bytes(json.dumps(values), encoding="utf-8"), headers=headers)
    response_body = urlopen(request).read()
    print(response_body)
    return(response_body);


#enroll(image_url="http://media.kairos.com/kairos-elizabeth.jpg", subject_id="Elizabeth")
recognize(image_url="http://media.kairos.com/kairos-elizabeth.jpg")
if __name__ == '__main__':
    app.run()

