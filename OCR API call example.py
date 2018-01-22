import argparse
import base64
import json
import sys
import requests
import config as cfg

# Your Google Cloud Vision API Key should be stored in a file called
#  config.py with the variable name googleCoudVisionAPIKey
api_key = cfg.googleCloudVisionAPIKey

def main(input_file):
    '''
    Translates the input file into a Google AnnotateImageRequest json object,
       makes a request to the API, and prints out the json response. This is taken from 
       Google documentation, and includes options for other non-OCR Vision API requests.

    Args:
        input_file: a file object, containing lines of input to convert.
    '''
    request_list = []
    input_data = open(input_file).readlines()
    for line in input_data:
        print(line)
        image_filename, features = line.lstrip().split(' ', 1)

        with open(image_filename, 'rb') as image_file:
            content_json_obj = {
                'content': base64.b64encode(image_file.read()).decode('UTF-8')
            }

        feature_json_obj = []
        for word in features.split(' '):
            feature, max_results = word.split(':', 1)
            feature_json_obj.append({
                'type': get_detection_type(feature),
                'maxResults': int(max_results),
            })

        request_list.append({
            'features': feature_json_obj,
            'image': content_json_obj,
        })
    
    full_request = json.dumps({'requests': request_list})
    response = requests.post(url='https://vision.googleapis.com/v1/images:annotate?key='+api_key, 
                             data=full_request, 
                             headers={'Content-Type': 'application/json'})

    with open('output.json', 'w', encoding='utf-8') as output_file:
        json.dump(response.text, output_file, ensure_ascii=True)
    
    json_response = response.json()
    words = json_response['responses'][0]['textAnnotations'][0]['description']
    print(words)

DETECTION_TYPES = [
    'TYPE_UNSPECIFIED',
    'FACE_DETECTION',
    'LANDMARK_DETECTION',
    'LOGO_DETECTION',
    'LABEL_DETECTION',
    'TEXT_DETECTION',
    'SAFE_SEARCH_DETECTION',
]

def get_detection_type(detect_num):
    """Return the Vision API symbol corresponding to the given number."""
    detect_num = int(detect_num)
    if 0 < detect_num < len(DETECTION_TYPES):
        return DETECTION_TYPES[detect_num]
    else:
        return DETECTION_TYPES[0]

if __name__ == '__main__':
    main('./input.txt')