# データベースの情報を書き換える関数の一覧
#

from .models import student, assignment, course, studentassignment, instructor, studentcourse, resource, studentresource, assignment_attachment,\
                    forum, quiz, studentquiz, comment, coursecomment,announcement,studentannouncement
from .settings import session
from .get import get_courseids
import time
from .original_classes import Status

def add_announcement(studentid, data,db_ses):
    course_ids = get_courseids(studentid,db_ses)
    announcements = db_ses.query(
        announcement.Announcement).filter(announcement.Announcement.course_id.in_(course_ids)).all()
    new_announcement=[]
    upd_announcement = []
    for item in data:
        announcement_exist = False
        update=False
        if item["course_id"] not in course_ids:
            continue
        for i in announcements:
            if i.announcement_id == item["announcement_id"]:
                announcement_exist = True
                if item["createddate"] !=i.createddate:
                    update=True
                break
        if announcement_exist == False:
            new_announcement.append(item)
        elif update == True:
            upd_announcement.append(item)
    if len(new_announcement) != 0:
        db_ses.execute(announcement.Announcement.__table__.insert(),new_announcement)
    if len(upd_announcement) != 0:
        db_ses.bulk_update_mappings(announcement.Announcement, upd_announcement)
    db_ses.commit()
    return

def add_assignment(studentid, data, db_ses, allow_delete=1):
    course_ids = get_courseids(studentid,db_ses)
    assignments = db_ses.query(
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
                if item["modifieddate"] != i.modifieddate:
                    update=True
                # もし削除扱いになっている場合はそれを直すためにupdateする
                if i.deleted == 1:
                    item["deleted"]=0
                    update = True
                break
        if assignment_exist == False:
            new_asm.append(item)
        elif update == True:
            upd_asm.append(item)
    # if allow_delete == 1:
    #     # 逆に、テーブルに格納されている課題情報について、今回のAPIで取得できたかを調べる。
    #     now = int(time.time())
    #     for i in assignments:
    #         assignment_deleted = True
    #         for item in data:
    #             if item["assignment_id"] == i.assignment_id:
    #                 assignment_deleted = False
    #                 break
    #         if now>i.time_ms:
    #             # 期限切れなら課題削除ではない可能性が高い
    #             assignment_deleted = False
    #         if assignment_deleted and i.deleted == 0:
    #             upd_asm.append({"assignment_id": i.assignment_id, "deleted": 1})
    
    if len(new_asm) != 0:
        db_ses.execute(assignment.Assignment.__table__.insert(),new_asm)
    if len(upd_asm) != 0:
        db_ses.bulk_update_mappings(assignment.Assignment, upd_asm)
    db_ses.commit()
    return

def add_assignment_attachment(url, title, assignment_id, db_ses):
    assignments = db_ses.query(assignment_attachment.Assignment_attachment.assignment_url).all()
    isExist = False
    for i in assignments:
        if list(i)[0] == url:
            isExist = True
            break
    if isExist == False:
        new_assignment_attachment = assignment_attachment.Assignment_attachment(assignment_url=url, title=title, assignment_id=assignment_id)
        db_ses.add(new_assignment_attachment)
        db_ses.commit()
    return


def add_comment(student_id, reply_to, content, db_ses):
    update_time = int(time.time())
    new_comment = comment.Comment(student_id=student_id, reply_to=reply_to, update_time=update_time, content=content)
    try:
        db_ses.add(new_comment)
        db_ses.commit()
    # primarykeyが同じ時について繰り返し処理にする
    except:
        db_ses.add(new_comment)
        db_ses.commit()
    db_ses.refresh(new_comment)
    return new_comment.comment_id


def add_course(studentid, data, db_ses):
    course_ids = get_courseids(studentid, db_ses)
    courses = db_ses.query(
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
        db_ses.execute(course.Course.__table__.insert(),new_crs)
    if len(upd_crs) != 0:
        db_ses.bulk_update_mappings(course.Course, upd_crs)
    db_ses.commit()
    return


def add_coursecomment(studentid, comment_id, course_id, db_ses):
    course_ids = get_courseids(studentid, db_ses)
    if course_id not in course_ids:
        return False
    new_coursecomment = coursecomment.Coursecomment(comment_id=comment_id, course_id=course_id)
    # course table の comment_lat_update を更新する
    last_update = int(time.time())
    crs = db_ses.query(course.Course).filter(course.Course.course_id).first()
    crs.comment_last_update = last_update
    db_ses.add(new_coursecomment)
    db_ses.commit()
    return True
    

def add_forum(studentid,title,contents, db_ses):
    inq = forum.Forum()
    inq.student_id = studentid
    inq.title = title
    inq.contents = contents
    db_ses.add(inq)
    db_ses.commit()
    return f"""
    -----FORUM-----
    STUDENT: {studentid},
    TITLE: {title},
    CONTENTS: {contents}
    ---------------"""

def add_instructor(instructorid, fullname, emailaddress, db_ses):
    instructors = db_ses.query(instructor.Instructor.instructor_id).all()
    isExist = False
    for i in instructors:
        if list(i)[0] == instructorid:
            isExist = True
            break
    if isExist == False:
        new_instructor = instructor.Instructor(instructor_id=instructorid, fullname=fullname, emailaddress=emailaddress)
        db_ses.add(new_instructor)
        db_ses.commit()
    return

def add_quiz(studentid, data, db_ses, allow_delete=1):
    course_ids = get_courseids(studentid,db_ses)
    quizzes = db_ses.query(
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
                if item["modifieddate"] != i.modifieddate:
                    update=True
                # もし削除扱いになっている場合はそれを直すためにupdateする
                if i.deleted == 1:
                    item["deleted"]=0
                    update = True
                break
        if quiz_exist == False:
            new_quiz.append(item)
        elif update == True:
            upd_quiz.append(item)
    # if allow_delete == 1:
    #     # 逆に、テーブルに格納されている課題情報について、今回のAPIで取得できたかを調べる。
    #     now = int(time.time())
    #     for i in quizzes:
    #         quiz_deleted = True
    #         for item in data:
    #             if item["quiz_id"] == i.quiz_id:
    #                 quiz_deleted = False
    #                 break
    #         if now>i.time_ms:
    #             # 期限切れなら課題削除ではない可能性が高い
    #             quiz_deleted = False
    #         if quiz_deleted and i.deleted == 0:
    #             upd_quiz.append({"quiz_id": i.quiz_id, "deleted": 1})
    if len(new_quiz) != 0:
        db_ses.execute(quiz.Quiz.__table__.insert(),new_quiz)
    if len(upd_quiz) != 0:
        db_ses.bulk_update_mappings(quiz.Quiz, upd_quiz)
    db_ses.commit()
    return

def add_resource(studentid, data, db_ses, allow_delete=1):
    course_ids = get_courseids(studentid, db_ses)
    resources = db_ses.query(
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
                if item["modifieddate"] != i.modifieddate:
                    update=True
                # もし削除扱いになっている場合はそれを直すためにupdateする
                if i.deleted == 1:
                    item["deleted"]=0
                    update = True
                break
        if resource_exist == False:
            new_res.append(item)
        elif update == True:
            upd_res.append(item)
    # if allow_delete == 1:
    #     # 逆に、テーブルに格納されている履修情報について、今回のAPIで取得できたかを調べる。
    #     for i in resources:
    #         resource_deleted = True
    #         for item in data:
    #             if item["resource_url"] == i.resource_url:
    #                 resource_deleted = False
    #                 break
    #         if resource_deleted and i.deleted == 0:
    #             upd_res.append({"resource_url": i.resource_url, "deleted": 1})
    
    if len(new_res) != 0:
        db_ses.execute(resource.Resource.__table__.insert(),new_res)
    if len(upd_res) != 0:
        db_ses.bulk_update_mappings(resource.Resource, upd_res)
    db_ses.commit()
    return
  
def add_student(studentid, fullname, db_ses, last_update = 0, last_update_subject = 0, language = "ja"):
    students = db_ses.query(student.Student.student_id).all()
    isExist = False
    for i in students:
        if list(i)[0] == studentid:
            isExist = True
            break
    new_student = {"student_id":studentid, "fullname":fullname,"last_update":last_update, "last_update_subject":last_update_subject,"language":language}
    if isExist == False:
        db_ses.execute(student.Student.__table__.insert(),new_student)
    else:
        db_ses.bulk_update_mappings(student.Student, [new_student])
    db_ses.commit()
    return

def add_studentcourse(studentid, data, db_ses, allow_delete = 1):
    """
        学生の履修状況をテーブルに追加する

        data: [{"sc_id":"","student_id":"", "course_id":""},{}]
        allow_delete: 逆にdataにない情報を削除する
        APIなどで全取得したデータの場合は1、そうでない場合は0にする
    """
    sc = db_ses.query(studentcourse.Studentcourse).filter(studentcourse.Studentcourse.student_id == studentid).all()
    new_sc = []
    upd_sc = []
    # APIで取得した履修情報について、既にテーブルに格納されているか調べる
    for item in data:
        course_exist = False
        update = False
        for i in sc:
            if i.course_id == item["course_id"]:
                course_exist = True

                # もし履修取り消し扱いになっている場合はそれを直すためにupdateする
                if i.deleted == 1:
                    update = True
                break
        
        # 追加・更新リストに上の結果に応じて加える
        if not course_exist:
            new_sc.append(item)
        if update:
            upd_sc.append({"sc_id": item["sc_id"], "deleted": 0})

    if allow_delete == 1:
        # 逆に、テーブルに格納されている履修情報について、今回のAPIで取得できたかを調べる。
        for i in sc:
            course_deleted = True
            for item in data:
                if item["course_id"] == i.course_id:
                    course_deleted = False
                    break
            if course_deleted and i.deleted == 0:
                upd_sc.append({"sc_id": i.sc_id, "deleted": 1})
    if len(new_sc) != 0:
        db_ses.execute(studentcourse.Studentcourse.__table__.insert(),new_sc)
    if len(upd_sc) != 0:
        db_ses.bulk_update_mappings(studentcourse.Studentcourse, upd_sc)
    db_ses.commit()
    return

def add_student_announcement(studentid, data, db_ses):
    """
        data:announcement_id, student_id, status
    """
    sa = db_ses.query(
        studentannouncement.Student_Announcement).filter(studentannouncement.Student_Announcement.student_id == studentid).all()
    course_ids = get_courseids(studentid, db_ses)
    new_sa = []
    upd_sa = []
    for item in data:
        announcement_exist = False
        update=False
        if not item["course_id"] in course_ids:
            continue
        for i in sa:
            if i.announcement_id == item["announcement_id"]:
                announcement_exist = True
                break
        if announcement_exist == False:
            new_sa.append(item)
        elif update == True:
            upd_sa.append(item)
    if len(new_sa) != 0:
        db_ses.execute(studentannouncement.Student_Announcement.__table__.insert(),new_sa)
    if len(upd_sa) != 0:
        db_ses.bulk_update_mappings(studentannouncement.Student_Announcement, upd_sa)
    db_ses.commit()
    return

def add_student_assignment(studentid, data, db_ses,allow_delete=1):
    """
        data:assignment_id, student_id, status
    """
    sa = db_ses.query(
        studentassignment.Student_Assignment).filter(studentassignment.Student_Assignment.student_id == studentid).all()
    course_ids = get_courseids(studentid,db_ses)
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

                # もし削除扱いになっている場合はそれを直すためにupdateする
                if i.deleted == 1:
                    update = True

                break
        if assignment_exist == False:
            new_sa.append(item)
        elif update == True:
            upd_sa.append(item)
    if allow_delete == 1:
        # 逆に、テーブルに格納されている履修情報について、今回のAPIで取得できたかを調べる。
        for i in sa:
            assignment_deleted = True
            for item in data:
                if item["sa_id"] == i.sa_id:
                    assignment_deleted = False
                    break
            if assignment_deleted and i.deleted == 0:
                upd_sa.append({"sa_id": i.sa_id, "deleted": 1})
    if len(new_sa) != 0:
        db_ses.execute(studentassignment.Student_Assignment.__table__.insert(),new_sa)
    if len(upd_sa) != 0:
        db_ses.bulk_update_mappings(studentassignment.Student_Assignment, upd_sa)
    db_ses.commit()
    return

def add_student_quiz(studentid, data, db_ses,allow_delete=1):
    """
        data:quiz_id, student_id, status
    """
    sq = db_ses.query(
        studentquiz.Student_Quiz).filter(studentquiz.Student_Quiz.student_id == studentid).all()
    course_ids = get_courseids(studentid, db_ses)
    new_sq = []
    upd_sq = []
    for item in data:
        quiz_exist = False
        update=False
        if not item["course_id"] in course_ids:
            continue
        for i in sq:
            if i.quiz_id == item["quiz_id"]:
                quiz_exist = True

                # もし削除扱いになっている場合はそれを直すためにupdateする
                if i.deleted == 1:
                    update = True
                
                break
        if quiz_exist == False:
            new_sq.append(item)
        elif update == True:
            upd_sq.append(item)
    if allow_delete == 1:
        # 逆に、テーブルに格納されている情報について、今回のAPIで取得できたかを調べる。
        for i in sq:
            quiz_deleted = True
            for item in data:
                if item["sq_id"] == i.sq_id:
                    quiz_deleted = False
                    break
            if quiz_deleted and i.deleted == 0:
                upd_sq.append({"sq_id": i.sq_id, "deleted": 1})
    if len(new_sq) != 0:
        db_ses.execute(studentquiz.Student_Quiz.__table__.insert(),new_sq)
    if len(upd_sq) != 0:
        db_ses.bulk_update_mappings(studentquiz.Student_Quiz, upd_sq)
    db_ses.commit()
    return

def add_student_resource(studentid,data, db_ses,allow_delete=1):
    """
        data: resourceurl, studentid, status
    """
    sr = db_ses.query(studentresource.Student_Resource).filter(studentresource.Student_Resource.student_id ==studentid).all()
    course_ids = get_courseids(studentid, db_ses)
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
                if item["status"] !=0 and i.status ==0:
                    update=True
                # もし削除扱いになっている場合はそれを直すためにupdateする
                if i.deleted == 1:
                    update = True
                break
        if resource_exist == False:
            new_sr.append(item)
        elif update == True:
            upd_sr.append({"sr_id":item["sr_id"],"deleted":0})
    if allow_delete == 1:
        # 逆に、テーブルに格納されている情報について、今回のAPIで取得できたかを調べる。
        for i in sr:
            resource_deleted = True
            for item in data:
                if item["sr_id"] == i.sr_id:
                    resource_deleted = False
                    break
            if resource_deleted and i.deleted == 0:
                upd_sr.append({"sr_id": i.sr_id, "deleted": 1})
    if len(new_sr) != 0:
        db_ses.execute(studentresource.Student_Resource.__table__.insert(),new_sr)
    if len(upd_sr) != 0:
        db_ses.bulk_update_mappings(studentresource.Student_Resource, upd_sr)
    db_ses.commit()
    return
  
#update

def update_resource_status(studentid, resourceids: list, db_ses):
    srs = db_ses.query(studentresource.Student_Resource.resource_url, studentresource.Student_Resource.sr_id).filter(
        studentresource.Student_Resource.student_id == studentid).all()
    update_list = []
    for r_id in resourceids:
        sr_id = f'{studentid}:{r_id}'
        update_list.append({"sr_id":sr_id, "status":1})
    db_ses.bulk_update_mappings(studentresource.Student_Resource, update_list)
    db_ses.commit()
    return

def update_student_course_hide(student_id, course_list, hide, db_ses):
    update_list = []
    for coursedata in course_list:
        sc_id = f'{student_id}:{coursedata}'
        update_list.append({"sc_id":sc_id,"hide":hide})
    db_ses.bulk_update_mappings(studentcourse.Studentcourse, update_list)
    db_ses.commit()
    return

def update_student_needs_to_update_sitelist(student_id,db_ses, need_to_update_sitelist=0):
    st = db_ses.query(student.Student).filter(student.Student.student_id==student_id).first()
    st.need_to_update_sitelist = need_to_update_sitelist
    db_ses.commit()
    return

def update_student_show_already_due(student_id,db_ses,show_already_due=0):
    st = db_ses.query(student.Student).filter(student.Student.student_id==student_id).first()
    st.show_already_due = show_already_due
    db_ses.commit()
    return

def update_task_clicked_status(studentid, taskids:list,db_ses, mode="task"):
    update_list = []
    if mode == "task":
        for t_id in taskids:
            sa_id = f'{studentid}:{t_id}'
            update_list.append({"sa_id":sa_id, "clicked":1})
        db_ses.bulk_update_mappings(studentassignment.Student_Assignment, update_list)
    elif mode == "quiz":
        for t_id in taskids:
            sq_id = f'{studentid}:{t_id}'
            update_list.append({"sq_id":sq_id, "clicked":1})
        db_ses.bulk_update_mappings(studentquiz.Student_Quiz, update_list)
    db_ses.commit() 
    return

def update_task_status(studentid, taskids: list,db_ses, mode=0, taskmode="task"):
    update_list = []
    status = Status.NotYet.value
    if mode==0:
        status = Status.Done.value
    if taskmode == "task":
        for t_id in taskids:
            sa_id = f'{studentid}:{t_id}'
            update_list.append({"sa_id":sa_id, "status":status})
        db_ses.bulk_update_mappings(studentassignment.Student_Assignment, update_list)
    elif taskmode == "quiz":
        for t_id in taskids:
            sq_id = f'{studentid}:{t_id}'
            update_list.append({"sq_id":sq_id, "status":status})
        db_ses.bulk_update_mappings(studentquiz.Student_Quiz, update_list)
    db_ses.commit()
    return

# コースのコメントをチェックしたときに実行
def update_comment_checked(studentid, courseid,db_ses):
    sc_id = f"{studentid}:{courseid}"
    sc = db_ses.query(studentcourse.Studentcourse).filter(studentcourse.Studentcourse.sc_id==sc_id).first()
    sc.comment_checked = 1
    db_ses.commit()
    return

# コースのコメントが追加されたときに実行
def update_comment_unchecked(courseid, db_ses):
    sc_ids = db_ses.query(studentcourse.Studentcourse.sc_id).filter(
        studentcourse.Studentcourse.course_id==courseid).all()
    update_list = []
    for sc_id in sc_ids:
        update_list.append({"sc_id":sc_id, "comment_checked":0})
    db_ses.bulk_update_mappings(studentcourse.Studentcourse, update_list)
    db_ses.commit()
    return