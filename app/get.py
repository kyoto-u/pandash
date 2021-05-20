# データベース操作を伴い情報を取得する関数の一覧
#
from math import *
from .models import student, assignment, course, studentassignment, studentcourse, resource, studentresource
from .settings import SHOW_YEAR_SEMESTER, session, panda_url
from .original_classes import TimeLeft

def get_courseids(studentid):
    course_ids = session.query(studentcourse.Studentcourse.course_id).filter(studentcourse.Studentcourse.student_id==studentid).all()
    return [i.course_id for i in course_ids]

def get_coursename(courseid):
    coursename = session.query(course.Course.coursename).filter(course.Course.course_id==courseid).first()
    return coursename[0]

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

def get_student(studentid):
    studentdata = session.query(student.Student).filter(student.Student.student_id == studentid).all()
    if len(studentdata) != 0:
        studentdata = studentdata[0]
    else:
        studentdata = None
    return studentdata

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
        task["assignment_url"] = f'{panda_url}/portal/site/{task["course_id"]}/tool/{task["tool_id"]}?assignmentReference=/assignment/a/{task["course_id"]}/{task["assignmentid"]}&panel=Main&sakai_action=doView_submission'
        tasks.append(task)
    return tasks
