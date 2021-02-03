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
# 最後の一桁: 0-> 前期 1->　前期集中 2-> 後期　3 -> 後期集中　4 -> 通年  5 -> 通年集中  9-> どれも取得できなかった場合
VALID_YEAR_SEMESTER=[20200,20201,20202,20203,20204,20205,20209,20210,20211,20212,20213,20214,20215,20219]

# デフォルトで表示する教科の学期一覧
# 前４ケタ:年度
# 最後の一桁: 0-> 前期  1->　前期集中 2-> 後期　3 -> 後期集中　4 -> 通年  5 -> 通年集中  9-> どれも取得できなかった場合
SHOW_YEAR_SEMESTER =[20202,20203,20204,20205,20209]

cas_client = CASClient(cas_url, auth_prefix='', proxy_url=proxy_url, proxy_callback=proxy_callback)

#engine = create_engine('mysql://pandash:pandash@localhost/pandash00?charset=utf8', echo=False)
engine = create_engine('mysql://root:9F#Mhyx3Zfxa@localhost/pandash?charset=utf8', echo=False)

session = orm.scoped_session(
    orm.sessionmaker(bind=engine)
)

Base = declarative_base()

