"""SQLAlchemy models for Pixly."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)


class Picture(db.Model):
    """User in the system."""

    __tablename__ = 'pictures'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    shutter_speed = db.Column(
        db.Float,
    )

    aperture = db.Column(
        db.Float,
    )

    flash = db.Column(
        db.Integer,
    )

    date_time = db.Column(
        db.Text
    )

    pic_height = db.Column(
        db.Integer,
        nullable=False,
    )

    pic_width = db.Column(
        db.Integer,
        nullable=False,
    )

    location = db.Column(
        db.Text,
    )

    camera_make = db.Column(
        db.Text,
        nullable=False,
    )

    camera_model = db.Column(
        db.Text,
        nullable=False,
    )

    iso = db.Column(
        db.Integer,
    )

    photographer = db.Column(
        db.Text,
        nullable=False,
    )

    caption = db.Column(
        db.Text,
        nullable=False,
    )



