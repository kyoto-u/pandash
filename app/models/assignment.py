import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Assignment(settings.Base):
    __tablename__ = 'assignments'
    AssignmentID = Column(String, primary_key=True)
    AssignmentUrl = Column(String)
    Title = Column(String)
    Limit_at = Column(String)
    Instructions = Column(String)
    ClassSchedule = Column(String)