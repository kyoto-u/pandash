# APIを用いて情報を取得する関数一覧
#

import asyncio, json
from math import *
from .settings import VALID_YEAR_SEMESTER, api_url, kulasis_api_url
import re
from .original_classes import Status
import functools

def get_announcement_from_api(announcements, student_id):
    announcement_list = []
    st_anouncement_list = []
    an_st_collection = announcements.get("announcement_collection")
    for announce in an_st_collection:
        announcement_id = announce.get('announcementId')
        title = announce.get('title')
        body = announce.get('body')
        createddate = announce.get('createdOn')
        course_id = announce.get('siteId')
        announcement_list.append({"sa_id":f"{student_id}:{announcement_id}","announcement_id":announcement_id,"title":title,"body":body,"createddate":createddate,"course_id":course_id}) 
        st_anouncement_list.append({"announcement_id":announcement_id,"course_id":course_id})
    announcement_dict = {"student_annoucement":st_anouncement_list, "annoouncements":announcement_list}
    return announcement_dict

def get_assignments_from_api(assignments, student_id):
    assignment_list = []
    sa_list = []
    as_colection = assignments.get("assignment_collection")
    for assignment in as_colection:
        assignment_id = assignment.get('id')
        url = assignment.get('entityURL')
        title = assignment.get('title')[:80]
        instructions = assignment.get('instructions')[:100]
        time_ms = assignment.get('dueTime').get('epochSecond')*1000 #millisecond
        limit_at = datetime.datetime.fromtimestamp(time_ms//1000,datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%SZ")
        course_id = assignment.get('context')
        modifieddate = assignment.get('timeLastModified').get('epochSecond')*1000 #millisecond
        status = assignment.get('status')
        sa_list.append({"sa_id":f"{student_id}:{assignment_id}","assignment_id":assignment_id,"course_id":course_id,"status":Status.NotYet.value,"student_id":student_id,"clicked":0})
        assignment_list.append({"assignment_id":assignment_id,"url":url,"title":title,"limit_at":limit_at,"instructions":instructions,"time_ms":time_ms,"modifieddate":modifieddate,"course_id":course_id})
    assignment_dict = {"student_assignments":sa_list, "assignments":assignment_list}
    return assignment_dict

def get_course_from_api(site, student_id):
    course_id = site.get('id')
    instructor_id="unknown"
    fullname="unknown"
    if site.get('siteOwner'):
        instructor_id = site.get('siteOwner').get('userId')
        fullname = site.get('siteOwner').get('userDisplayName')
    coursename = site.get('title')
    yearsemester = "10009"
    classschedule = "oth"
    try:
        yearsch = re.match(r'\[.*\]', coursename)
        semnum = "9"
        semester = yearsch.group()[5:7]
        classsch = yearsch.group()[7:9]
        if semester == '前期':
            semnum = "0"
        elif semester == '前集':
            semnum = "1"
        elif semester == '後期':
            semnum = "2"
        elif semester == '後集':
            semnum = "3"
        elif semester == '通年':
            semnum = "4"
        elif semester == '通集':
            semnum = "5"
        # else:
            # return None
        yearsemester = f"{yearsch.group()[1:5]}{semnum}"
        week = "oth"
        if classsch[0] == "月":
            week = "mon"
        elif classsch[0] == "火":
            week = "tue"
        elif classsch[0] == "水":
            week = "wed"
        elif classsch[0] == "木":
            week = "thu"
        elif classsch[0] == "金":
            week = "fri"
        classschedule = f"{week}{str(int(classsch[1]))}"
    except:
        # return None
        pass
    if int(yearsemester) not in VALID_YEAR_SEMESTER:
        return None
    course_dict = {"course_id":course_id,"instructior_id":instructor_id,"coursename":coursename,"yearsemester":yearsemester,"classschedule":classschedule,"page_id":"","announcement_page_id":""}
    student_course_dict = {"sc_id":f"{student_id}:{course_id}","course_id":course_id,"student_id":student_id}
    return {"course":course_dict, "student_course":student_course_dict}

def get_course_id_from_api(membership):
    mem_collection = membership.get('membership_collection')
    student_id = ""
    site_list = []
    for member in mem_collection:
        if student_id == "":
            student_id = member.get('userId')
        # roleがStudentでない場合はスルー
        if member.get('memberRole') != "Student":
            continue
        user_site_id = member.get('entityId')
        site_id = user_site_id.replace(f'{student_id}::site:','')
        site_list.append(site_id)
    return {"student_id":student_id, "site_list":site_list}

# get_course_id_from_api(membership) の代わり
def get_course_id_from_site_api(site, student_id):
    site_collection = site.get('site_collection')
    site_list = []
    for s in site_collection:
        if s.get('joinerRole') != "Student" and s.get('joinerRole') != None:
            continue
        user_site_id = s.get('id')
        site_id = user_site_id.replace(f'{student_id}::site:','')
        site_list.append(site_id)
    return {"student_id":student_id, "site_list":site_list}

def get_membership_json(ses):
    res = ses.get(f"{api_url}/membership.json", verify=True)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

# get_membership_json(ses) の代わり
def get_site_json(ses):
    res = ses.get(f"{api_url}/site.json?_limit=2000", verify=True)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {"site_collection": []}

def get_page_from_api(pages):
    page_id = ""
    announcement_page_id = ""
    for page in pages:
        title = page.get('title')
        if re.search('課題', title) or re.search('assignment', title):
            page_id = page.get('tools')[0].get('id')
        elif re.search('お知らせ', title) or re.search('announcement', title):
            announcement_page_id = page.get('tools')[0].get('id')
        if page_id != "" and announcement_page_id != "":
            break
    return {"page_id":page_id, "announcement_page_id":announcement_page_id}

def get_resources_from_api(resources, course_id, student_id):
    resource_list = []
    sr_list = []
    content_collection = resources.get("content_collection")
    for content in content_collection:
        file_type = content.get('type')
        if file_type == "collection":
            continue
        resource_author = content.get('author')
        resource_container = content.get('container')
        md = str(int(content.get('modifiedDate'))//1000)
        date_format = "%Y%m%d%H%M%S"
        resource_modified_date = int(datetime.datetime.strptime(md,date_format).timestamp()*1000) #millisecond
        resource_title = content.get('title')[:80]
        resource_url = content.get('url')
        container_split = resource_container.split('/')
        resource_list.append({'course_id':course_id, 'container': resource_container, 'title': resource_title, \
            'resource_url': resource_url, 'modifieddate': resource_modified_date})
        sr_list.append({"sr_id":f"{student_id}:{resource_url}", "resource_url":resource_url, "student_id":student_id, "course_id":course_id, "status":0})
    resource_dict = {"student_resources":sr_list, "resources":resource_list}
    return resource_dict

import datetime
def get_quizzes_from_api(quizzes, course_id, student_id):
    quiz_list = []
    sq_list = []
    quiz_collection = quizzes.get("sam_pub_collection")
    for content in quiz_collection:
        quiz_id = str(content.get('publishedAssessmentId'))
        # とりあえずsite_id
        url = content.get('ownerSiteId')
        title = content.get('entityTitle')
        time_ms = content.get('dueDate') # millisecond
        if time_ms==None:
            # 期限のないものは2099-12-31T23:59:59Zとなるよう設定
            time_ms=4102412399000				
        modifieddate = int(content.get('lastModifiedDate')) #millisecond
        limit_at = datetime.datetime.fromtimestamp(time_ms//1000,datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%dT%H:%M:%SZ")
        quiz_list.append({'course_id':course_id, 'quiz_id': quiz_id, 'url':url, 'title': title, \
            'limit_at':limit_at, 'time_ms': time_ms, 'modifieddate': modifieddate, 'instructions':''})
        sq_list.append({"sq_id":f"{student_id}:{quiz_id}", "quiz_id":quiz_id, "student_id":student_id, "course_id":course_id, "status":Status.NotYet.value,"clicked":0})
    quiz_dict = {"student_quizzes":sq_list, "quizzes":quiz_list}
    return quiz_dict

def get_student_id_from_api(membership):
    mem_collection = membership.get('membership_collection')
    student_id = ""
    for member in mem_collection:
        student_id = member.get('userId')
        break
    return student_id

def get_user_info_from_api(user):
    fullname = user.get('displayName')
    student_id = user.get('id')
    return {"student_id":student_id,"fullname":fullname}

def get_user_json(ses):
    res = ses.get(f"{api_url}/user/current.json", verify=True)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

def get_session_json(ses):
    res = ses.get(f"{api_url}/session/current.json", verify=True)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

#async
async def async_get_announcement(ses):
    url = f"{api_url}/announcement/user.json?n=2000"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {'announcement_collection':[]}

async def async_get_assignments(ses):
    url = f"{api_url}/assignment/my.json"
    func = functools.partial(ses.get, url, verify=True)
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, func)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

async def async_get_content(site_id, ses):
    url = f"{api_url}/content/site/{site_id}.json"
    func = functools.partial(ses.get, url, verify=True)
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, func)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {'content_collection':[]}

async def async_get_quiz(site_id, ses):
    url = f"{api_url}/sam_pub/context/{site_id}.json"
    func = functools.partial(ses.get, url, verify=True)
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, func)
    if res.status_code == 403:
        # 恐らく履修解除等によりアクセスが出来なくなった
        return {'sam_pub_collection':[]}
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {'sam_pub_collection':[]}

