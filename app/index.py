from math import *
import time
from .models import student, assignment, course, studentassignment, instructor, studentcourse, resource, studentresource, assignment_attachment, forum
from .settings import SHOW_YEAR_SEMESTER, VALID_YEAR_SEMESTER, session, app_url, panda_url
import re
from pprint import pprint
import copy

class TimeLeft():
    time_ms:int
    language:str

    def __init__(self, time_ms, language = 'ja'):
        self.time_ms = time_ms
        self.language = language
    
    def add_ato(self, msg):
        if self.language == 'ja':
            msg = f'あと{msg}'
        else:
            msg = f'{msg} left'
        return msg

    def add_ijyou(self, msg):
        if self.language == 'ja':
            msg = f'{msg}以上'
        else:
            msg = f'more than {msg}'
        return msg
    
    def add_miman(self, msg):
        if self.language == 'ja':
            msg = f'{msg}未満'
        else:
            msg = f'less than {msg}'
        return msg

    def time_left_to_str(self):
        to = {'ja':'と','en':' and '}
        unit_minute_single = {'ja':'分', 'en':' minute'}
        unit_minute = {'ja':'分', 'en':' minutes'}
        unit_hour_single = {'ja':'時間', 'en':' hour'}
        unit_hour = {'ja':'時間', 'en':' hours'}
        unit_day_single = {'ja':'日', 'en':' day'}
        unit_day = {'ja':'日', 'en':' days'}
        unit_week_single = {'ja':'週間', 'en':' week'}
        unit_week = {'ja':'週間', 'en':' weeks'}
        now = floor(time.time())
        seconds = self.time_ms/1000 - now
        minutes = seconds/60
        hours = minutes/60
        days = hours/24
        weeks = days/7
        months = weeks/4
        judge_style = 'one_sec'
        msg =''

        if seconds < 0:
            return {'msg':'','judge':judge_style}
        elif minutes < 1:
            # 一分未満
            msg = self.add_miman('1'+ unit_minute_single[self.language])
            judge_style = 'one_min'
        elif hours < 1:
            # 一時間未満
            judge_style = 'one_hour'
            if floor(minutes) == 1:
                msg = str(floor(minutes)) + unit_minute_single[self.language]
            else:
                msg = str(floor(minutes)) + unit_minute[self.language]
        elif days < 1:
            # 一日未満
            judge_style = 'one_day'
            if floor(minutes) == 1:
                msg = str(floor(hours)) + unit_hour_single[self.language]
            else:
                msg = str(floor(hours)) + unit_hour[self.language]
        elif weeks < 1:
            # 一週間未満
            judge_style = 'one_week'
            if floor(days) == 1:
                msg = str(floor(days)) + unit_day_single[self.language]
            else:
                msg = str(floor(days)) + unit_day[self.language]
        elif months < 1:
            # 一か月(4週間)未満
            judge_style = 'one_month'
            if floor(weeks) == 1:
                msg = str(floor(weeks)) + unit_week_single[self.language]
            else:
                msg = str(floor(weeks)) + unit_week[self.language]

            remain_days = floor(days) - floor(weeks)*7

            if remain_days != 0:
                if remain_days ==1:
                    msg += to[self.language] + str(remain_days) + unit_day_single[self.language]
                else:
                    msg += to[self.language] + str(remain_days) + unit_day[self.language]
        else:
            # 一か月以上
            judge_style = 'one_year'
            msg = self.add_ijyou('4' + unit_week[self.language])
        
        return {'msg':self.add_ato(msg),'judge':judge_style}

def sync_student_contents(studentid, crs, asm, res, now,last_update=0):
    # 以下主な方針
    #
    # studentテーブルにlast_updateを用意し、毎回update後に記録しておく
    # APIで課題全取得
    # これまでにないものはinsert
    # modifieddateがlast_updateよりあとのもののみupdate
    #

    # 更新をするのはstudent, student_assignment, student_course, student_resource
    # 加えて、assignment,course,resourceも同時に更新することにする。

    # courseが最初!!!
    sync_student_course(studentid, crs["student_courses"], crs["courses"], last_update)
    sync_student_assignment(studentid, asm["student_assignments"], asm["assignments"], last_update)
    sync_student_resource(studentid, res["student_resources"], res["resources"], last_update)

    return 0

def sync_student_assignment(studentid, sa, asm,last_update): 
    # 追加、更新をする
    add_student_assignment(studentid,sa, last_update)
    add_assignment(studentid, asm, last_update)
    
    


    return 0

def sync_student_course(studentid, sc, crs, last_update):
    # 追加、更新をする
    add_studentcourse(studentid, sc)
    add_course(studentid, crs, last_update)
    return 0

