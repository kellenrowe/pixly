""" Form to add a picture """

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
# from flask_uploads import UploadSet, IMAGES

# images = UploadSet('images', IMAGES)


class AddPictureForm(FlaskForm):
    """ Form to add a picture. """
    photographer = StringField("Name of Photographer",
                               validators=[InputRequired()])
    caption = StringField("Caption",
                          validators=[InputRequired()])
    picture = FileField("Chose a picture for upload",
                        validators=[FileRequired(),
                                    FileAllowed(
                                        ['jpg', 'png', 'svg', 'jpeg'],
                                        "Images Only")])
