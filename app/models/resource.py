import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Resource(settings.Base):
    __tablename__ = 'resources'
    # ResourceID = Column(Integer(), primary_key=True, autoincrement=True)
    resource_url = Column(String(727), primary_key=True)
    title = Column(String(400))
    container = Column(String(500))
    modifieddate = Column(sqlalchemy.BigInteger()) # milliseconds e.g. 1600000000000
    course_id = Column(String(40),index=True)

settings.Base.metadata.create_all(settings.engine)
