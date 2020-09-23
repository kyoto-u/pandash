  
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String

Base = sqlalchemy.ext.declarative.declarative_base()

class enrollment(Base):
    __tablename__ = 'enrollments'
    enrollmentID = sqlalchemy.Column(String, primary_key=True)
    assignmentID = sqlalchemy.Column(String)
    StudentID = sqlalchemy.Column(String)
    CourseID = sqlalchemy.Column(String)
    Status = sqlalchemy.Column(String)