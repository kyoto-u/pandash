  
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Text
from .. import settings

class Student_Resource(settings.Base):
    __tablename__ = 'studentresources'
    primary_id = sqlalchemy.Column(Integer, primary_key=True , autoincrement=True)
    sr_id = sqlalchemy.Column(Text())
    resource_url = sqlalchemy.Column(Text())
    course_id = sqlalchemy.Column(String(80))
    student_id = sqlalchemy.Column(String(40),index=True)
    status = sqlalchemy.Column(Integer())
    deleted = sqlalchemy.Column(Integer(), default=0)

settings.Base.metadata.create_all(settings.engine)