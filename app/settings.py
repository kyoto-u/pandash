from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine(
#     'mysql://pandash:pandash@localhost/pandash00?charset=utf8', echo=False)

engine = create_engine(
    'mysql://root:9F#Mhyx3Zfxa@localhost/pandash?charset=utf8', echo=False)

session = orm.scoped_session(
    orm.sessionmaker(bind=engine)
)

Base = declarative_base()

