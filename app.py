import boto3
import os
from flask import Flask, request, redirect, jsonify, render_template
from flask_debugtoolbar import DebugToolbarExtension
# from flask_cors import CORS
from models import (db, connect_db, Picture)
from PIL import Image, ImageFilter, ExifTags, ImageOps
from PIL.ExifTags import TAGS
from forms import UploadForm
from werkzeug.utils import secure_filename
from secret import ACCESS_KEY_ID, SECRET_KEY, BUCKET, IMAGE_URL
import botocore


app = Flask(__name__)

# By default allows CORS for all domains and all routes
# CORS(app)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///pixly'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

# app.config['UPLOADED_IMAGES_DEST'] = "./images/"

client = boto3.client('s3',
                      aws_access_key_id=ACCESS_KEY_ID,
                      aws_secret_access_key=SECRET_KEY)


####################### Routes ###########################


@app.route("/", methods=["GET"])
def display_homepage():
    """ Route home page """

    return render_template("homepage.html")


@app.route("/images", methods=["GET"])
def display_all_image():
    """ Route for displaying all images """

    pictures = Picture.query.all()

    picturesUrl = []
    for picture in pictures:
        picturesUrl.append({"url": f'{IMAGE_URL}{picture.id}',
                            "id": f'{picture.id}'})

    return render_template("all_pictures.html", pictures=picturesUrl)


@app.route("/images/add", methods=["GET", "POST"])
def add_image():
    """ Route for uploading a new image """

    form = UploadForm()

    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)

        f.save(os.path.join(filename))

        image = Image.open(f'{filename}')

        exif = {}
        for tag, value in image._getexif().items():
            if tag in TAGS:
                exif[TAGS[tag]] = value

        picture = Picture(
            photographer=form.photographer.data,
            caption=form.caption.data,
            date_time=exif.get('DateTime'),
            camera_make=exif.get('Make'),
            camera_model=exif.get('Model'),
            iso=exif.get('ISOSpeedRatings'),
            flash=exif.get('Flash'),
            pic_width=exif.get('ExifImageWidth'),
            pic_height=exif.get('ExifImageHeight'),
            # location=exif[""],
            image_url=IMAGE_URL,
            file_name=filename
        )

        db.session.add(picture)
        db.session.commit()

# TODO: f is the entire image object and we can possibly use that instead of filename
        
        upload_file_bucket = BUCKET
        upload_file_key = picture.id
        client.upload_file(filename,
                           upload_file_bucket,
                           str(upload_file_key),
                           ExtraArgs={'ACL': 'public-read'})
        os.remove(filename)
        return redirect('/images')
    else:
        return render_template("add_picture.html", form=form)


@app.route("/images/<int:id>", methods=["GET"])
def edit_image(id):
    """ Route for viewing and editing an image """

    return render_template('edit_picture.html', url=f'{IMAGE_URL}{id}', id=id)


@app.route("/images/<id>/<edit>", methods=["GET", "POST"])
def edit_image_edit(id, edit):

    # Revert all edits
    if edit == "cancel":
        return redirect(f'/images/{id}')

    print("id here", id)
    filename = f'{id}.jpeg'

    # Save changes to AWS 
    if edit == "save":
        upload_file_bucket = BUCKET
        upload_file_key = id
        client.upload_file(
            filename,
            upload_file_bucket,
            upload_file_key,
            ExtraArgs={'ACL': 'public-read'}
        )

        os.remove(filename)
        return redirect(f'/images/{id}')

    picture = Picture.query.get_or_404(int(id))
    filename = picture.file_name
 
    s3 = boto3.resource('s3')

    if not os.path.exists(f'./{filename}'):
        # Download the picture
        try:
            s3.Bucket(BUCKET).download_file(id, id)

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise
        print("filenamern", filename)
        os.rename(id, filename)

    image = Image.open(filename)

    if edit == "grayscale":
        newImage = ImageOps.grayscale(image)
     
    if edit == "left":
        newImage = image.rotate(90, expand=True)
        
    if edit == "right":
        newImage = image.rotate(-90, expand=True)
   
    if edit == "posterize":
        newImage = ImageOps.posterize(image, 5)
       
    newImage.save(os.path.join(filename))

    return render_template('edit_picture.html',
                           url=f'/{filename}', 
                           id=id)
 

