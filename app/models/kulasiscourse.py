import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from sqlalchemy.sql.expression import column, true
from .. import settings

class Kulasiscourse(settings.Base):
    __tablename__ = 'kulasiscourses'
    # direct/courselink/_kcd={site_id}
    course_id = Column(String(80), index=True)
    lecture_no = Column(Integer(), primary_key=True, index=True)
    deparment_no = Column(Integer())

    # coursename
    lecture_name = Column(String(200))
    lecture_name_en = Column(String(200))

    lecture_week_schedule = Column(String(80))
    lecture_week_schedule_en = Column(String(80))

    instructor_name = Column(String(80))
    instructor_name_en = Column(String(80))

    syllabus_url = Column(String(500))

    yearsemester = Column(Integer()) # 2020年前期：20200 2020年後期：20201
    # classschedule = Column(String(4)) # mon1, wed2, ...   othe
    
settings.Base.metadata.create_all(settings.engine)