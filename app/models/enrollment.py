  
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class Enrollment(settings.Base):
    __tablename__ = 'enrollments'
    enrollment_id = sqlalchemy.Column(Integer(), primary_key=True, autoincrement=True)
    assignment_id = sqlalchemy.Column(String(40))
    student_id = sqlalchemy.Column(String(40))
    status = sqlalchemy.Column(String(8))

settings.Base.metadata.create_all(settings.engine)