def sync_student_resource(studentid, sr, res, last_update):
    # 追加、更新をする
    add_student_resource(studentid, sr)
    add_resource(studentid, res, last_update)
    return 0

def get_data_from_api_and_update(student_id,ses,now,last_update,need_to_update_sitelist):
    get_membership = {"student_id": "", "site_list":[]}
    if need_to_update_sitelist == 0:                
        get_membership["student_id"] = student_id
        get_membership["site_list"] = get_courses_id_to_be_taken(student_id)
    else:
        # 時間かかる
        last_update = 0
        get_membership = get_course_id_from_api(get_membership_json(ses))
        already_known= get_courses_id_to_be_taken(student_id)
        # 新規のもののみを取り上げる
        get_membership["site_list"] = [i for i in get_membership["site_list"] if i not in already_known]
    if student_id != "":
        # get_assignments = get_assignments_from_api(assignments.json(), student_id)
        get_sites = {"courses":[],"student_courses":[]}
        get_resources = {"resources":[],"student_resources":[]}
        asyncio.set_event_loop(asyncio.SelectorEventLoop())
        loop = asyncio.get_event_loop()
        c_statements = []
        s_statements = []
        p_statements = []
        for courseid in get_membership["site_list"]:
            c_statements.append(async_get_content(courseid, ses))
            s_statements.append(async_get_site(courseid, ses))
            p_statements.append(async_get_site_pages(courseid, ses))
            # site = s.get(f"{api_url}site/{courseid}.json")
            # resources = s.get(f"{api_url}content/site/{courseid}.json")
            # get_site = get_course_from_api(site.json(), student_id)
            # get_sites["courses"].append(get_site["course"])
            # get_sites["student_courses"].append(get_site["student_course"])
            # get_resource = get_resources_from_api(resources.json(),courseid,student_id)
            # get_resources["resources"].append(get_resource["resources"])
            # get_resources["student_resources"].append(get_resources["student_resources"])
        c_statements.extend(s_statements)
        c_statements.extend(p_statements)
        c_statements.extend([async_get_assignments(ses),async_get_user_info(ses)])
        tasks = asyncio.gather(*c_statements)
        content_site = loop.run_until_complete(tasks)
        content_site_len = int(len(content_site))-2
        one_third_content_site_len = content_site_len//3
        contents = content_site[0:one_third_content_site_len]
        sites = content_site[one_third_content_site_len:one_third_content_site_len*2]
        pages = content_site[one_third_content_site_len*2:content_site_len]
        get_assignments = get_assignments_from_api(content_site[content_site_len],student_id)
        user_info = get_user_info_from_api(content_site[content_site_len+1])
        index = 0
        for courseid in get_membership["site_list"]:
            get_resource = get_resources_from_api(contents[index],courseid,student_id)
            get_site = get_course_from_api(sites[index], student_id)
            if get_site:
                get_site["course"]["page_id"] = get_page_from_api(pages[index])
                get_sites["courses"].append(get_site["course"])
                get_sites["student_courses"].append(get_site["student_course"])
                get_resources["resources"].extend(get_resource["resources"])
                get_resources["student_resources"].extend(get_resource["student_resources"])
            index += 1
        # student_id       student_id
        # get_membership   {"student_id": , "site_list": []}
        # get_assignments  {"assignments": [], student_assignments: []}
        # get_sites        {"courses": [], "student_courses": []}
        # get_resources    {"resources":[], "student_resources": []}
        # user_info        {"student_id": , "fullname": }
        sync_student_contents(student_id, get_sites, get_assignments, get_resources, now, last_update=last_update)



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
        time_ms = assignment.get('dueTime').get('time')
        course_id = assignment.get('context')
        modifieddate = assignment.get('timeLastModified').get('time')
        status = assignment.get('status')
        sa_list.append({"sa_id":f"{student_id}:{assignment_id}","assignment_id":assignment_id,"course_id":course_id,"status":"未","student_id":student_id,"clicked":0})
        assignment_list.append({"assignment_id":assignment_id,"url":url,"title":title,"limit_at":limit_at,"instructions":instructions,"time_ms":time_ms,"modifieddate":modifieddate,"course_id":course_id})
    assignment_dict = {"student_assignments":sa_list, "assignments":assignment_list}
    return assignment_dict

