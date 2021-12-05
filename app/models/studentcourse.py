import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class Studentcourse(settings.Base):
    __tablename__ = 'studentcourses'
    sc_id = sqlalchemy.Column(String(80), primary_key=True)
    student_id = sqlalchemy.Column(String(40),index=True)
    course_id = sqlalchemy.Column(String(40))
    hide = sqlalchemy.Column(Integer(),default=0)
    deleted = sqlalchemy.Column(Integer(),default=0)

settings.Base.metadata.create_all(settings.engine)