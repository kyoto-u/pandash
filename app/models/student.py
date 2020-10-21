import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class Student(settings.Base):
    __tablename__ = 'students'
    StudentID = sqlalchemy.Column(String(40), primary_key=True)
    FullName = sqlalchemy.Column(String(40))

settings.Base.metadata.create_all(settings.engine)