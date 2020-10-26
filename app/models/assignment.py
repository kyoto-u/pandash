import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Assignment(settings.Base):
    __tablename__ = 'assignments'
    AssignmentID = Column(String(40), primary_key=True)
    AssignmentUrl = Column(String(500))
    Title = Column(String(100))
    Limit_at = Column(String(40))
    Instructions = Column(String(1000))
    Time_ms = Column(Integer())
    ModifiedDate = Column(sqlalchemy.BigInteger())

settings.Base.metadata.create_all(settings.engine)