def get_resources_from_api(resources, course_id, student_id):
    resource_list = []
    sr_list = []
    content_collection = resources.get("content_collection")
    for content in content_collection:
        resource_author = content.get('author')
        resource_container = content.get('container')
        resource_modified_date = content.get('modifiedDate')
        resource_title = content.get('title')[:80]
        resource_url = content.get('url')
        container_split = resource_container.split('/')
        resource_list.append({'course_id':course_id, 'container': resource_container, 'title': resource_title, \
            'resource_url': resource_url, 'modifieddate': resource_modified_date})
        sr_list.append({"sr_id":f"{student_id}:{resource_url}", "resource_url":resource_url, "student_id":student_id, "course_id":course_id, "status":0})
    resource_dict = {"student_resources":sr_list, "resources":resource_list}
    return resource_dict

def get_student_id_from_api(membership):
    mem_collection = membership.get('membership_collection')
    student_id = ""
    for member in mem_collection:
        student_id = member.get('userId')
        break
    return student_id

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

def get_user_info_from_api(user):
    fullname = user.get('displayName')
    student_id = user.get('id')
    return {"student_id":student_id,"fullname":fullname}

def get_page_from_api(pages):
    page_id = ""
    for page in pages:
        title = page.get('title')
        if re.search('課題', title) or re.search('assignment', title):
            page_id = page.get('tools')[0].get('id')
            break
    return page_id

import asyncio, requests, json

def get_user_json(ses):
    res = ses.get("https://panda.ecs.kyoto-u.ac.jp/direct/user/current.json")
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

def get_session_json(ses):
    res = ses.get("https://panda.ecs.kyoto-u.ac.jp/direct/session/current.json")
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

def get_membership_json(ses):
    res = ses.get("https://panda.ecs.kyoto-u.ac.jp/direct/membership.json")
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}


async def async_get_content(site_id, ses):
    url = f"https://panda.ecs.kyoto-u.ac.jp/direct/content/site/{site_id}.json"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {'content_collection':[]}

async def async_get_site(site_id, ses):
    url = f"https://panda.ecs.kyoto-u.ac.jp/direct/site/{site_id}.json"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {'id':site_id}

async def async_get_site_pages(site_id, ses):
    url = f"https://panda.ecs.kyoto-u.ac.jp/direct/site/{site_id}/pages.json"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

async def async_get_assignments(ses):
    url = f"https://panda.ecs.kyoto-u.ac.jp/direct/assignment/my.json"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}

async def async_get_user_info(ses):
    url = f"https://panda.ecs.kyoto-u.ac.jp/direct/user/current.json"
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, ses.get, url)
    try:
        return res.json()
    except json.JSONDecodeError as e:
        return {}


def get_tasklist(studentid, show_only_unfinished = False,courseid=None, day=None, mode=0):
    """
        mode
        0:tasklist
        1:tasklist for overview
    """
    # new_student = enrollment.enrollment()
    # new_student.enrollmentID = "2"
    # new_student.assignmentID = "kadai"
    # new_student.StudentID = "guest"
    # new_student.Status = "finished"
    # new_student.CourseID = "courseA"

    # new_student = assignment.Assignment()
    # new_student.AssignmentID = "kadai"
    # new_student.Title = "kadai"

    # session.add(new_student)

    # new_student = course.Course()
    # new_student.CourseID = "courseA"
    # new_student.CourseName = "PandAsh"
    # session.add(new_student)
    # session.commit()

    if show_only_unfinished == False:
        enrollments = session.query(studentassignment.Student_Assignment).filter(
            studentassignment.Student_Assignment.student_id == studentid).all()
    else:
        enrollments = session.query(studentassignment.Student_Assignment).filter(
            studentassignment.Student_Assignment.student_id == studentid).filter(
                studentassignment.Student_Assignment.status == "未").all()
    assignmentids =[i.assignment_id for i in enrollments]
    course_to_be_taken=get_courses_to_be_taken(studentid)
    courseids = [i.course_id for i in course_to_be_taken]
    assignmentdata = session.query(assignment.Assignment).filter(
        assignment.Assignment.assignment_id.in_(assignmentids)).all()
    
    coursedata = session.query(course.Course).filter(
            course.Course.course_id.in_(courseids)).all()
    
    tasks = []
    for data in enrollments:
        asmdata = [i for i in assignmentdata if i.assignment_id == data.assignment_id]
        crsdata = [i for i in coursedata if i.course_id == asmdata[0].course_id]
        
        if courseid != None:
            if courseid != asmdata[0].course_id:
                continue
        if asmdata[0].course_id not in courseids:
            continue
        if day != None:
            if day not in crsdata[0].classschedule:
                continue
        
        task = {}
        task["status"] = data.status
        task["taskname"] = asmdata[0].title
        task["assignmentid"] = data.assignment_id
        task["deadline"] = asmdata[0].limit_at
        task["time_left"] = TimeLeft(asmdata[0].time_ms).time_left_to_str()
        task["clicked"] = data.clicked
        if task["time_left"]["msg"] == "":
            task["status"]="期限切れ"
        if mode == 1:
            # overviewのtooltipsに使用
            task["instructions"] = asmdata[0].instructions

        task["subject"] = crsdata[0].coursename
        task["tool_id"] = crsdata[0].page_id
        task["course_id"] = crsdata[0].course_id
        if mode == 1:
            task["classschedule"] = crsdata[0].classschedule
        if show_only_unfinished==1:
            if task["status"]!="未":
                continue
        task["assignment_url"] = f"{panda_url}/site/"+task["course_id"]+f"/tool/"+task["tool_id"]+f"?assignmentReference=/assignment/a/"+task["course_id"]+"/"+task["assignmentid"]+"&panel=Main&sakai_action=doView_submission"
        tasks.append(task)
    return tasks

