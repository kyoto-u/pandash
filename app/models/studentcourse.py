import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class Studentcourse(settings.Base):
    __tablename__ = 'studentcourses'
    sc_id = sqlalchemy.Column(Integer(), primary_key=True, autoincrement=True)
    student_id = sqlalchemy.Column(String(40),index=True)
    course_id = sqlalchemy.Column(String(40))

settings.Base.metadata.create_all(settings.engine)