async def async_get_site(site_id, ses):
    url = f"{api_url}/site/{site_id}.json"
    func = functools.partial(ses.get, url, verify=True)
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, func)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {'id':site_id}

async def async_get_site_pages(site_id, ses):
    url = f"{api_url}/site/{site_id}/pages.json"
    func = functools.partial(ses.get, url, verify=True)
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, func)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

async def async_get_user_info(ses):
    url = f"{api_url}/user/current.json"
    func = functools.partial(ses.get, url, verify=True)
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, func)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}



# kulasis api  param=kulasis_login_get_api_keys()
# site_list {lecture_no: , department_no}
def get_kulasis_lecture_and_department_no_from_timetable_api(timetable, studentid):
    timetables = timetable.get('timetables')
    site_list = []
    for sub in timetables:
        lecture_no = sub.get('lectureNo')
        department_no = sub.get('departmentNo')
        site_list.append({'lectureNo':lecture_no, 'department_no':department_no})
    return {"studentid":studentid, "site_list":site_list}


def get_timetable(ses, param):
    """
    時間割の取得
    {
        "showWhichSemester": 前期:"first" or 後期:"second",
        "timetables":[
            {
                "departmentMinimalName":"学部の略称",
                "departmentMinimalNameEn":"学部名の略称 (英語)",
                "departmentName":"学部名",
                "departmentNameEn":"学部名 (英語)",
                "departmentNo":"学部の番号 (Number として格納されている)",
                "isLa": "全学共通科目かどうか (bool)",
                "isNew": "KULASIS の時間割に NEW があるかどうか (bool)",
                "isShownOnKouki": "後期の時間割に表示されているか (bool)",
                "isShownOnZenki": "前期の時間割に表示されているか (bool)",
                "isSyutyuSemester": "集中講義かどうか (bool)",
                "lectureName":"講義の名称",
                "lectureNameEn":"講義の名称 (英語)",
                "lectureNo": "講義の番号 (Number)",
                "lectureWeekSchedule":"講義の曜時限 (複数あるときには 月1, 月2 のようにカンマで区切られる。)",
                "lectureWeekScheduleEn":"講義の曜時限 (英語、複数あるときのはカンマ区切り。)",
                "newFamily": (不明),
                "newFamilyEn": (不明),
                "periodNo": "何時限目か (Number, 1-5)",
                "roomName":"講義の教室名",
                "roomNameEn":"講義の教室名 (英語)",
                "semester":"前期か後期か",
                "semesterEn":"前期か後期か (英語)",
                "shortTeacherName":"担当教員 (省略形 ?)",
                "shortTeacherNameEn":"担当教員 (省略形 ? 英語)",
                "targetDiscipline":"対象学科",
                "targetDisciplineEn":"対象学科 (英語)",
                "teacherName":"担当教員",
                "teacherNameEn":"担当教員 (英語)",
                "weekdayNo": "曜日 (月曜から順に 1) (Number)"
            }
        ]
    }
    """
    res = ses.get(f"{kulasis_api_url}/timetable/get_table", params=param)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

