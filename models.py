"""SQLAlchemy models for Pixly."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Picture(db.Model):
    """User in the system."""

    __tablename__ = 'pictures'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    shutter_speed = db.Column(
        db.Integer,
    )

    aperture = db.Column(
        db.Integer,
    )

    flash = db.Column(
        db.Integer,
    )

    date_time = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    pic_height = db.Column(
        db.Integer,
        nullable=False,
    )

    pic_length = db.Column(
        db.Integer,
        nullable=False,
    )

    location = db.Column(
        db.Text,
        nullable=False,
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


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
