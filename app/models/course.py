import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Course(settings.Base):
    __tablename__ = 'courses'
    CourseID = Column(String(40), primary_key=True)
    InstructorID = Column(String(40))
    CourseName = Column(String(40))
    ClassSchedule = Column(String(40))

settings.Base.metadata.create_all(settings.engine)