async def get_lecture_detail(ses, param, departmentNo, lectureNo):
    """
    講義の詳細情報の取得
    {
        "departmentMinimalName":"学部名",
        "departmentMinimalNameEn":"学部名 (英語)",
        "departmentNo": "学部の番号 (Number)",
        "isCourseMailChanged": "新しい授業連絡メールがあるかどうか (bool)",
        "isLa": "全学共通科目かどうか ? (bool)",
        "isLectureMaterialChanged": "新しい講義資料があるか (bool)",
        "isLectureSupportChanged": "不明 (bool)",
        "isReportChanged": "新しいレポート情報があるか (bool)",
        "lectureCode":"講義番号",
        "lectureName":"講義名",
        "lectureNameEn":"講義名 (英語)",
        "lectureNo":"講義番号 (リクエストと同じもの、 lectureCode との使い分けは不明) (Number)",
        "lectureWeekSchedule":"講義の曜時限",
        "lectureWeekScheduleEn":"講義の曜時限 (英語)",
        "newFamily":"不明",
        "newFamilyEn":"不明",
        "oldFamily":"不明",
        "oldFamilyEn":"不明",
        "pandaURL":"Panda の URL",
        "roomName":"教室名",
        "roomNameEn":"教室名 (英語)",
        "semester":"前期 or 後期",
        "semesterEn":"前期 or 後期 (英語)",
        "syllabusURL":"シラバスの URL",
        "targetDiscipline":"対象学科",
        "targetDisciplineEn":"対象学科 (英語)",
        "teacherName":"教員名",
        "teacherNameEn":"教員名 (英語)"
    }
    """
    param["departmentNo"] = departmentNo
    param["lectureNo"] = lectureNo
    kulasis_loop = asyncio.get_event_loop()
    res = await kulasis_loop.run_in_executor(None, ses.get, f"{kulasis_api_url}/support/lecture_detail", params=param)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

