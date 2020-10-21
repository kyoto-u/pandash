import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Course(settings.Base):
    __tablename__ = 'courses'
    CourseID = Column(String(40), primary_key=True)
    InstructorID = Column(String(40))
    CourseName = Column(String(40))
    # 2020年前期：20200 2020年後期：20201
    YearSemester = Column(Integer())
    # mon1, wed2, ...   othe
    ClassSchedule = Column(String(4))

settings.Base.metadata.create_all(settings.engine)