# mode = 1 のときはhideのものも取得
def get_courses_to_be_taken(studentid, mode = 0,return_data = 'course'):
    data=[]
    courses = session.query(studentcourse.Studentcourse).filter(
        studentcourse.Studentcourse.student_id == studentid).all()
    for i in courses:
        if mode==0 and i.hide==1:
            continue
        coursedata = session.query(course.Course).filter(
            course.Course.course_id == i.course_id).all()
        if coursedata[0].yearsemester in SHOW_YEAR_SEMESTER:
            if return_data == 'course':
                data.append(coursedata[0])
            elif return_data == 'student_course':
                data.append(i)
            else:
                #一応courseを返す
                data.append(coursedata[0])
    return data

def get_courses_id_to_be_taken(studentid, mode=0):
    data=[]
    courses = session.query(studentcourse.Studentcourse).filter(
        studentcourse.Studentcourse.student_id == studentid).all()
    for i in courses:
        if mode==0 and i.hide == 1:
            continue
        coursedata = session.query(course.Course).filter(
            course.Course.course_id == i.course_id).all()
        if coursedata[0].yearsemester in SHOW_YEAR_SEMESTER:
            data.append(coursedata[0].course_id)
    return data

def setdefault_for_overview(studentid, mode='tasklist'):
    data={}
    days =["mon", "tue", "wed", "thu", "fri"]
    default = {"subject": "", "shortname": "", "searchURL": "","tasks": []}
    for day in days:
        for i in range(5):
            data[day+str(i+1)]=copy.copy(default)
    data["others"]=[]
    coursedata = get_courses_to_be_taken(studentid)
    for course in coursedata:
        add_in_others = False
        add_subject = False
        # 教科に時限情報がない場合
        if course.classschedule == "others" or course.classschedule == "oth":
            add_in_others = True
        else:
            if data[course.classschedule]["subject"] != "":
                if course.coursename != data[course.classschedule]["subject"]:
                    # 本来の時限に既に別科目が入っている
                    add_in_others = True
            else:
                # 本来の時限に科目を入れられる
                add_subject = True

        if add_in_others == True:
            # othersは教科が複数あるので何番目の教科か判定する必要がある
            subject_exist = False
            index = 0
            for subject in data["others"]:
                if subject["subject"] == course.coursename:
                    subject_exist = True
                    break
                index += 1
            if subject_exist:
                continue
            else:
                # 新しい教科を追加
                data["others"].append({})
                data["others"][index]["searchURL"] = app_url+ f"/{mode}/course/"+course.course_id
                data["others"][index]["subject"] = course.coursename
                data["others"][index]["shortname"] = re.sub(
                    "\[.*\]", "", course.coursename)
                data["others"][index]["tasks"] = []

        elif add_subject == True:
            data[course.classschedule]["searchURL"] = app_url+ f"/{mode}/course/"+course.course_id
            data[course.classschedule]["subject"] = course.coursename
            data[course.classschedule]["shortname"] = re.sub(
                "\[.*\]", "", course.coursename)
            data[course.classschedule]["tasks"] = []
    return data


def task_arrange_for_overview(tasks,task_arranged):

    for task in tasks:
        add_in_others = False
        # 教科に時限情報がない場合
        if task["classschedule"] == "others" or task["classschedule"] == "oth":
            add_in_others = True
        else:
            if task["classschedule"] in task_arranged.keys():
                if task["subject"] != task_arranged[task["classschedule"]]["subject"]:
                    add_in_others = True
            else:
                add_in_others = True
        if add_in_others == True:
            # othersは教科が複数あるので何番目の教科か判定する必要がある
            subject_exist = False
            index = 0
            for subject in task_arranged["others"]:
                if subject["subject"] == task["subject"]:
                    subject_exist = True
                    break
                index += 1
            if subject_exist:
                task_arranged["others"][index]["tasks"].append(task)
            else:
                # 新しい教科を追加(本来ここに到達することはない)
                task_arranged["others"].append({})
                task_arranged["others"][index]["searchURL"] = ""
                task_arranged["others"][index]["subject"] = task["subject"]
                task_arranged["others"][index]["shortname"] = re.sub(
                    "\[.*\]", "", task["subject"])
                task_arranged["others"][index]["tasks"] = [task]

        else:
            task_arranged[task["classschedule"]]["tasks"].append(task)
    return task_arranged


