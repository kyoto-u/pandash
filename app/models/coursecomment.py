import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Course_Comment(settings.Base):
    __tablename__ = 'coursecomments'
    sa_id = Column(String(120), primary_key=True)
    comment_id = Column(String(80))
    course_id = Column(String(80))
    deleted = Column(Integer(), default=0)

settings.Base.metadata.create_all(settings.engine)