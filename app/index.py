from .models import student, assignment, course, studentassignment, instructor, studentcourse, resource, studentresource, assignment_attachment
from .settings import session
import re


def get_tasklist(studentid, mode=0):
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

    enrollments = session.query(studentassignment.Student_Assignment).filter(
        studentassignment.Student_Assignment.student_id == studentid).all()
    tasks = []
    for data in enrollments:
        task = {}
        task["status"] = data.status
        task["assignmentid"] = data.assignment_id
        assignmentdata = session.query(assignment.Assignment).filter(
            assignment.Assignment.assignment_id == data.assignment_id).all()
        task["taskname"] = assignmentdata[0].title
        task["deadline"] = assignmentdata[0].limit_at
        if mode == 0:
            task["time_left"] = remain_time(assignmentdata[0].time_ms)
        if mode == 1:
            task["instructions"] = assignmentdata[0].instructions
        coursedata = session.query(course.Course).filter(
            course.Course.course_id == data.course_id).all()
        task["subject"] = coursedata[0].coursename
        if mode == 1:
            task["classschedule"] = coursedata[0].classschedule
        tasks.append(task)
    return tasks

def get_courses_to_be_taken(studentid):
    data=[]
    courses = session.query(studentassignment.Student_Assignment).filter(
        studentassignment.Student_Assignment.student_id == studentid).all()
    for course in courses:
        if course.hide == 1:
            continue
        coursedata = session.query(course.Course).filter(
            course.Course.course_id == course.course_id).all()
        data.append(coursedata[0])
    return data

def setdefault_for_overview(data, studentid):
    days =["mon", "tue", "wed", "thu", "fri"]
    for day in days:
        for i in range(5):
            data.setdefault(day+str(i+1),{"subject": "", "shortname": "", "searchURL": "","tasks": []})
            data[day+str(i+1)]["tasks"] = sort_tasks(data[day+str(i+1)]["tasks"])
    data.setdefault("others",[])
    for subject in data["others"]:
        subject["tasks"] = sort_tasks(subject["tasks"])
    coursedata = get_courses_to_be_taken(studentid)
    for course in coursedata:
        add_in_others = False
        add_new_subject = False
        # 教科に時限情報がない場合
        if course.classschedule == "others":
            add_in_others = True
        else:
            if course.coursename != data[course.classschedule]["subject"] and course.coursename != "":
                add_in_others = True
            else:
                add_new_subject = True
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
                data["others"][index]["subject"] = course.coursename
                data["others"][index]["shortname"] = re.sub(
                    "\[.*\]", "", course.coursename)
                data["others"][index]["tasks"] = []

        elif add_new_subject == True:
            data[course.classschedule] = {}
            data[course.classschedule]["shorturl"] = ""
            data[course.classschedule]["subject"] = course.coursename
            data[course.classschedule]["shortname"] = re.sub(
                "\[.*\]", "", course.coursename)
            data[course.classschedule]["tasks"] = []
    return data


def task_arrange_for_overview(tasks):
    task_arranged = {"others": []}

    for task in tasks:
        # if task["status"] != "未":
        #     continue
        add_in_others = False
        add_new_subject = False
        # 教科に時限情報がない場合
        if task["classschedule"] == "others":
            add_in_others = True
        else:
            if task["classschedule"] in task_arranged.keys():
                if task["subject"] != task_arranged[task["classschedule"]]["subject"]:
                    add_in_others = True
            else:
                add_new_subject = True
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
                # 新しい教科を追加
                task_arranged["others"].append({})
                task_arranged["others"][index]["subject"] = task["subject"]
                task_arranged["others"][index]["shortname"] = re.sub(
                    "\[.*\]", "", task["subject"])
                task_arranged["others"][index]["tasks"] = [task]

        elif add_new_subject == True:
            task_arranged[task["classschedule"]] = {}
            task_arranged[task["classschedule"]]["shorturl"] = ""
            task_arranged[task["classschedule"]]["subject"] = task["subject"]
            task_arranged[task["classschedule"]]["shortname"] = re.sub(
                "\[.*\]", "", task["subject"])
            task_arranged[task["classschedule"]]["tasks"] = [task]
        else:
            task_arranged[task["classschedule"]]["tasks"].append(task)
    return task_arranged


def add_student(studentid, fullname):
    students = session.query(student.Student.student_id).all()
    isExist = False
    for i in students:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == studentid:
            isExist = True

    if isExist == False:
        new_student = student.Student(student_id=studentid, fullname=fullname)
        session.add(new_student)
        session.commit()

    return

def add_assignment_attachment(url, title, assignment_id):
    assignments = session.query(assignment_attachment.Assignment_attachment.assignment_url).all()
    isExist = False
    for i in assignments:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == url:
            isExist = True

    if isExist == False:
        new_assignment_attachment = assignment_attachment.Assignment_attachment(assignment_url=url, title=title, assignment_id=assignment_id)

        session.add(new_assignment_attachment)
        session.commit()

    return

