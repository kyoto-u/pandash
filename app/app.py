import flask
from .models import student, assignment, course, enrollment,instructor


def create_app():
    app=flask.Flask(__name__)
    return app




app = create_app()

