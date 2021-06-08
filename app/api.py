# APIを用いて情報を取得する関数一覧
#

import asyncio, json
from math import *
from .settings import VALID_YEAR_SEMESTER, api_url
import re
from .original_classes import Status

def get_assignments_from_api(assignments, student_id):
    assignment_list = []
    sa_list = []
    ass_colection = assignments.get("assignment_collection")
    for assignment in ass_colection:
        assignment_id = assignment.get('id')
        url = assignment.get('entityURL')
        title = assignment.get('title')[:80]
        limit_at = assignment.get('dueTimeString')
        instructions = assignment.get('instructions')[:100]
        time_ms = assignment.get('dueTime').get('epochSecond')
        course_id = assignment.get('context')
        modifieddate = assignment.get('timeLastModified').get('epochSecond')
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
    yearsch = re.match(r'\[.*\]', coursename)
    yearsemester = "10009"
    classschedule = "oth"
    try:
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
    course_dict = {"course_id":course_id,"instructior_id":instructor_id,"coursename":coursename,"yearsemester":yearsemester,"classschedule":classschedule,"page_id":""}
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
        if s.get('joinerRole') != "Student":
            continue
        user_site_id = s.get('id')
        site_id = user_site_id.replace(f'{student_id}::site:','')
        site_list.append(site_id)
    return {"student_id":student_id, "site_list":site_list}

def get_membership_json(ses):
    res = ses.get(f"{api_url}/membership.json")
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

# get_membership_json(ses) の代わり
def get_site_json(ses):
    res = ses.get(f"{api_url}/site.json?_limit=2000")
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {"site_collection": []}

def get_page_from_api(pages):
    page_id = ""
    for page in pages:
        title = page.get('title')
        if re.search('課題', title) or re.search('assignment', title):
            page_id = page.get('tools')[0].get('id')
            break
    return page_id

def get_resources_from_api(resources, course_id, student_id):
    resource_list = []
    sr_list = []
    content_collection = resources.get("content_collection")
    for content in content_collection:
        resource_author = content.get('author')
        resource_container = content.get('container')
        md = str(int(content.get('modifiedDate'))//1000)
        date_format = "%Y%m%d%H%M%S"
        resource_modified_date = int(datetime.datetime.strptime(md,date_format).timestamp())
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
        quiz_id = content.get('publishedAssessmentId')
        # とりあえずsite_id
        url = content.get('ownerSiteId')
        title = content.get('entityTitle')
        time_ms = content.get('dueDate')
        modifieddate = str(int(content.get('lastModifiedDate'))//1000)
        limit_at = datetime.datetime.fromtimestamp(limit_at//1000)
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
    res = ses.get(f"{api_url}/user/current.json")
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

def get_session_json(ses):
    res = ses.get(f"{api_url}/session/current.json")
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

#async
async def async_get_assignments(ses):
    url = f"{api_url}/assignment/my.json"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

async def async_get_content(site_id, ses):
    url = f"{api_url}/content/site/{site_id}.json"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {'content_collection':[]}

async def async_get_quiz(site_id, ses):
    url = f"{api_url}/sam_pub/content/{site_id}.json"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {'sam_pub_collection':[]}

async def async_get_site(site_id, ses):
    url = f"{api_url}/site/{site_id}.json"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {'id':site_id}

async def async_get_site_pages(site_id, ses):
    url = f"{api_url}/site/{site_id}/pages.json"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

async def async_get_user_info(ses):
    url = f"{api_url}/user/current.json"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}
