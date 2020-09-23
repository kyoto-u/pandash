from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
    'mysql://pandash:pandash@localhost/pandash00?charset=utf8')

Base = declarative_base()