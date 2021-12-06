import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy import BigInteger, String, Column
from .. import settings

class Announcement(settings.Base):
    __tablename__ = 'announcements'
    announcement_id = Column(String(80), primary_key=True)
    title = Column(String(400)) # お知らせのタイトル
    body = Column(String(1000)) # お知らせの本文
    createddate = Column(BigInteger()) # お知らせの公開日時 (milliseconds) e.g. 1600000000000
    course_id = Column(String(40),index=True)

settings.Base.metadata.create_all(settings.engine)
