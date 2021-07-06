import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import Integer, String, Column
from .. import settings

class Quiz(settings.Base):
    __tablename__ = 'quizzes'
    quiz_id = Column(String(80), primary_key=True)
    url = Column(String(500))
    title = Column(String(400)) # テスト・クイズのタイトル
    limit_at = Column(String(40)) # deadline e.g. 2021-01-01T00:00:00Z
    instructions = Column(String(1000))
    time_ms = Column(sqlalchemy.BigInteger()) # deadline (milliseconds) e.g. 1600000000000
    modifieddate = Column(sqlalchemy.BigInteger()) # 出題内容の最終修正日時 (milliseconds) e.g. 1600000000000
    course_id = Column(sqlalchemy.String(40),index=True)

settings.Base.metadata.create_all(settings.engine)
