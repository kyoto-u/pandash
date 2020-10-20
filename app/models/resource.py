import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Resource(settings.Base):
    __tablename__ = 'resources'
    # ResourceID = Column(Integer(), primary_key=True, autoincrement=True)
    ResourceUrl = Column(String(100), primary_key=True)
    Title = Column(String(40))
    Container = Column(String(80))
    ModifiedDate = Column(sqlalchemy.BigInteger())

settings.Base.metadata.create_all(settings.engine)