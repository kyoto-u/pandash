  
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class Student_Resource(settings.Base):
    __tablename__ = 'studentresources'
    sr_id = sqlalchemy.Column(String(767), primary_key=True)
    resource_url = sqlalchemy.Column(String(727))
    course_id = sqlalchemy.Column(String(80))
    student_id = sqlalchemy.Column(String(40),index=True)
    status = sqlalchemy.Column(Integer())
    deleted = sqlalchemy.Column(Integer(), default=0)

settings.Base.metadata.create_all(settings.engine)