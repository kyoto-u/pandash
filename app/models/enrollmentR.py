  
import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String
from .. import settings

class EnrollmentR(settings.Base):
    __tablename__ = 'enrollmentRs'
    enrollment_r_url = sqlalchemy.Column(Integer(), primary_key=True, autoincrement=True)
    resourse_url = sqlalchemy.Column(String(500))
    student_id = sqlalchemy.Column(String(40))
    status = sqlalchemy.Column(String(8))

settings.Base.metadata.create_all(settings.engine)