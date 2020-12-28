from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from cas_client import CASClient

app_url ='https://pandash.ecs.kyoto-u.ac.jp'
app_login_url = 'https://pandash.ecs.kyoto-u.ac.jp/login'
cas_url = 'https://cas.ecs.kyoto-u.ac.jp/cas'
proxy_url = 'https://pandash.ecs.kyoto-u.ac.jp/pgtCallback'
proxy_callback = 'http://158.101.137.245/login/proxy'
# proxy ticketの取得
# 'https://cas.ecs.kyoto-u.ac.jp/cas/proxy?targetService=http://localhost/proxy&pgt=PGT-330-CSdUc5fCBz3g8KDDiSgO5osXfLMj9sRDAI0xDLg7jPn8gZaDqS'
cas_client = CASClient(cas_url, auth_prefix='', proxy_url=proxy_url, proxy_callback=proxy_callback)

engine = create_engine('mysql://pandash:pandash@localhost/pandash00?charset=utf8', echo=False)
#engine = create_engine('mysql://root:9F#Mhyx3Zfxa@localhost/pandash?charset=utf8', echo=False)

session = orm.scoped_session(
    orm.sessionmaker(bind=engine)
)

Base = declarative_base()

