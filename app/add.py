# データベースの情報を書き換える関数の一覧
#

from .models import student, assignment, course, studentassignment, instructor, studentcourse, resource, studentresource, assignment_attachment, forum,quiz,studentquiz
from .settings import session
from .get import get_courseids
from .original_classes import Status

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

def add_quiz(studentid, data, last_update):
    course_ids = get_courseids(studentid)
    quizzes = session.query(
        quiz.Quiz).filter(quiz.Quiz.course_id.in_(course_ids)).all()
    new_quiz=[]
    upd_quiz = []
    for item in data:
        quiz_exist = False
        update=False
        if item["course_id"] not in course_ids:
            continue
        for i in quizzes:
            if i.quiz_id == item["quiz_id"]:
                quiz_exist = True
                if item["modifieddate"] > last_update:
                    update=True
                break
        if quiz_exist == False:
            new_quiz.append(item)
        elif update == True:
            upd_quiz.append(item)
    if len(new_quiz) != 0:
        session.execute(quiz.Quiz.__table__.insert(),new_quiz)
    if len(upd_quiz) != 0:
        session.bulk_update_mappings(quiz.Quiz, upd_quiz)
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
                if item["status"] !=Status.AlreadyDue.value:
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

def add_student_quiz(studentid, data, last_update):
    """
        data:quiz_id, student_id, status
    """
    sa = session.query(
        studentquiz.Student_Quiz).filter(studentquiz.Student_Quiz.student_id == studentid).all()
    course_ids = get_courseids(studentid)
    new_sq = []
    upd_sq = []
    for item in data:
        quiz_exist = False
        update=False
        if not item["course_id"] in course_ids:
            continue
        for i in sa:
            if i.quiz_id == item["quiz_id"]:
                quiz_exist = True
                if item["status"] !=Status.AlreadyDue.value:
                    update=True
                break
        if quiz_exist == False:
            new_sq.append(item)
        elif update == True:
            upd_sq.append(item)
    if len(new_sq) != 0:
        session.execute(studentquiz.Student_Quiz.__table__.insert(),new_sq)
    if len(upd_sq) != 0:
        session.bulk_update_mappings(studentquiz.Student_Quiz, upd_sq)
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
  
#update

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

def update_student_course_hide(student_id, course_list, hide):
    update_list = []
    for coursedata in course_list:
        sc_id = f'{student_id}:{coursedata}'
        update_list.append({"sc_id":sc_id,"hide":hide})
    session.bulk_update_mappings(studentcourse.Studentcourse, update_list)
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

def update_task_clicked_status(studentid, taskids:list):
    update_list = []
    for t_id in taskids:
        sa_id = f'{studentid}:{t_id}'
        update_list.append({"sa_id":sa_id, "clicked":1})
    session.bulk_update_mappings(studentassignment.Student_Assignment, update_list)
    session.commit() 
    return

def update_task_status(studentid, taskids: list, mode=0):
    update_list = []
    status = Status.NotYet.value
    if mode==0:
        status = Status.Done.value
    for t_id in taskids:
        sa_id = f'{studentid}:{t_id}'
        update_list.append({"sa_id":sa_id, "status":status})
    session.bulk_update_mappings(studentassignment.Student_Assignment, update_list)
    session.commit()
    return
