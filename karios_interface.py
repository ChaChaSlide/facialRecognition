import requests

api_url = "https://api.kairos.com"
app_id = "01d28598"
app_key = "d995adad6b5a3e0bd47a4dc3bcff5202"
gallery = "MyGallery"

headers = {
    'Content-Type': 'application/json',
    "app_id": app_id,
    "app_key": app_key
}


def recognize(image_url):
    values = {
            'image': image_url,
            'gallery_name': gallery
        }
    request = requests.post('https://api.kairos.com/recognize', data=bytes(json.dumps(values), encoding="utf-8"), headers=headers)
    json_data = json.loads(request.text)
    results = json_data['images'][0]
    count = 0
    resultList = []
    resultID = []
    resultConfidence = []
    #print(results['candidates'])
    for i in results['candidates']:
        if results['candidates'][count]['confidence'] > .60:
            resultID.append(results['candidates'][0]['subject_id'])
            resultConfidence.append(results['candidates'][0]['confidence'])
        count+=1
    resultList = list(zip(resultID,resultConfidence))
    print(resultList)
    return resultList;

def enroll(image_url, subject_id):
    values = {
                "image": image_url,
                "subject_id": subject_id,
                "gallery_name": gallery
            }

    request = Request('https://api.kairos.com/enroll', data=bytes(json.dumps(values), encoding="utf-8"), headers=headers)
    response_body = urlopen(request).read()
    print(response_body)
    return response_body;