def get_resource_list(studentid, course_id=None, day=None):
    srs = session.query(studentresource.Student_Resource).filter(
        studentresource.Student_Resource.student_id == studentid).all()
    
    resource_urls = [i.resource_url for i in srs]
    
    resourcedata = session.query(resource.Resource).filter(
        resource.Resource.resource_url.in_(resource_urls)).all()
    course_to_be_taken=get_courses_to_be_taken(studentid)
    courseids = [i.course_id for i in course_to_be_taken]
    coursedata = session.query(course.Course).filter(
        course.Course.course_id.in_(courseids)).all()
    resource_list={i:[] for i in courseids}

    for data in srs:
        rscdata = [i for i in resourcedata if i.resource_url == data.resource_url]
        crsdata = [i for i in coursedata if i.course_id == rscdata[0].course_id]
        
        if course_id != None:
            if course_id != rscdata[0].course_id:
                continue
        if rscdata[0].course_id not in courseids:
            continue
        if day !=None:
            if day not in crsdata[0].classschedule:
                continue
        resource_dict = {}
        resource_dict["resource_url"] = data.resource_url
        resource_dict["title"] = rscdata[0].title
        resource_dict["container"] = rscdata[0].container
        resource_dict["modifieddate"] = rscdata[0].modifieddate
        resource_dict["status"] = data.status
        resource_list[rscdata[0].course_id].append(resource_dict)
    return resource_list


def resource_arrange(resource_list:list, coursename:str, courseid):
    course = {"folders":[],"files":[],"name":coursename}
    folderlist = []
    html = ""
    for r in resource_list:
        container = r['container']
        container_spilt = container.split('/')
        del container_spilt[-1]
        for i in range(3):
            del container_spilt[0]
        for folder in folderlist:
            if folder == container_spilt:
                break
        else:
            folderlist.append(container_spilt)
    for foldername in folderlist:
        list_f = course["folders"]
        str_place = 0
        folderindex = 1
        folder_num = 0
        for f in foldername:
            folder_num += 1
            index = 0
            isExist = False
            tag_class = "fas fa-folder-plus"
            if folder_num == 1:
                tag_class = "far fa-folder"
            for lf in list_f:
                if lf["name"] == f:
                    list_f = list_f[index]["folders"]
                    isExist = True
                    break
                index += 1
            if isExist:
                html_1 = re.search(f'><i class="fa.*">{f}</i><ul>', html[str_place:])
                if html_1:
                    str_place += html_1.end()
                folderindex += 1
                continue
            folder_id = '/'.join(foldername[:folderindex])
            html = html[:str_place] + f'''
            <li id="{folder_id}"><i class="{tag_class}">{f}</i><ul></ul></li>''' + html[str_place:]
            html_1 = re.search(f'><i class="fa.*">{f}</i><ul>', html[str_place:])
            if html_1:
                str_place += html_1.end()
            list_f.append({'folders':[],'files':[],'name':f})
            list_len = len(list_f)
            list_f = list_f[list_len-1]["folders"]
            folderindex += 1
    for r in resource_list:
        list_f = course["folders"]
        container = r['container']
        container_spilt = container.split('/')
        del container_spilt[-1]
        for i in range(3):
            del container_spilt[0]
        folder_id = '/'.join(container_spilt)
        folder = re.search(f'<li id="{folder_id}">',html)
        search_num = 0
        if folder:
            search_num = folder.end()
        folder_i = re.search(f'</i><ul>',html[search_num:])
        # target = "_self"
        target = "_blank"
        # if re.search(r'.*\.pdf' ,r["resource_url"]):
        #     target = "_blank"
        #2020/1/19 Shinji Akayama style = "poi"
        # checkbox あり
        # add_html = f"""
        # <li>
        #     <div class="form-check">
        #         <input class="form-check-input" type="checkbox" id="{r["resource_url"]}" value="0"/>
        #         <label class="form-check-label" for="{r["resource_url"]}"> 
        #             <a href="{r["resource_url"]}" target="{target}" download="{r["title"]}" name="{r["resource_url"]}"　style="pointer-events: none;">{r["title"]}</a>
        #         </label>
        #     </div>
        # </li>"""
        # if r['status'] == 1:
        #     add_html = f"""
        #     <li>
        #         <div class="d-inline-flex">
        #             <div class="form-check">
        #                 <input class="form-check-input" type="checkbox" id="{r["resource_url"]}" value="1" disabled checked/>
        #                 <label class="form-check-label" for="{r["resource_url"]}">
        #                         <a href="{r["resource_url"]}" download="{r["title"]}" data-container="body" data-toggle="tooltip" title="このファイルを再ダウンロードする" name="{r["resource_url"]}" target="{target}">{r["title"]}</a>                     
        #                 </label>
        #             </div>
        #         </div>
        #     </li>
        #     """
        # checkbox なし
        status_class = "undownloaded"
        resource_title = r["title"]
        if r["status"] == 1:
            status_class = "downloaded"
            resource_title = "このファイルを再ダウンロードする"
        add_html = f"""
            <li>
                <div class="d-inline-flex">
                    <div class="form-check">
                        <label class="form-check-label" for="{r["resource_url"]}">
                                <a href="{r["resource_url"]}" download="{r["title"]}" data-container="body" data-toggle="tooltip" title={resource_title} name="{r["resource_url"]}" target="{target}" class="resource {status_class}">{r["title"]}</a>                     
                        </label>
                    </div>
                </div>
            </li>
        """
        if folder_i:
            html = html[:folder_i.end()+search_num] + add_html + html[folder_i.end()+search_num:]
    # html = f"""<span><i class="far fa-folder" style="font-size:medium;">{coursename}</i></span>
    #         """ + html
    # html = f'<li class="list-group-item">{coursename}<ul>' + html + '</ul></li>'
    html = f"""
        <div class="card">
            <div class="card-body ressubs">
        <span><i class="far fa-folder">
            <a href="/resourcelist/course/{courseid}">{coursename}</a>
        </i><span>
        """ + html + "</div></div>"
    return html

