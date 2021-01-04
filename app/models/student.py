import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class Student(settings.Base):
    __tablename__ = 'students'
    student_id = sqlalchemy.Column(String(40), primary_key=True, index = True)
    fullname = sqlalchemy.Column(String(40))
    last_update = sqlalchemy.Column(sqlalchemy.BigInteger())
    language = sqlalchemy.Column(String(40))

settings.Base.metadata.create_all(settings.engine)