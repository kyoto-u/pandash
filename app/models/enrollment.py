  
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class enrollment(settings.Base):
    __tablename__ = 'enrollments'
    enrollmentID = sqlalchemy.Column(String(40), primary_key=True)
    assignmentID = sqlalchemy.Column(String(40))
    StudentID = sqlalchemy.Column(String(40))
    CourseID = sqlalchemy.Column(String(40))
    Status = sqlalchemy.Column(String(40))

settings.Base.metadata.create_all(settings.engine)