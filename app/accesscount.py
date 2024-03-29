import sqlalchemy
from .models import student, access
from .settings import session
import datetime
import calendar, pytz
from sqlalchemy.dialects.mysql import insert

# def count_accesses(today):
#     """
#     today = datetime.datetime.today()
#     その月のユニークなアクセス数を取得
#     retrun st_cnt
#     """
#     firstdate = get_first_date(today) * 1000
#     lastdate = get_last_date(today) * 1000
#     st_cnt = session.query(student.Student).filter(sqlalchemy.and_(
#             student.Student.last_update>firstdate, student.Student.last_update<lastdate,
#         )).count()
#     return st_cnt

# def insert_accesses(today):
#     """
#     その月のアクセス数をデータベースに挿入
#     """
#     lastdate = int(get_last_date(today) * 1000)
#     st_cnt = count_accesses(today)
#     insert_stmt = insert(access.Access).values(access_month_at=lastdate, unique_users=st_cnt)

#     on_conflict_stmt = insert_stmt.on_duplicate_key_update(
#     unique_users=insert_stmt.inserted.unique_users)

#     session.execute(on_conflict_stmt)
#     session.commit()

#     return

def check_and_insert_all_accesses(student_id, today,db_ses):
    """
    最終ログイン日時とアクセス日時を比較してその月初めてのアクセスならunique_usersに+1
    上に関わらずtotal_usersに+1
    """
    this_month = today.month
    last_update = db_ses.query(student.Student.last_update).filter(
        student.Student.student_id==student_id).first()
    try:
        last_update_month = datetime.datetime.fromtimestamp(last_update[0]//1000).month
    except:
        last_update_month = 0
    # primary key
    last_date = get_last_date(today)
    accesslog = db_ses.query(access.Access).filter(
        access.Access.access_month_at==int(last_date*1000)).first()
    if accesslog == None:
        db_ses.add(access.Access(access_month_at=int(last_date*1000)))
        db_ses.commit()
        accesslog = accesslog = db_ses.query(access.Access).filter(
        access.Access.access_month_at==int(last_date*1000)).first()
    if this_month != last_update_month:
        accesslog.unique_users += 1
    accesslog.total_users += 1
    db_ses.commit()
    return  
    

def get_first_date(today):
    """
    return unix time (first day)
    """
    fd = today.replace(day=1)
    fd_native = datetime.datetime.combine(fd, datetime.time())
    return datetime.datetime.timestamp(pytz.timezone('Asia/Tokyo').localize(fd_native))

def get_last_date(today):
    """
    return unix time (last day)
    """
    ld = today.replace(day=calendar.monthrange(today.year,today.month)[1])
    ld_native = datetime.datetime.combine(ld, datetime.time(hour=23,minute=59,second=59))
    return datetime.datetime.timestamp(pytz.timezone('Asia/Tokyo').localize(ld_native))

def get_today(today):
    """
    return unix time (today)
    """
    td_native = datetime.datetime.combine(today, datetime.time())
    return datetime.datetime.timestamp(pytz.timezone('Asia/Tokyo').localize(td_native))

from dateutil.relativedelta import relativedelta
def get_access_logs(db_ses):
    dashboard = {"labels":{}, "unique_data":{}, "total_data":{}}
    now = datetime.datetime.now()
    last_dates = [get_last_date(now.date())]
    dashboard["labels"]["l_7"] = now.strftime('%Y年%m月')
    for i in range(6):
        l_i = now - relativedelta(months=(i+1))
        l_i_date = l_i.date()
        dashboard["labels"][f"l_{(6-i)}"] = l_i.strftime('%Y年%m月')
        last_dates.append(get_last_date(l_i_date))
    index = 0
    for last_date in last_dates:
        accesslog = db_ses.query(access.Access).filter(
                access.Access.access_month_at==int(last_date*1000)).first()
        try:
            dashboard["unique_data"][f"d_{(7-index)}"] = accesslog.unique_users
            dashboard["total_data"][f"d_{(7-index)}"] = accesslog.total_users
        except:
            # データがないとき
            dashboard["unique_data"][f"d_{(7-index)}"] = 0
            dashboard["total_data"][f"d_{(7-index)}"] = 0
        index += 1
    return dashboard