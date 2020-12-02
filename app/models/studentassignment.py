  
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class Student_Assignment(settings.Base):
    __tablename__ = 'studentassignments'
    sa_id = sqlalchemy.Column(Integer(), primary_key=True, autoincrement=True)
    assignment_id = sqlalchemy.Column(String(40))
    student_id = sqlalchemy.Column(String(40),index=True)
    status = sqlalchemy.Column(String(8))

settings.Base.metadata.create_all(settings.engine)