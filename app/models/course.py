import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Course(settings.Base):
    __tablename__ = 'courses'
    CourseID = Column(String, primary_key=True)
    InstructorID = Column(String)
    CourseName = Column(String)