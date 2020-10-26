import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Assignment_attachment(settings.Base):
    __tablename__ = 'assignment_attachments'
    assignment_attachment_url = Column(String(500), primary_key=True)
    title = Column(String(100))
    assignment_id = Column(String(40))

settings.Base.metadata.create_all(settings.engine)