def get_lecture_detail_from_api(lecture):
    kulasis_course_dict = {'course_id':'','lecture_no':0,'department_no':0,'lecture_name':'','lecture_name_en':'',\
        'lecture_week_schedule':'','lecture_week_schedule_en':'','syllabus_url':'','yearsemester':0}
    panda_url = lecture.get('pandaURL')
    try:
        kulasis_course_dict['course_id'] = re.split(r'/_kcd=',panda_url)[1]
    except IndexError as e:
        kulasis_course_dict['course_id'] = ''
    kulasis_course_dict['lecture_no'] = lecture.get('lectureNo')
    kulasis_course_dict['department_no'] = lecture.get('departmentNo')
    kulasis_course_dict['lecutre_name'] = lecture.get('lectureName')
    kulasis_course_dict['lcture_name_en'] = lecture.get('lecutreNameEn')
    kulasis_course_dict['lecture_week_schedule'] = lecture.get('lectureWeekSchedule')
    kulasis_course_dict['lecture_week_schedule_en'] = lecture.get('lectureWeekScheduleEn')
    kulasis_course_dict['syllabus_url'] = lecture.get('syllabusURL')
    # 要検討
    kulasis_course_dict['yearsemester'] = 0
    return kulasis_course_dict
    
async def get_lecture_material(ses, param, departmentNo, lectureNo):
    """
    講義資料の一覧取得
    {
        "lectureMaterials": [
            {
                    "comment":"コメント",
                    "commentEn":"コメント (英語)",
                    "isNew": "新しいかどうか ? (bool)",
                    "lastModifiedAt":"更新日時",
                    "lastModifiedAtEn":"更新日時 (英語)",
                    "lectureMaterialAttachmentNumbers": "資料の番号のリスト (Number の list)",
                    "lectureWeekSchedule":"曜時限",
                    "lectureWeekScheduleEn":"曜時限 (英語)",
                    "teacherName":"教員名",
                    "teacherNameEn":"教員名 (英語)",
                    "title":"タイトル",
                    "titleEn":"タイトル (英語)"
            }
        ]
    }
    """
    param["departmentNo"] = departmentNo
    param["lectureNo"] = lectureNo
    kulasis_loop = asyncio.get_event_loop()
    res = await kulasis_loop.run_in_executor(None, ses.get, f"{kulasis_api_url}/support/lecture_material", params=param)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

