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
    # studentcourse table の更新が必要かどうか
    need_to_update_sitelist = sqlalchemy.Column(Integer(), default=0)
    show_already_due = sqlalchemy.Column(sqlalchemy.Integer(), default=1)

settings.Base.metadata.create_all(settings.engine)