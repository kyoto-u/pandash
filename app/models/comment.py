import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from sqlalchemy_utils import UUIDType
from .. import settings
import uuid

class Comment(settings.Base):
    __tablename__ = 'comments'
    comment_id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    student_id = Column(String(80))
    reply_to = Column(String(80))
    update_time = Column(Integer())
    content = Column(String(1000))

settings.Base.metadata.create_all(settings.engine)