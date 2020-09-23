import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Assignment(settings.Base):
    __tablename__ = 'assignments'
    AssignmentID = Column(String(40), primary_key=True)
    AssignmentUrl = Column(String(40))
    Title = Column(String(40))
    Limit_at = Column(String(40))
    Instructions = Column(String(40))
    ClassSchedule = Column(String(40))

settings.Base.metadata.create_all(settings.engine)