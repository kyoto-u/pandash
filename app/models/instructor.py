import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class Instructor(settings.Base):
    __tablename__ = 'Instructors'
    InstructorID = sqlalchemy.Column(String, primary_key=True)
    FullName = sqlalchemy.Column(String(40))
    EmailAddress = sqlalchemy.Column(String)