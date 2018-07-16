import requests
from flask import Flask, json
import os

API_URL = os.environ['API_URL']
APP_ID = os.environ['APP_ID']
APP_KEY = os.environ['APP_KEY']
GALLERY_NAME = os.environ['GALLERY_NAME']
CONFIDENCE_LEVEL = os.environ['CONFIDENCE_LEVEL']
headers = {
    'Content-Type': 'application/json',
    "app_id": APP_ID,
    "app_key": APP_KEY
}
def recognize(image_url):
    """ Checks whether the face passed as argument is recognized in Gallery.

        :param image_url: Url to Server hosted image, to be sent to Kairos API.

        :returns List: List of candidates who have 60% confidence level.

    """
    values = {
            'image': image_url,
            'gallery_name': GALLERY_NAME
        }
    request = requests.post('https://api.kairos.com/recognize', data=bytes(json.dumps(values), encoding="utf-8"), headers=headers)
    json_data = json.loads(request.text)
    result_list = []
    results = json_data['images'][0]

    if not results['candidates']:
        return result_list
    for candidate in results['candidates']:
        if candidate['confidence'] > CONFIDENCE_LEVEL:
            result_list.append((candidate['subject_id'],candidate['confidence']))

    return result_list


def enroll(image_url, subject_id):
    ''' Enrolls new subjects into the gallery, using their face mapping and unique ID as identifiers.

        :param
            image_url (string): Url to Server hosted image, to be sent to Kairos API.
            subject_id (string): ID of subject to be enrolled into the gallery.

        :returns
            True/False: Dependant on whether the subject could be enrolled successfully or not.
    '''
    values = {
                "image": image_url,
                "subject_id": subject_id,
                "gallery_name": GALLERY_NAME
            }

    request = requests.post('https://api.kairos.com/enroll', data=bytes(json.dumps(values), encoding="utf-8"), headers=headers)
    response_body = json.loads(request.text)
    if len(response_body.keys()) > 1:
        return True
    else:
        return False;


def remove_subject(subject_id):
    ''' Removes subject from Gallery based on ID sent.

        :param subject_id: ID of subject to be removed form Gallery.

        :return: True on successful delete, False if subject could not be removed or ID was not found.
    '''
    values = {
                "subject_id": subject_id,
                "gallery_name": GALLERY_NAME
            }

    request = requests.post('https://api.kairos.com/gallery/remove_subject', data=bytes(json.dumps(values), encoding="utf-8"), headers=headers)
    response_body = json.loads(request.text)
    print(response_body.get('status'))
    if response_body.get('status') == 'Complete':
        return True
    else:
        return False


def remove_gallery():
    ''' Removes entire gallery of faces.

        :return: True if gallery is removed. False if it could not be removed, or if gallery could not be found.

    '''
    values = {
                "gallery_name": GALLERY_NAME
            }

    request = requests.post('https://api.kairos.com/gallery/remove', data=bytes(json.dumps(values), encoding="utf-8"), headers=headers)
    response_body = json.loads(request.text)
    if response_body.get('status') == 'Complete':
        return True
    else:
        return False