def add_assignment(assignmentid, url,
                   title, limit_at, instructions, time_ms, modifieddate, courseid):
    assignments = session.query(assignment.Assignment.assignment_id).all()
    isExist = False
    for i in assignments:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == assignmentid:
            isExist = True

    if isExist == False:
        new_assignment = assignment.Assignment(assignment_id=assignmentid, url=url, title=title, \
            limit_at=limit_at, instructions=instructions, time_ms=time_ms/1000, modifieddate=modifieddate, course_id=courseid)

        session.add(new_assignment)
        session.commit()

    return

def add_course(courseid, instructorid, \
                    coursename, yearsemester, classschedule):
    courses = session.query(course.Course.course_id).all()
    isExist = False
    for i in courses:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == courseid:
            isExist = True

    if isExist == False:
        new_course = course.Course(course_id=courseid, instructor_id=instructorid, \
            coursename=coursename, yearsemester=yearsemester, classschedule=classschedule)
        session.add(new_course)
        session.commit()

    return


def add_student_assignment(assignment_id, student_id, status):
    enrollments_assignmentid = session.query(
        studentassignment.Student_Assignment.assignment_id).all()
    enrollments_studentid = session.query(
        studentassignment.Student_Assignment.student_id).all()
    isExist_assignmentid = False
    isExist_studentid = False
    for i in enrollments_assignmentid:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == assignment_id:
            isExist_assignmentid = True

    if isExist_assignmentid:
        for i in enrollments_studentid:
            i_str = str(i)
            i_str = i_str.replace('(', '')
            i_str = i_str.replace(')', '')
            i_str = i_str.replace('\'', '')
            i_str = i_str.replace(',', '')
            if i_str == student_id:
                isExist_studentid = True

    if isExist_studentid == False:
        new_enrollment = studentassignment.Student_Assignment(assignment_id=assignment_id, student_id=student_id, status=status)
        session.add(new_enrollment)
        session.commit()

    return


def add_instructor(instructorid, fullname, emailaddress):
    instructors = session.query(instructor.Instructor.instructor_id).all()
    isExist = False
    for i in instructors:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == instructorid:
            isExist = True

    if isExist == False:
        new_instructor = instructor.Instructor(instructor_id=instructorid, fullname=fullname, emailaddress=emailaddress)
        session.add(new_instructor)
        session.commit()

    return

def add_student_resource(resourceurl, studentid, status):
    sr_resourceurl = session.query(studentresource.Student_Resource.resourse_url).all()
    sr_studentid = session.query(studentresource.Student_Resource.student_id).all()
    isExist_resourceurl = False
    isExist_studentid = False
    for i in sr_resourceurl:
        i_str = str(i)
        i_str = i_str.replace('(','')
        i_str = i_str.replace(')','')
        i_str = i_str.replace('\'','')
        i_str = i_str.replace(',','')
        if i_str == resourceurl:
            isExist_resourceurl = True
        
    if isExist_resourceurl:
        for i in sr_studentid:
            i_str = str(i)
            i_str = i_str.replace('(','')
            i_str = i_str.replace(')','')
            i_str = i_str.replace('\'','')
            i_str = i_str.replace(',','')
            if i_str == studentid:
                isExist_studentid = True

    if isExist_studentid == False:
        new_sc = studentresource.Student_Resource(resource_url=resourceurl, student_id=studentid, status=status)
        session.add(new_sc)
        session.commit()
    
    return

def add_resource(resourceurl, title, container, modifieddate, course_id):
    resources = session.query(resource.Resource.resource_url).all()
    isExist = False
    for i in resources:
        i_str = str(i)
        i_str = i_str.replace('(','')
        i_str = i_str.replace(')','')
        i_str = i_str.replace('\'','')
        i_str = i_str.replace(',','')
        if i_str == resourceurl:
            isExist = True
    if isExist == False:
        new_resource = resource.Resource(resource_url=resourceurl, title=title, container=container, modifieddate=modifieddate, course_id=course_id)
        session.add(new_resource)
        session.commit()
    return

def add_studentcourse(student_id, course_id):
    sc_studentid = session.query(
        studentcourse.Studentcourse.student_id).all()
    sc_courseid = session.query(
        studentcourse.Studentcourse.course_id).all()
    isExist_studentid = False
    isExist_courseid = False
    for i in sc_courseid:
        i_str = str(i)
        i_str = i_str.replace('(', '')
        i_str = i_str.replace(')', '')
        i_str = i_str.replace('\'', '')
        i_str = i_str.replace(',', '')
        if i_str == course_id:
            isExist_courseid = True

    if isExist_courseid:
        for i in sc_studentid:
            i_str = str(i)
            i_str = i_str.replace('(', '')
            i_str = i_str.replace(')', '')
            i_str = i_str.replace('\'', '')
            i_str = i_str.replace(',', '')
            if i_str == student_id:
                isExist_studentid = True

    if isExist_studentid == False:
        new_sc = studentcourse.Studentcourse(student_id=student_id, course_id=course_id)
        session.add(new_sc)
        session.commit()
    return

def sort_tasks(tasks, show_only_unfinished = False, max_time_left = 1):
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

from math import *
import time
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
