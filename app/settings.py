from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from cas_client import CASClient

app_login_url = 'http://127.0.0.1:5000/login'
cas_url = 'https://cas.ecs.kyoto-u.ac.jp/cas'
proxy_url = 'https://cas.ecs.kyoto-u.ac.jp/cas/proxy'
targetService = f'{app_login_url}/proxy'
cas_client = CASClient(cas_url, auth_prefix='', proxy_url=proxy_url, proxy_callback=targetService)

# engine = create_engine(
#     'mysql://pandash:pandash@localhost/pandash00?charset=utf8', echo=False)

engine = create_engine(
    'mysql://root:9F#Mhyx3Zfxa@localhost/pandash?charset=utf8', echo=False)

session = orm.scoped_session(
    orm.sessionmaker(bind=engine)
)

Base = declarative_base()

