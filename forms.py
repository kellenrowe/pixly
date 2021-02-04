""" Form to add a picture """

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
# from flask_uploads import UploadSet, IMAGES

# from werkzeug.utils import secure_filename
# images = UploadSet('images', IMAGES)


class UploadForm(FlaskForm):
    """ Form to add a picture. """
    photographer = StringField("Name of Photographer",
                               validators=[InputRequired()])
    caption = StringField("Caption",
                          validators=[InputRequired()])
                 
    photo = FileField("",
                      validators=[FileRequired()])
