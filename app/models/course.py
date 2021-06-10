import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Course(settings.Base):
    __tablename__ = 'courses'
    course_id = Column(String(80), primary_key=True,index=True)
    page_id = Column(String(80))
    instructor_id = Column(String(40))
    coursename = Column(String(800)) # コース名
    yearsemester = Column(Integer()) # 2020年前期：20200 2020年後期：20201
    classschedule = Column(String(4)) # mon1, wed2, ...   othe

settings.Base.metadata.create_all(settings.engine)