def get_coursename(courseid):
    coursename = session.query(course.Course.coursename).filter(course.Course.course_id==courseid).first()
    return coursename[0]

def get_courseids(studentid):
    course_ids = session.query(studentcourse.Studentcourse.course_id).filter(studentcourse.Studentcourse.student_id==studentid).all()
    return [i.course_id for i in course_ids]

def get_student(studentid):
    studentdata = session.query(student.Student).filter(student.Student.student_id == studentid).all()
    if len(studentdata) != 0:
        studentdata = studentdata[0]
    else:
        studentdata = None
    return studentdata

def add_student(studentid, fullname, last_update = 0, last_update_subject = 0, language = "ja"):
    students = session.query(student.Student.student_id).all()
    isExist = False
    for i in students:
        if list(i)[0] == studentid:
            isExist = True
            break
    new_student = {"student_id":studentid, "fullname":fullname,"last_update":last_update, "last_update_subject":last_update_subject,"language":language}
    if isExist == False:
        session.execute(student.Student.__table__.insert(),new_student)
    else:
        session.bulk_update_mappings(student.Student, [new_student])
    session.commit()
    return

def add_assignment_attachment(url, title, assignment_id):
    assignments = session.query(assignment_attachment.Assignment_attachment.assignment_url).all()
    isExist = False
    for i in assignments:
        if list(i)[0] == url:
            isExist = True
            break
    if isExist == False:
        new_assignment_attachment = assignment_attachment.Assignment_attachment(assignment_url=url, title=title, assignment_id=assignment_id)
        session.add(new_assignment_attachment)
        session.commit()
    return

def add_assignment(studentid, data, last_update):
    course_ids = get_courseids(studentid)
    assignments = session.query(
        assignment.Assignment).filter(assignment.Assignment.course_id.in_(course_ids)).all()
    new_asm=[]
    upd_asm = []
    for item in data:
        assignment_exist = False
        update=False
        if item["course_id"] not in course_ids:
            continue
        for i in assignments:
            if i.assignment_id == item["assignment_id"]:
                assignment_exist = True
                if item["modifieddate"] > last_update:
                    update=True
                break
        if assignment_exist == False:
            new_asm.append(item)
        elif update == True:
            upd_asm.append(item)
    if len(new_asm) != 0:
        session.execute(assignment.Assignment.__table__.insert(),new_asm)
    if len(upd_asm) != 0:
        session.bulk_update_mappings(assignment.Assignment, upd_asm)
    session.commit()
    return

