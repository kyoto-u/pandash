import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Comment(settings.Base):
    __tablename__ = 'comments'
    comment_id = Column(String(80), primary_key=True)
    student_id = Column(String(80))
    reply_to = Column(String(80))
    update_time = Column(Integer(80))
    content = Column(String(1000))

settings.Base.metadata.create_all(settings.engine)