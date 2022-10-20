import sqlalchemy
from sqlalchemy import column, sql
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from sqlalchemy.sql.sqltypes import Boolean
from .. import settings

class Forum(settings.Base):
    __tablename__ = 'forums'
    forum_id = Column(Integer, primary_key=True , autoincrement=True)
    student_id = Column(String(40))
    title = Column(String(200))
    contents = Column(String(1000))

    createdate = Column(sqlalchemy.BigInteger())

    replied_student_id = Column(String(40))
    reply_contents = Column(String(1000))
    replied = Column(Integer, default=0)

    name = Column(String(40))
    email = Column(String(100))

    reply_checked =Column(Integer, default=0)


settings.Base.metadata.create_all(settings.engine)