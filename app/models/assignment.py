import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column

Base = sqlalchemy.ext.declarative.declarative_base()

class Assignment(Base):
    __tablename__ = 'assignments'
    AssignmentID = Column(String, primary_key=True)
    AssignmentUrl = Column(String)
    Title = Column(String)
    Limit_at = Column(String)
    Instructions = Column(String)
    ClassSchedule = Column(String)