from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from cas_client import CASClient

# このサービス自身のURL
app_url ='https://pandash.ecs.kyoto-u.ac.jp'
app_login_url = app_url + '/login'
app_logout_url = app_url + '/logout'
cas_url = 'https://cas.ecs.kyoto-u.ac.jp/cas'
proxy_url = app_url + '/pgtCallback'
proxy_callback = 'https://panda.ecs.kyoto-u.ac.jp/sakai-login-tool/container'
# PandAのAPI用URL
api_url = 'https://panda.ecs.kyoto-u.ac.jp/direct/'

# 収集する教科の学期一覧
# 前４ケタ:年度
# 最後の一桁: 0-> 前期  1-> 後期  2-> 集中・通年など  3-> どれも取得できなかった場合
VALID_YEAR_SEMESTER=[20201]

cas_client = CASClient(cas_url, auth_prefix='', proxy_url=proxy_url, proxy_callback=proxy_callback)

#engine = create_engine('mysql://pandash:pandash@localhost/pandash00?charset=utf8', echo=False)
engine = create_engine('mysql://root:9F#Mhyx3Zfxa@localhost/pandash?charset=utf8', echo=False)

session = orm.scoped_session(
    orm.sessionmaker(bind=engine)
)

Base = declarative_base()

