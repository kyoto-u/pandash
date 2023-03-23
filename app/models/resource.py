import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column,Text
from .. import settings

class Resource(settings.Base):
    __tablename__ = 'resources'
    # ResourceID = Column(Integer(), primary_key=True, autoincrement=True)
    primary_id = sqlalchemy.Column(Integer, primary_key=True , autoincrement=True)
    resource_url = Column(Text())
    title = Column(Text())
    container = Column(Text())
    modifieddate = Column(sqlalchemy.BigInteger()) # milliseconds e.g. 1600000000000
    course_id = Column(String(40),index=True)
    deleted = Column(Integer(),default=0)

settings.Base.metadata.create_all(settings.engine)
