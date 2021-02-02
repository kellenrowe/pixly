import os
from flask import Flask, request, redirect
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


@app.route("/", methods=["POST", "GET"])
def show_form():
    """ VIEW FUNCTION DESCRIPTION """

    return render_template("conv_form.html")
