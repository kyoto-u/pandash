import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String

Base = sqlalchemy.ext.declarative.declarative_base()

class Instructor(Base):
    __tablename__ = 'Instructors'
    InstructorID = sqlalchemy.Column(String, primary_key=True)
    FullName = sqlalchemy.Column(String(40))
    EmailAddress = sqlalchemy.Column(String)