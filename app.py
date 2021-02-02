import os
from flask import Flask, request, redirect, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import (db, connect_db, Picture)
from PIL import Image, ImageFilter, ExifTags
from PIL.ExifTags import TAGS
# from forms import (ImageAddForm)

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///pixly'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


####################### Routes ###########################


@app.route("/images", methods=["GET"])
def display_all_image():
    """ Route for displaying all images """
   
    return 


@app.route("/images/add", methods=["POST"])
def add_image():
    """ Route for uploading a new image """

    # Opening and getting exif data from image
    try:
        image = Image.open("test.jpeg")
    except IOError:
        pass
    
    exif = {}
    for tag, value in image._getexif().items():
        if tag in TAGS:
            exif[TAGS[tag]] = value



@app.route("/images/<int:id>", methods=["POST"])
def edit_image():
    """ Route for edit an image """

