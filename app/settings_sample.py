from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from cas_client import CASClient

# このサービス自身のURL
app_url = "http://myapp.com"
# CASサーバのurl
cas_url = "https://panda.ecs.kyoto-u.ac.jp/cas"
proxy_callback = "https://panda.ecs.kyoto-u.ac.jp/sakai-login-tool/container"
# PandAのurl
panda_url = "https://panda.ecs.kyoto-u.ac.jp"
# kulasisのurl(今は利用していない)
kulasis_api_url = ""

app_login_url = app_url + "/login"
app_logout_url = app_url + "/logout"

# 収集する教科の学期一覧(現在はyear_semester.jsonに移動したため利用されていない)
# 前４ケタ:年度
# 最後の一桁: 0-> 前期 1->　前期集中 2-> 後期　3 -> 後期集中　4 -> 通年  5 -> 通年集中  9-> どれも取得できなかった場合
VALID_YEAR_SEMESTER = [
    10009,
    20210,
    20211,
    20212,
    20213,
    20214,
    20215,
    20219,
    20220,
    20221,
    20222,
    20223,
    20224,
    20225,
    20229,
    20230,
    20231,
    20232,
    20233,
    20234,
    20235,
    20239,
]

# デフォルトで表示する教科の学期一覧
# 前４ケタ:年度
# 最後の一桁: 0-> 前期  1->　前期集中 2-> 後期　3 -> 後期集中　4 -> 通年  5 -> 通年集中  9-> どれも取得できなかった場合
SHOW_YEAR_SEMESTER = [
    10009,
    20220,
    20221,
    20222,
    20223,
    20224,
    20225,
    20234,
    20235,
    20229,
    20239,
]

# pgtを受け取る場所
proxy_url = app_url + "/pgtCallback"
# PandAのAPI用URL
api_url = f"{panda_url}/direct"

# cas_clientのインスタンス
cas_client = CASClient(
    cas_url, auth_prefix="", proxy_url=proxy_url, proxy_callback=proxy_callback
)

# mysql接続に利用するユーザー名
mysql_user = "root"
# mysql接続に利用するパスワード
mysql_password = "password"
# mysql接続のホスト
mysql_host = "localhost"
# データベース名
mysql_database = "pandash"

engine = create_engine(
    f"mysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}?charset=utf8",
    echo=False,
)

session = orm.scoped_session(
    orm.sessionmaker(bind=engine, autoflush=True, autocommit=False)
)

Base = declarative_base()
