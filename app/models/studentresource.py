  
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class Student_Resource(settings.Base):
    __tablename__ = 'studentresources'
    sr_id = sqlalchemy.Column(String(540), primary_key=True)
    resource_url = sqlalchemy.Column(String(500))
    student_id = sqlalchemy.Column(String(40),index=True)
    status = sqlalchemy.Column(Integer())

settings.Base.metadata.create_all(settings.engine)