import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column, DateTime
from sqlalchemy.sql.expression import true
from sqlalchemy.sql.sqltypes import BigInteger
from .. import settings
import datetime

class Access(settings.Base):
    __tablename__ = 'accesses'
    # lastdate
    access_month_at = Column(BigInteger(), primary_key=True)
    unique_users = Column(Integer(), default=0)
    total_users = Column(Integer(), default=0)


settings.Base.metadata.create_all(settings.engine)
