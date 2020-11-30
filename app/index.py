from math import *
import time
from .models import student, assignment, course, studentassignment, instructor, studentcourse, resource, studentresource, assignment_attachment
from .settings import session, app_url
import re
from pprint import pprint
import copy


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
        if day != None:
            if day not in crsdata[0].classschedule:
                continue
        if asmdata[0].course_id not in courseids:
            continue
        
        task = {}
        task["status"] = data.status
        task["taskname"] = asmdata[0].title
        task["assignmentid"] = data.assignment_id
        task["deadline"] = asmdata[0].limit_at
        task["time_left"] = remain_time(asmdata[0].time_ms)
        if mode == 1:
            # overviewのtooltipsに使用
            task["instructions"] = asmdata[0].instructions

        task["subject"] = crsdata[0].coursename
        if mode == 1:
            task["classschedule"] = crsdata[0].classschedule

        tasks.append(task)
    return tasks

def get_courses_to_be_taken(studentid):
    data=[]
    courses = session.query(studentcourse.Studentcourse).filter(
        studentcourse.Studentcourse.student_id == studentid).all()
    for i in courses:
        # if course.hide == 1:
        #     continue
        coursedata = session.query(course.Course).filter(
            course.Course.course_id == i.course_id).all()
        data.append(coursedata[0])
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
        if course.classschedule == "others":
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
        if task["classschedule"] == "others":
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
    resource_list = []
    resources = session.query(studentresource.Student_Resource).filter(
        studentresource.Student_Resource.student_id == studentid).all()
    for data in resources:
        resourcedata = session.query(resource.Resource).filter(
            resource.Resource.resource_url == data.resource_url).all()
        if course_id != None:
            if course_id != resourcedata[0].course_id:
                continue
        coursedata = session.query(course.Course).filter(
            course.Course.course_id == resourcedata[0].course_id).all()
        if day !=None:
            if day not in coursedata.classschedule:
                continue
        resource_dict = {}
        resource_dict["resource_url"] = data.resource_url
        resource_dict["title"] = resourcedata[0].title
        resource_dict["container"] = resourcedata[0].container
        resource_dict["modifieddate"] = resourcedata[0].modifieddate
        resource_dict["status"] = data.status
        resource_list.append(resource_dict)
    return resource_list


def resource_arrange(resource_list:list, coursename:str):
    course = {"folders":[],"files":[],"name":coursename}
    folderlist = []
    html = ""
    for r in resource_list:
        container = r['container']
        container_spilt = container.split('/')
        del container_spilt[-1]
        for i in range(4):
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
                html_1 = re.search(f'><i class="{tag_class}">{f}</i><ul>', html[str_place:])
                str_place += html_1.end()
                folderindex += 1
                continue
            folder_id = '/'.join(foldername[:folderindex])
            html = html[:str_place] + f'''
            <li id="{folder_id}"><i class="{tag_class}">{f}</i><ul></ul></li>''' + html[str_place:]
            html_1 = re.search(f'><i class="{tag_class}">{f}</i><ul>', html[str_place:])
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
        for i in range(4):
            del container_spilt[0]
        folder_id = '/'.join(container_spilt)
        folder = re.search(f'<li id="{folder_id}">',html)
        search_num = folder.end()
        folder_i = re.search(f'</i><ul>',html[search_num:])
        add_html = f"""
        <li>
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="{r["resource_url"]}" value="0"/>
                <label class="form-check-label" for="{r["resource_url"]}">
                    <a href="{r["resource_url"]} target="_self" download="{r["title"]}" name="{r["resource_url"]}">{r["title"]}</a>
                </label>
            </div>
        </li>"""
        if r['status'] == 1:
            add_html = f"""
            <li>
                <div class="d-inline-flex">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="{r["resource_url"]}" value="1" disabled checked/>
                        <label class="form-check-label" for="{r["resource_url"]}">
                            <a href="{r["resource_url"]}" download="{r["title"]}" data-container="body" data-toggle="tooltip" title="このファイルを再ダウンロードする" name="{r["resource_url"]}">{r["title"]}</a>
                        </label>
                    </div>
                </div>
            </li>
            """
        html = html[:folder_i.end()+search_num] + add_html + html[folder_i.end()+search_num:]
    # html = f"""<span><i class="far fa-folder" style="font-size:medium;">{coursename}</i></span>
    #         """ + html
    html = f'<li class="list-group-item">{coursename}<ul>' + html + '</ul></li>'
    return html

def get_coursename(courseid):
    coursename = session.query(course.Course.coursename).filter(course.Course.course_id==courseid).first()
    return coursename[0]

def get_courseids(studentid):
    course_ids = session.query(studentcourse.Studentcourse.course_id).filter(studentcourse.Studentcourse.student_id==studentid).all()
    return list(course_ids)

def add_student(studentid, fullname):
    students = session.query(student.Student.student_id).all()
    isExist = False
    for i in students:
        if list(i)[0] == studentid:
            isExist = True
            break
    if isExist == False:
        new_student = student.Student(student_id=studentid, fullname=fullname)
        session.add(new_student)
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

