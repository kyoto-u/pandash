  
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class Student_Quiz(settings.Base):
    __tablename__ = 'studentquizzes'
    sq_id = sqlalchemy.Column(String(120), primary_key=True)
    quiz_id = sqlalchemy.Column(String(80))
    course_id = sqlalchemy.Column(String(80))
    student_id = sqlalchemy.Column(String(40),index=True)
    status = sqlalchemy.Column(String(8))
    clicked = sqlalchemy.Column(Integer(), default=0)
    deleted = sqlalchemy.Column(Integer(), default=0)

settings.Base.metadata.create_all(settings.engine)