def add_course(studentid, data, last_update):
    course_ids = get_courseids(studentid)
    courses = session.query(
        course.Course).filter(course.Course.course_id.in_(course_ids)).all()
    new_crs=[]
    upd_crs = []
    for item in data:
        course_exist = False
        update=False
        if item["course_id"] not in course_ids:
            continue
        for i in courses:
            if i.course_id == item["course_id"]:
                course_exist = True
                break
        if course_exist == False:
            new_crs.append(item)
        elif update == True:
            upd_crs.append(item)
    if len(new_crs) != 0:
        session.execute(course.Course.__table__.insert(),new_crs)
    if len(upd_crs) != 0:
        session.bulk_update_mappings(course.Course, upd_crs)
    session.commit()
    return


def add_student_assignment(studentid, data, last_update):
    """
        data:assignment_id, student_id, status
    """
    sa = session.query(
        studentassignment.Student_Assignment).filter(studentassignment.Student_Assignment.student_id == studentid).all()
    course_ids = get_courseids(studentid)
    new_sa = []
    upd_sa = []
    for item in data:
        assignment_exist = False
        update=False
        if not item["course_id"] in course_ids:
            continue
        for i in sa:
            if i.assignment_id == item["assignment_id"]:
                assignment_exist = True
                if item["status"] !='未':
                    update=True
                break
        if assignment_exist == False:
            new_sa.append(item)
        elif update == True:
            upd_sa.append(item)
    if len(new_sa) != 0:
        session.execute(studentassignment.Student_Assignment.__table__.insert(),new_sa)
    if len(upd_sa) != 0:
        session.bulk_update_mappings(studentassignment.Student_Assignment, upd_sa)
    session.commit()
    return


def add_instructor(instructorid, fullname, emailaddress):
    instructors = session.query(instructor.Instructor.instructor_id).all()
    isExist = False
    for i in instructors:
        if list(i)[0] == instructorid:
            isExist = True
            break
    if isExist == False:
        new_instructor = instructor.Instructor(instructor_id=instructorid, fullname=fullname, emailaddress=emailaddress)
        session.add(new_instructor)
        session.commit()
    return

def add_student_resource(studentid,data):
    """
        data: resourceurl, studentid, status
    """
    sr = session.query(studentresource.Student_Resource).filter(studentresource.Student_Resource.student_id ==studentid).all()
    course_ids = get_courseids(studentid)
    new_sr = []
    upd_sr = []
    for item in data:
        resource_exist = False
        update = False
        if item["course_id"] not in course_ids:
            continue
        for i in sr:
            if i.resource_url == item["resource_url"]:
                resource_exist = True
                if item["status"] !=0:
                    update=True
                break
        if resource_exist == False:
            new_sr.append(item)
        elif update == True:
            upd_sr.append(item)
    if len(new_sr) != 0:
        session.execute(studentresource.Student_Resource.__table__.insert(),new_sr)
    if len(upd_sr) != 0:
        session.bulk_update_mappings(studentresource.Student_Resource, upd_sr)
    session.commit()
    return


def add_resource(studentid, data, last_update):
    course_ids = get_courseids(studentid)
    resources = session.query(
        resource.Resource).filter(resource.Resource.course_id.in_(course_ids)).all()
    new_res=[]
    upd_res = []
    for item in data:
        resource_exist = False
        update=False
        if item["course_id"] not in course_ids:
            continue
        for i in resources:
            if i.resource_url == item["resource_url"]:
                resource_exist = True
                if i.modifieddate > last_update:
                    update=True
                break
        if resource_exist == False:
            new_res.append(item)
        elif update == True:
            upd_res.append(item)
    if len(new_res) != 0:
        session.execute(resource.Resource.__table__.insert(),new_res)
    if len(upd_res) != 0:
        session.bulk_update_mappings(resource.Resource, upd_res)
    session.commit()
    return

def update_student_needs_to_update_sitelist(student_id,need_to_update_sitelist=0):
    st = session.query(student.Student).filter(student.Student.student_id==student_id).first()
    st.need_to_update_sitelist = need_to_update_sitelist
    session.commit()
    return

def update_student_show_already_due(student_id,show_already_due=0):
    st = session.query(student.Student).filter(student.Student.student_id==student_id).first()
    st.show_already_due = show_already_due
    session.commit()
    return

def update_student_course_hide(student_id, course_list, hide):
    update_list = []
    for coursedata in course_list:
        sc_id = f'{student_id}:{coursedata}'
        update_list.append({"sc_id":sc_id,"hide":hide})
    session.bulk_update_mappings(studentcourse.Studentcourse, update_list)
    session.commit()
    return