def add_assignment(assignmentid, url,
                   title, limit_at, instructions, time_ms, modifieddate, courseid):
    assignments = session.query(assignment.Assignment.assignment_id).all()
    isExist = False
    need_update = False
    for i in assignments:
        if list(i)[0] == assignmentid:
            isExist = True
            assignment_md = session.query(assignment.Assignment.modifieddate).filter(
                assignment.Assignment.assignment_id == assignmentid).all()
            if list(assignment_md[0])[0] != modifieddate:
                need_update = True
            break
    if isExist == False:
        new_assignment = assignment.Assignment(assignment_id=assignmentid, url=url, title=title, \
                                               limit_at=limit_at, instructions=instructions, time_ms=time_ms/1000, modifieddate=modifieddate, course_id=courseid)
        session.add(new_assignment)
        session.commit()
    elif need_update:
        old_assignment = session.query(assignment.Assignment).filter(assignment.Assignment.assignment_id==assignmentid).first()
        old_assignment.url = url
        old_assignment.title = title
        old_assignment.limit_at = limit_at
        old_assignment.time_ms = time_ms
        old_assignment.modifieddate = modifieddate
        session.add(old_assignment)
        session.commit()
    return

def add_course(courseid, instructorid, \
               coursename, yearsemester, classschedule):
    courses = session.query(course.Course.course_id).all()
    isExist = False
    for i in courses:
        if list(i)[0] == courseid:
            isExist = True
            break
    if isExist == False:
        new_course = course.Course(course_id=courseid, instructor_id=instructorid, \
                                   coursename=coursename, yearsemester=yearsemester, classschedule=classschedule)
        session.add(new_course)
        session.commit()
    return


def add_student_assignment(studentid, data):
    """
        data:assignment_id, student_id, status
    """
    sa = session.query(
        studentassignment.Student_Assignment.assignment_id).filter(studentassignment.Student_Assignment.student_id == studentid).all()
    assignment_exist = False
    new_sa = []
    for item in data:
        for i in sa:
            if i.assignment_id == item["assignment_id"]:
                assignment_exist = True
                break
        if assignment_exist == False:
            new_sa.append(item)
    session.execute(studentassignment.Student_Assignment.__table__.insert(),new_sa)
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
    resource_exist = False
    sr = session.query(studentresource.Student_Resource).filter(studentresource.Student_Resource.student_id ==studentid).all()
    new_sr = []
    for item in data:
        for i in sr:
            if i.resource_url == item["resourceurl"]:
                resource_exist = True
                break
        if resource_exist == False:
            new_sr.append(item)
    session.execute(studentresource.Student_Resource.__table__.insert(),new_sr)
    session.commit()
    return


def add_resource(resourceurl, title, container, modifieddate, course_id):
    resources = session.query(resource.Resource.resource_url).all()
    isExist = False
    need_update = False
    for i in resources:
        if list(i)[0] == resourceurl:
            isExist = True
            resource_md = session.query(resource.Resource.modifieddate).filter(
                resource.Resource.resource_url==resourceurl)
            if list(resource_md[0])[0] != modifieddate:
                need_update = True
            break
    if isExist == False:
        new_resource = resource.Resource(resource_url=resourceurl, title=title, container=container, modifieddate=modifieddate, course_id=course_id)
        session.add(new_resource)
        session.commit()
    elif need_update:
        old_resource = session.query(resource.Resource).filter(
            resource.Resource.resource_url==resourceurl).first()
        old_resource.title = title
        old_resource.container = container
        old_resource.modifieddate = modifieddate
        old_resource.course_id = course_id
        session.add(old_resource)
        need_student_resource = session.query(studentresource.Student_Resource).filter(
            studentresource.Student_Resource.resource_url==resourceurl).all()
        for sr in need_student_resource:
            sr.status = 0
            session.add(sr)
        session.commit()
    return

def add_studentcourse(studentid, data):
    """
        data:[{student_id:"", course_id:""},{}]
    """
    sc = session.query(studentcourse.Studentcourse).filter(studentcourse.Studentcourse.student_id == studentid).all()
    course_exist = False
    new_sc = []
    for item in data:
        for i in sc:
            if i.course_id == item["course_id"]:
                course_exist = True
                break
        if course_exist == False:
            new_sc.append(item)
    session.excute(studentcourse.Studentcourse.__table__.insert(),new_sc)
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
    tasks = sorted(tasks, key=lambda x: x["deadline"])
    tasks = sorted(tasks, key=lambda x: order_status(x["status"]))
    return tasks


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

def remain_time(time_ms):
    ato = 'あと'
    now = floor(time.time())
    seconds = time_ms - now
    minutes = seconds/60
    hours = minutes/60
    days = hours/24
    weeks = days/7
    months = weeks/4

    if seconds < 0:
        return ''
    elif minutes < 1:
        return '1分未満'
    elif hours < 1:
        return ato + str(floor(minutes)) + '分'
    elif days < 1:
        return ato + str(floor(hours)) + '時間'
    elif weeks < 1:
        return ato + str(floor(days)) + '日'
    elif months < 1:
        remain_days = floor(days) - floor(weeks)*7
        if remain_days == 0:
            return ato + str(floor(weeks)) + '週間'
        else:
            return ato + str(floor(weeks)) + '週と' + \
                str(remain_days) + '日'
    else:
        return ato + '4週間以上'
