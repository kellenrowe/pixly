import os
from flask import Flask, request, redirect, jsonify, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import (db, connect_db, Picture)
from PIL import Image, ImageFilter, ExifTags
from PIL.ExifTags import TAGS
from forms import UploadForm
from werkzeug.utils import secure_filename

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

app.config['UPLOADED_IMAGES_DEST'] = "./images/"

####################### Routes ###########################


# @app.route("/images", methods=["GET"])
# def display_all_image():
#     """ Route for displaying all images """

#     pictures = Picture.query.all()

#     return


@app.route("/images/add", methods=["GET", "POST"])
def add_image():
    """ Route for uploading a new image """
    form = UploadForm()

    print("before validation", form.photo.data)
    print("before validation", form.caption.data)
    

    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        print("inside validation", filename)

        f.save(os.path.join(
            app.config['UPLOADED_IMAGES_DEST'], filename
        ))

        try:
            print("inside try", filename)
            image = Image.open(f'./images/{filename}')
        except IOError:
            pass
    
        exif = {}
        for tag, value in image._getexif().items():
            if tag in TAGS:
                exif[TAGS[tag]] = value
        

        print("heree", type(exif["ExifImageWidth"]))

        picture = Picture(
            photographer=form.photographer.data,
            caption=form.caption.data,
            date_time=exif["DateTime"],
            camera_make=exif["Make"],
            camera_model=exif["Model"],
            # shutter_speed=exif["ShutterSpeedValue"],
            # aperture=exif["ApertureValue"],
            iso=exif["ISOSpeedRatings"],
            flash=exif["Flash"],
            pic_width=exif["ExifImageWidth"],
            pic_height=exif["ExifImageHeight"],
            # location=exif[""],
    )

        db.session.add(picture)
        db.session.commit()

        print("return redirect")
        #need to grab id
        return redirect(f'/images')
        # return redirect(f'/images/{id}')

    else:
        print("return render template")
        return render_template("add_picture.html", form=form)


# @app.route("/images/<int:id>", methods=["POST"])
# def edit_image():
#     """ Route for edit an image """