# 未実装
def get_lecture_material_from_api(material):
    resource_list = []
    sr_list = []
    content_collection = material.get("lectureMaterials")
    return

async def get_lecture_material_attachment(ses, param, departmentNo, lectureMaterialAttachmentNo):
    """
    講義資料のダウンロード
    lectureMaterialAttachmentNoはlectureMaterialAttachmentNumbersから取得
    {
        "contentType":"ファイル形式 (MIME ?)",
        "fileBody":"ファイルの中身 (base64)",
        "fileName":"ファイル名"
    }
    """
    param["departmentNo"] = departmentNo
    param["lectureMaterialAttachmentNo"] = lectureMaterialAttachmentNo
    kulasis_loop = asyncio.get_event_loop()
    res = await kulasis_loop.run_in_executor(None, ses.get, f"{kulasis_api_url}/support/lecture_material_attachment", params=param)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

async def get_mail_list(ses, param, departmentNo, lectureNo):
    """
    授業連絡メールの一覧の取得
    {
        "courseMails":[
            {
                "courseMailNo": "連絡メールのメッセージ番号 (Number)",
                "date":"送信日時",
                "dateEn":"送信日時 (英語)",
                "departmentNo":"学部の番号 (Number)",
                "isNew":"新しいかどうか ? (bool)",
                "lectureWeekSchedule":"講義の曜時限",
                "lectureWeekScheduleEn":"講義の曜時限 (英語)",
                "teacherName":"講義の担当教員",
                "teacherNameEn":"講義の担当教員 (英語)",
                "title":"件名",
                "titleEn":"件名 (英語)"
            }
        ]
    }
    """
    param["departmentNo"] = departmentNo
    param["lectureNo"] = lectureNo
    kulasis_loop = asyncio.get_event_loop()
    res = await kulasis_loop.run_in_executor(None, ses.get, f"{kulasis_api_url}/support/course_mail_list", params=param)
    try:
        response = res.json()
        response["lecture_no"] = lectureNo
        return response
    except json.JSONDecodeError as e:
        return {}

def get_mail_list_from_api(mail_list):
    lecture_no = mail_list.get('lectureNo')
    mails = mail_list.get('courseMails')
    mail_details = []
    for mail in mails:
        mail_details.append({'courseMailNo':mail.get('courseMailNo'),'date':mail.get('date'),'department_no':mail.get('departmentNo'),\
            'title':mail.get('title'), 'lectureNo':lecture_no})
    return mail_details

async def get_mail_detail(ses, param, departmentNo, courseMailNo):
    """
    講義連絡メールの内容取得
    {
        "date":"送信日時",
        "textBody":"本文",
        "title":"件名"
    }
    """
    param["departmentNo"] = departmentNo
    param["courseMailNo"] = courseMailNo
    kulasis_loop = asyncio.get_event_loop()
    res = await kulasis_loop.run_in_executor(None, ses.get, f"{kulasis_api_url}/support/course_mail", params=param)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

# announcement は sutdentとcourseと結びつける
def get_mail_detail_from_api(mail_detail, mail_list_index):
    body = mail_detail.get('body')
    mail_list_index["body"] = body
    announcement = mail_list_index
    return announcement