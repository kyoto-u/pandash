import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Coursecomment(settings.Base):
    __tablename__ = 'coursecomments'
    comment_id = Column(String(80))
    course_id = Column(String(80))
    deleted = Column(Integer())

settings.Base.metadata.create_all(settings.engine)