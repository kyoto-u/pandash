import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Forum(settings.Base):
    __tablename__ = 'forums'
    forum_id = Column(Integer, primary_key=True , autoincrement=True)
    student_id = Column(String(40))
    title = Column(String(200))
    contents = Column(String(1000))

settings.Base.metadata.create_all(settings.engine)