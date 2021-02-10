  
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class Student_Assignment(settings.Base):
    __tablename__ = 'studentassignments'
    sa_id = sqlalchemy.Column(String(120), primary_key=True)
    assignment_id = sqlalchemy.Column(String(80))
    course_id = sqlalchemy.Column(String(80))
    student_id = sqlalchemy.Column(String(40),index=True)
    status = sqlalchemy.Column(String(8))
    clicked = sqlalchemy.Column(Integer(), default=0)

settings.Base.metadata.create_all(settings.engine)