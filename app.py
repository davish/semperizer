import cognitive_face as CF
import requests
from io import BytesIO
from PIL import Image, ImageDraw
import boto3
import base64

from flask import Flask, request

def get_coords(faceDictionary):
    rect = faceDictionary['faceRectangle']
    mult = 1.5
    width = int(rect['width']*(mult))
    height = int(rect['height']*(mult))
    left = rect['left'] + int(rect['width']*(1-mult)/2) 
    top = rect['top'] + int(rect['height']*(1-mult)/2 - 10*mult)
    return (width, height), (left, top)

def getRectangle(faceDictionary):
    rect = faceDictionary['faceRectangle']
    left = rect['left']
    top = rect['top']
    bottom = left + rect['height']
    right = top + rect['width']
    return ((left, top), (bottom, right))


KEY = '6d4814cd80b241c786f4090f439590ef'  # Replace with a valid subscription key (keeping the quotes in place).
BASE_URL = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0'  # Replace with your regional Base URL

CF.Key.set(KEY)
CF.BaseUrl.set(BASE_URL)

# You can use this example JPG or replace the URL below with your own URL to a JPEG image.

def semperize(image_url):
	faces = CF.face.detect(image_url, attributes='gender')
	response = requests.get(image_url)
	img = Image.open(BytesIO(response.content))
	semp = Image.open('pic.png')

	draw = ImageDraw.Draw(img)
	for face in faces:
	    # draw.rectangle(getRectangle(face), outline='red')
	    if face['faceAttributes']['gender'] == 'male':
		    size, coords = get_coords(face)
		    i = semp.resize(size)
		    img.paste(i, coords, i)

	#Display the image in the users default image browser.
	buffered = BytesIO()
	img.save(buffered, format="PNG")
	return buffered



app = Flask(__name__)

@app.route('/')
def root():
	return app.send_static_file('index.html')

@app.route('/success')
def uploaded():
	url = 'https://s3.amazonaws.com/pkp-semperizer/' + request.args.get('key')
	img = semperize(url)
	img_str = base64.b64encode(img.getvalue())
	return '<img src="data:image/png;base64,' + str(img_str) + '">'