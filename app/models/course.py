import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column

Base = sqlalchemy.ext.declarative.declarative_base()

class Course(Base):
    __tablename__ = 'courses'
    CourseID = Column(String, primary_key=True)
    InstructorID = Column(String)
    CourseName = Column(String)