import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String

Base = sqlalchemy.ext.declarative.declarative_base()

class Student(Base):
    __tablename__ = 'students'
    StudentID = sqlalchemy.Column(String, primary_key=True)
    FullName = sqlalchemy.Column(String(40))