def update_resource_status(studentid, resourceids: list):
    srs = session.query(studentresource.Student_Resource.resource_url, studentresource.Student_Resource.sr_id).filter(
        studentresource.Student_Resource.student_id == studentid).all()
    update_list = []
    for r_id in resourceids:
        sr_id = f'{studentid}:{r_id}'
        update_list.append({"sr_id":sr_id, "status":1})
    session.bulk_update_mappings(studentresource.Student_Resource, update_list)
    session.commit()
    return

def update_task_status(studentid, taskids: list, mode=0):
    update_list = []
    status = "未"
    if mode==0:
        status = "済"
    for t_id in taskids:
        sa_id = f'{studentid}:{t_id}'
        update_list.append({"sa_id":sa_id, "status":status})
    session.bulk_update_mappings(studentassignment.Student_Assignment, update_list)
    session.commit()
    return

def update_task_clicked_status(studentid, taskids:list):
    update_list = []
    for t_id in taskids:
        sa_id = f'{studentid}:{t_id}'
        update_list.append({"sa_id":sa_id, "clicked":1})
    session.bulk_update_mappings(studentassignment.Student_Assignment, update_list)
    session.commit() 
    return

def add_studentcourse(studentid, data):
    """
        data:[{student_id:"", course_id:""},{}]
    """
    sc = session.query(studentcourse.Studentcourse).filter(studentcourse.Studentcourse.student_id == studentid).all()
    new_sc = []
    for item in data:
        course_exist = False
        for i in sc:
            if i.course_id == item["course_id"]:
                course_exist = True
                break
        if course_exist == False:
            new_sc.append(item)
    if len(new_sc)!=0:
        session.execute(studentcourse.Studentcourse.__table__.insert(),new_sc)
    session.commit()
    return

def sort_tasks(tasks, show_only_unfinished = False, max_time_left = 3):
    """
        about max_time_left
        0:an hour
        1:a day
        2:a week
    """
    if show_only_unfinished == True:
        tasks = [task for task in tasks if task["status"] == "未"]
    if max_time_left in [0, 1, 2]:
        tasks = [task for task in tasks if timejudge(task, max_time_left)]
    
    for task in tasks:
        if task["time_left"] == "":
            task["status"]="期限切れ"

    
    new_tasks = sorted([i for i in tasks if i["status"] != "期限切れ"], key=lambda x: x["deadline"])
    new_tasks.extend(sorted([i for i in tasks if i["status"] == "期限切れ"], key=lambda x: x["deadline"],reverse=True))
    new_tasks = sorted(new_tasks, key=lambda x: order_status(x["status"]))
    return new_tasks


def timejudge(task, max_time_left):
    # ex あと10分
    time_left = task["time_left"]
    units = ["minute", "分", "hour", "時", "day", "日"]
    u_num = 0
    if max_time_left == 0:
        u_num = 2
    elif max_time_left == 1:
        u_num = 4
    else:
        u_num = 6
    for i in range(u_num):
        if units[i] in time_left:
            return True
    return False


def order_status(status):
    if status == "未":
        return 0
    elif status == "済":
        return 1
    elif status == "期限切れ":
        return 2
    else:
        return 3


def get_search_condition(show_only_unfinished ,max_time_left , course=None, day=None):
    condition=[]
    select3a_judge = 0
    if course != None:
        condition.append(f"{get_coursename(course)}のみ")
    elif day !=None:
        condition.append(f"{day_to_str(day)}のみ")
    if show_only_unfinished == 1:
        condition.append("未完了のみ")
        select3a_judge = 1
    if max_time_left == 0:
        condition.append("一時間以内")
        select3a_judge = 2
    elif max_time_left == 1:
        condition.append("二十四時間以内")
        select3a_judge = 3
    elif max_time_left == 2:
        condition.append("一週間以内")
        select3a_judge = 4
    if len(condition) != 0:       
        search_condition='・'.join(condition)
    else:
        search_condition="全て"
    return {"search_condition":search_condition, "select3a_judge":select3a_judge}

def day_to_str(day):
    if day == "mon":
        day_str="月曜"
    elif day == "tue":
        day_str="火曜"
    elif day == "wed":
        day_str="水曜"
    elif day == "thu":
        day_str="木曜"
    elif day == "fri":
        day_str="金曜"
    else: day_str="曜日設定がないもの"

    return day_str

def add_forum(studentid,title,contents):
    inq = forum.Forum()
    inq.student_id = studentid
    inq.title = title
    inq.contents = contents
    session.add(inq)
    session.commit()
    return f"""
    -----FORUM-----
    STUDENT: {studentid},
    TITLE: {title},
    CONTENTS: {contents}
    ---------------"""
