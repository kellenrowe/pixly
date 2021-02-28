import boto3
import os
from flask import Flask, request, redirect, jsonify, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import (db, connect_db, Picture)
from PIL import Image, ImageFilter, ExifTags, ImageOps, ImageEnhance, ImageFile
from PIL.ExifTags import TAGS
from forms import UploadForm
from werkzeug.utils import secure_filename
import botocore

ACCESS_KEY_ID = os.environ["ACCESS_KEY_ID"]
SECRET_KEY = os.environ["SECRET_KEY"]
BUCKET = os.environ["BUCKET"]
IMAGE_URL = os.environ["IMAGE_URL"]

app = Flask(__name__, static_folder="./static")

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///pixly'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

ImageFile.LOAD_TRUNCATED_IMAGES = True

client = boto3.client('s3',
                      aws_access_key_id=ACCESS_KEY_ID,
                      aws_secret_access_key=SECRET_KEY)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

####################### Routes ###########################


@app.route("/", methods=["GET"])
def display_homepage():
    """ renders home page """

    return render_template("homepage.html")


@app.route("/images", methods=["GET"])
def display_all_image():
    """ renders page for displaying all images """

    # search function
    if request.args.get("search"):
        pictures = Picture.query.filter(db.or_(
            Picture.caption.ilike(
                f'%{request.args.get("search")}%'), Picture.photographer.ilike(
                f'%{request.args.get("search")}%'))).all()
    else:
        pictures = Picture.query.all()

    # format the url and append to an array
    picturesUrl = []
    for picture in pictures:
        picturesUrl.append({"url": f'{IMAGE_URL}{picture.id}',
                            "id": f'{picture.id}',
                            "photog": f'{picture.photographer}',
                            "caption": f'{picture.caption}'})

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
    """ Route for viewing and editing an image
        - determines if image has been downloaded already
            and if so, pulls from local folder to perform
            edits. Allows for non-destructive editing.
    """

    # if os.path.exists(f'./static/{id}.png'):
    #     # print('exists ******************* ')
    #     return render_template('edit_picture.html',
    #                            url=f'../static/{id}.png', id=id)

    # print('doesnt exist *********')
    return render_template('edit_picture.html', url=f'{IMAGE_URL}{id}', id=id)


# @app.route("/images/<id>/save", methods=["GET", "POST"])
# def edit_image_save(id):
    # """ Route for saving an edited image.
    #     - saves image to db and sends to s3
    #     - removes image copy from local folder
    # """

#     filename = f'./static/{id}.png'

#     currentPicObj = Picture.query.get_or_404(int(id))

#     picture = Picture(
#         photographer=currentPicObj.photographer,
#         caption=currentPicObj.caption,
#         date_time=currentPicObj.date_time,
#         camera_make=currentPicObj.camera_make,
#         camera_model=currentPicObj.camera_model,
#         iso=currentPicObj.iso,
#         flash=currentPicObj.flash,
#         pic_width=currentPicObj.pic_width,
#         pic_height=currentPicObj.pic_height,
#         # location=exif[""],
#         image_url=IMAGE_URL,
#         file_name=f'{id}.png',
#     )

#     db.session.add(picture)
#     db.session.commit()

#     upload_file_bucket = BUCKET
#     upload_file_key = str(picture.id)
#     client.upload_file(
#         filename,
#         upload_file_bucket,
#         upload_file_key,
#         ExtraArgs={'ACL': 'public-read'}
#     )

#     os.remove(filename)
#     os.remove(f'{id}.png')
#     # print('saved to aws')
#     return redirect(f'/images/{picture.id}')


# @app.route("/images/<id>/cancel", methods=["GET", "POST"])
# def edit_image_cancel(id):
    # """ Route for cancelling an images edits.
    #     - removes image copy from local folder
    #     - redirects to edit page with original image
    # """

#     filename = f'{id}.png'
#     os.remove(filename)
#     os.remove(f'./static/{filename}')
#     return redirect(f'/images/{id}')


@app.route("/images/<int:id>/<edit>", methods=["GET", "POST"])
def edit_image_edit(id, edit):
    """ route to complete edits
        - gets image from s3
        - completes edit
        - sends back to s3 (waiting for refactor of save and cancel routes)
    """

    filename = f'{id}.png'
    s3 = boto3.resource('s3',
                        aws_access_key_id=ACCESS_KEY_ID,
                        aws_secret_access_key=SECRET_KEY,
                        )

    # if not os.path.exists(f'./static/{filename}'):
        # Download the picture
    try:
        s3.Bucket(BUCKET).download_file(str(id), str(id))

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    os.rename(str(id), filename)
    image = Image.open(filename)
    # else:
    #     image = Image.open(f'./static/{filename}')
    #     # print("opening image from images")

    if edit == "grayscale":
        newImage = ImageOps.grayscale(image)

    if edit == "left":
        # print('edit left')
        newImage = image.rotate(90, expand=True)

    if edit == "right":
        newImage = image.rotate(-90, expand=True)

    if edit == "posterize":
        newImage = ImageOps.posterize(image, 5)

    if edit == "emboss":
        newImage = image.filter(ImageFilter.EMBOSS)

    if edit == "blur":
        newImage = image.filter(ImageFilter.GaussianBlur(radius=4))

    if edit == "color":
        enhance = ImageEnhance.Color(image)
        newImage = enhance.enhance(1.5)

    if edit == "contrast":
        enhance = ImageEnhance.Contrast(image)
        newImage = enhance.enhance(1.5)

    if edit == "brightness":
        enhance = ImageEnhance.Brightness(image)
        newImage = enhance.enhance(1.5)

    newImage.save(os.path.join(filename))
    upload_file_bucket = BUCKET
    upload_file_key = str(id)
    client.upload_file(
        filename,
        upload_file_bucket,
        upload_file_key,
        ExtraArgs={'ACL': 'public-read'}
    )
    os.remove(filename)
    return redirect(f'/images/{id}')
