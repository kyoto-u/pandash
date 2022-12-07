# データベース操作を伴い情報を取得する関数の一覧
#
from math import *

from sqlalchemy.sql.expression import false

from app.models import forum
from .models import student, assignment, course, studentassignment, studentcourse, resource, studentresource, quiz, studentquiz, announcement, studentannouncement
from .models import comment, coursecomment
from .settings import panda_url
from .original_classes import TimeLeft ,Status
import datetime
import hashlib
from typing import List
import json

def get_announcements(studentid,show_only_unchecked, courseid, day, db_ses):
    enrollments = db_ses.query(studentannouncement.Student_Announcement).filter(
        studentannouncement.Student_Announcement.student_id == studentid).all()
    announcementids =[i.announcement_id for i in enrollments]
    course_to_be_taken=get_courses_to_be_taken(studentid, db_ses)
    courseids = [i.course_id for i in course_to_be_taken]
    announcementdata = db_ses.query(announcement.Announcement).filter(
        announcement.Announcement.announcement_id.in_(announcementids)).all()
    
    coursedata = db_ses.query(course.Course).filter(
            course.Course.course_id.in_(courseids)).all()
    
    returns = []
    for data in enrollments:
        if show_only_unchecked==1:
            if data.checked==1:
                continue
        anndata = [i for i in announcementdata if i.announcement_id == data.announcement_id]
        crsdata = [i for i in coursedata if i.course_id == anndata[0].course_id]
        
        if courseid != None:
            if courseid != anndata[0].course_id:
                continue
        if anndata[0].course_id not in courseids:
            continue
        if day != None:
            if day not in crsdata[0].classschedule:
                continue
        
        announce = {}
        announce["announcement_id"]=anndata[0].announcement_id
        announce["checked"]=data.checked
        announce["title"]=anndata[0].title
        announce["html_file"]=anndata[0].body
        announce["subject"]=crsdata[0].coursename
        announce["classschedule"]=crsdata[0].classschedule
        announce["course_id"]=anndata[0].course_id
        announce["publisher"]="xxxx"
        announce["time_ms"]=anndata[0].createddate
        announce["publish_date"]=datetime.datetime.fromtimestamp(anndata[0].createddate//1000).strftime("%Y/%m/%d %H:%M:%S")
        returns.append(announce)
    return returns

def get_announcement(studentid, announcementid, db_ses):
    # anm = db_ses.query(announcement.Announcement).filter(
    #     announcement.Announcement.announcement_id == announcementid).first()
    # course_to_be_taken = get_courses_to_be_taken(studentid)
    # courseids = [i.course_id for i in course_to_be_taken]

    st_ans = db_ses.query(studentannouncement.Student_Announcement).filter(
        studentannouncement.Student_Announcement.sa_id == f'{studentid}:{announcementid}').all()
    
    if len(st_ans) != 0:
        st_an = st_ans[0]
        anndata = db_ses.query(announcement.Announcement).filter(
            announcement.Announcement.announcement_id==announcementid).all()
        crsdata = db_ses.query(course.Course).filter(
            course.Course.course_id==anndata[0].course_id).all()
        announce = {}
        announce["announcement_id"]=anndata[0].announcement_id
        announce["checked"]=st_an.checked
        announce["title"]=anndata[0].title
        announce["html_file"]=anndata[0].body
        announce["subject"]=crsdata[0].coursename
        announce["classschedule"]=crsdata[0].classschedule
        announce["course_id"]=anndata[0].course_id
        announce["publisher"]="xxxx"
        announce["time_ms"]=anndata[0].createddate
        announce["publish_date"]=datetime.datetime.fromtimestamp(anndata[0].createddate//1000).strftime("%Y/%m/%d %H:%M:%S")
        return announce
    else:
        return {}



    # for courseid in courseids:
    #     if anm.course_id == courseid:
    #         return {"announcement_id":anm.announcement_id,"title":anm.title,"html_file":anm.body}
    # else:
    #     return {}


def get_assignments(studentid, db_ses, show_only_unfinished,courseid, day, mode,include_deleted = 0):
    if show_only_unfinished == False:
        enrollments = db_ses.query(studentassignment.Student_Assignment).filter(
            studentassignment.Student_Assignment.student_id == studentid).all()
    else:
        enrollments = db_ses.query(studentassignment.Student_Assignment).filter(
            studentassignment.Student_Assignment.student_id == studentid).filter(
                studentassignment.Student_Assignment.status == Status.NotYet.value).all()
    assignmentids =[i.assignment_id for i in enrollments]
    course_to_be_taken=get_courses_to_be_taken(studentid, db_ses)
    courseids = [i.course_id for i in course_to_be_taken]
    assignmentdata = db_ses.query(assignment.Assignment).filter(
        assignment.Assignment.assignment_id.in_(assignmentids)).all()
    
    coursedata = db_ses.query(course.Course).filter(
            course.Course.course_id.in_(courseids)).all()
    
    tasks = []
    for data in enrollments:
        if data.deleted==1:
            continue
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
        if include_deleted==0 and asmdata[0].deleted == 1:
            continue
        
        task = {}
        task["status"] = data.status
        task["taskname"] = asmdata[0].title
        task["time_ms"] = asmdata[0].time_ms
        task["assignmentid"] = data.assignment_id
        task["deadline"] = asmdata[0].limit_at
        if task["deadline"] == "2099-12-31T23:59:59Z":
            task["deadline"]="無期限"
        task["time_left"] = TimeLeft(asmdata[0].time_ms).time_left_to_str()
        task["clicked"] = data.clicked
        task["quiz"] = False
        if task["time_left"]["msg"] == "":
            task["status"]=Status.AlreadyDue.value
        if mode == 1:
            # overviewのtooltipsに使用
            task["instructions"] = asmdata[0].instructions

        task["subject"] = crsdata[0].coursename
        task["tool_id"] = crsdata[0].page_id
        task["course_id"] = crsdata[0].course_id
        if mode == 1:
            task["classschedule"] = crsdata[0].classschedule
        if show_only_unfinished==1:
            if task["status"]!=Status.NotYet.value:
                continue
        task["assignment_url"] = f'{panda_url}/portal/site/{task["course_id"]}/tool/{task["tool_id"]}?assignmentReference=/assignment/a/{task["course_id"]}/{task["assignmentid"]}&panel=Main&sakai_action=doView_submission'
        tasks.append(task)
    return tasks

# コメントを取得する courseid = None のときすべてのコメントを取得
def get_comments(studentid, courseid, db_ses):
    courseids = []
    if courseid:
        courseids.append(courseid)
    else:
        courses_to_be_taken=get_courses_to_be_taken(studentid, db_ses)
        courseids = [i.course_id for i in courses_to_be_taken]
    all_comments = []
    for courseid in courseids:
        coursecomemnts = db_ses.query(coursecomment.Course_Comment).filter(
            coursecomment.Course_Comment.course_id == courseid).all()
        commentids = [i.comment_id for i in coursecomemnts]
        # 全て取得せず　limit()で制限してページなどで分ける様にする場合は 降順で取得
        # commentdata = db_ses.query(comment.Comment).filter(
        #     comment.Comment.comment_id.in_(commentids)).order_by(comment.Comment.update_time.desc()).all()
        # 昇順で取得
        commentdata = db_ses.query(comment.Comment).filter(
               comment.Comment.comment_id.in_(commentids)).order_by(comment.Comment.update_time).limit(1000).all()
        comments = []
        index = 1
        for data in commentdata:
            # student_id のハッシュ化
            userid = hashlib.md5(data.sutdent_id.encode()).hexdigest()[:6]
            cmnt = {"commentid":data.comment_id,"userid":userid,"reply_to":data.reply_to,"update_time":data.update_time,"content":data.content,"index":index}
            index += 1
            comments.append(cmnt)
        coursename = get_coursename(courseid, db_ses)
        all_comments.append({"roomname":coursename, "commnets":comments})
    return all_comments

def get_chatrooms(studentid, courseid, db_ses):
    courseids = []
    chatrooms = []
    if courseid:
        courseids.append(courseid)
    else:
        courses_to_be_taken=get_courses_to_be_taken(studentid, db_ses)
        courseids = [i.course_id for i in courses_to_be_taken]
    for courseid in courseids:
        crs = db_ses.query(course.Course).filter(course.Course.course_id==courseid).first()
        coursename = crs[0].coursename
        link = f"/chat/course/{courseid}"
        last_update = str(datetime.datetime.fromtimestamp(crs[0].comment_last_update,datetime.timezone(datetime.timedelta(hours=9))))[:6]
        checked = db_ses.query(studentcourse.Studentcourse.comment_checked).filter(studentcourse.Studentcourse.sc_id==f"{studentid}:{courseid}").first()[0]
        chatrooms.append({"name":coursename,"link":link,"checked":checked,"last_update":last_update})
    return chatrooms


def get_courseids(studentid: str, db_ses, include_deleted = 0) ->List[str]:
    """
        データベース上でstudent_idと結びつけられたcourse_idを集めてリストを返す

        ユーザーの非表示に設定している教科や表示開講期外のものも収集される
    """
    course_ids = db_ses.query(studentcourse.Studentcourse).filter(studentcourse.Studentcourse.student_id==studentid).all()
    return [i.course_id for i in course_ids if include_deleted == 1 or i.deleted == 0]

def get_coursename(courseid: str, db_ses) -> str:
    """
        データベースを参照してcourse_idからcoursenameを取得する
    """
    coursename = db_ses.query(course.Course.coursename).filter(course.Course.course_id==courseid).first()
    return coursename[0]

def get_courses_id_to_be_taken(studentid, db_ses, mode=0,include_deleted=0) ->List[str]:
    """
        データベース上でstudent_idと結びつけられたcourse_idを集めてリストを返す

        表示開講期外のものは収集しない
        mode:
        0 -> ユーザーが非表示設定にしているものを収集しない
        1 -> ユーザーが非表示設定にしているものも収集する
        include_deleted:
        0 -> ユーザーが履修取り消ししたものを収集しない
        1 -> ユーザーが履修取り消ししたものも収集する
    """
    data=[]
    courses = db_ses.query(studentcourse.Studentcourse).filter(
        studentcourse.Studentcourse.student_id == studentid).all()
    show_year_semester = get_show_year_semester()
    for i in courses:
        if mode==0 and i.hide == 1:
            continue
        if include_deleted==0 and i.deleted == 1:
            continue
        coursedata = db_ses.query(course.Course).filter(
            course.Course.course_id == i.course_id).all()
        if coursedata[0].yearsemester in show_year_semester:
            data.append(coursedata[0].course_id)
    return data

# mode = 1 のときはhideのものも取得
def get_courses_to_be_taken(studentid, db_ses, mode = 0,include_deleted = 0,return_data = 'course'):
    """
        データベース上でstudent_idと結びつけられた教科情報を集めてリストを返す

        表示開講期外のものは収集しない
        mode:
        0 -> ユーザーが非表示設定にしているものを収集しない
        1 -> ユーザーが非表示設定にしているものも収集する
        include_deleted:
        0 -> ユーザーが履修取り消ししたものを収集しない
        1 -> ユーザーが履修取り消ししたものも収集する
        return_data:戻り値の型
        'course' -> course.Course
        'student_course' -> studentcourse.Studentcourse
    """
    data=[]
    courses = db_ses.query(studentcourse.Studentcourse).filter(
        studentcourse.Studentcourse.student_id == studentid).all()
    show_year_semester = get_show_year_semester()
    for i in courses:
        if mode==0 and i.hide==1:
            continue
        if include_deleted==0 and i.deleted == 1:
            continue
        coursedata = db_ses.query(course.Course).filter(
            course.Course.course_id == i.course_id).all()
        if coursedata[0].yearsemester in show_year_semester:
            if return_data == 'course':
                data.append(coursedata[0])
            elif return_data == 'student_course':
                data.append(i)
            else:
                #一応courseを返す
                data.append(coursedata[0])
    return data

def get_forums(student_id,show_only_not_replied,db_ses,all=false):
    if all:
        if show_only_not_replied == False:
            frms = db_ses.query(forum.Forum).all()
        else:
            frms = db_ses.query(forum.Forum).filter(
                forum.Forum.replied==1).all()
    else:
        if show_only_not_replied == False:
            frms = db_ses.query(forum.Forum).filter(forum.Forum.student_id==student_id).all()
        else:
            frms = db_ses.query(forum.Forum).filter(forum.Forum.replied==1).filter(forum.Forum.student_id==student_id).all()
    frmsdata = []
    for frm in frms:
        frmdata = {}
        frmdata["forum_id"] = frm.forum_id
        frmdata["createdate_ms"] = frm.createdate
        frmdata["createdate"] = str(datetime.datetime.fromtimestamp(frm.createdate//1000,datetime.timezone(datetime.timedelta(hours=9))))[:-6]
        frmdata["student_id"] = frm.student_id
        frmdata["title"] = frm.title
        frmdata["contents"] = frm.contents
        frmdata["reply_contents"] = frm.reply_contents
        frmdata["replied"] = frm.replied
        frmsdata.append(frmdata)
    return frmsdata


def get_quizzes(studentid, show_only_unfinished,courseid, day, mode,db_ses,include_deleted = 0):
    # 未完了以外の課題も表示するかによってテーブルからの取り出し方が変わる
    if show_only_unfinished == False:
        enrollments = db_ses.query(studentquiz.Student_Quiz).filter(
            studentquiz.Student_Quiz.student_id == studentid).all()
    else:
        enrollments = db_ses.query(studentquiz.Student_Quiz).filter(
            studentquiz.Student_Quiz.student_id == studentid).filter(
                studentquiz.Student_Quiz.status == Status.NotYet.value).all()
    # quizのidだけを収集したリスト、courseのidだけを収集したリストを作成
    quizids =[i.quiz_id for i in enrollments]
    course_to_be_taken=get_courses_to_be_taken(studentid, db_ses)
    courseids = [i.course_id for i in course_to_be_taken]
    
    # idのリストで絞り込んでquiz、courseの詳細情報を取得
    quizdata = db_ses.query(quiz.Quiz).filter(
        quiz.Quiz.quiz_id.in_(quizids)).all()
    coursedata = db_ses.query(course.Course).filter(
            course.Course.course_id.in_(courseids)).all()
    # taskをまとめたリストに条件を満たすものを追加していく
    tasks = []
    for data in enrollments:
        if data.deleted==1:
            continue
        # 各quizに対してquizの詳細データ、courseの詳細データがあるか探す
        qizdata = [i for i in quizdata if i.quiz_id == data.quiz_id]
        crsdata = [i for i in coursedata if i.course_id == qizdata[0].course_id]
        
        if courseid != None:
            # courseidでの絞り込み
            if courseid != qizdata[0].course_id:
                continue
        if qizdata[0].course_id not in courseids:
            # courseが何らかの理由（開講期や個人設定）で取得対象外であった場合は追加しない
            continue
        if day != None:
            # day(曜日)での絞り込み
            if day not in crsdata[0].classschedule:
                continue
        if include_deleted==0 and qizdata[0].deleted == 1:
            continue
        # 注：taskの構造はassignmentと構造をそろえているために一部の名称が不適切である
        task = {}
        task["status"] = data.status
        task["taskname"] = qizdata[0].title
        task["assignmentid"] = data.quiz_id
        task["deadline"] = qizdata[0].limit_at
        task["time_ms"] = qizdata[0].time_ms
        if task["deadline"] == "2099-12-31T23:59:59Z":
            task["deadline"]="無期限"
        task["time_left"] = TimeLeft(qizdata[0].time_ms).time_left_to_str()
        task["clicked"] = data.clicked
        task["quiz"] = True
        if task["time_left"]["msg"] == "":
            task["status"]=Status.AlreadyDue.value
        if mode == 1:
            # overviewのtooltipsに使用
            task["instructions"] = qizdata[0].instructions

        task["subject"] = crsdata[0].coursename
        task["tool_id"] = crsdata[0].quiz_page_id
        task["course_id"] = crsdata[0].course_id
        if mode == 1:
            task["classschedule"] = crsdata[0].classschedule
        if show_only_unfinished==1:
            if task["status"]!=Status.NotYet.value:
                continue
        task["assignment_url"] = f'{panda_url}/portal/site/{task["course_id"]}/tool-reset/{task["tool_id"]}'
        tasks.append(task)
    return tasks


def get_resource_list(studentid, db_ses, course_id=None, day=None,include_deleted=0):
    srs = db_ses.query(studentresource.Student_Resource).filter(
        studentresource.Student_Resource.student_id == studentid).all()
    
    resource_urls = [i.resource_url for i in srs]
    
    resourcedata = db_ses.query(resource.Resource).filter(
        resource.Resource.resource_url.in_(resource_urls)).all()
    course_to_be_taken=get_courses_to_be_taken(studentid, db_ses)
    sorted_courseids = sort_courses_by_classschedule(course_to_be_taken)
    coursedata = db_ses.query(course.Course).filter(
        course.Course.course_id.in_(sorted_courseids)).all()
    resource_list={i:[] for i in sorted_courseids}

    for data in srs:
        if data.deleted==1:
            continue
        rscdata = [i for i in resourcedata if i.resource_url == data.resource_url]
        crsdata = [i for i in coursedata if i.course_id == rscdata[0].course_id]

        if course_id != None:
            if course_id != rscdata[0].course_id:
                continue
        if rscdata[0].course_id not in sorted_courseids:
            continue
        if day !=None:
            if day not in crsdata[0].classschedule:
                continue
        if include_deleted==0 and rscdata[0].deleted == 1:
            continue
        resource_dict = {}
        resource_dict["resource_url"] = data.resource_url
        resource_dict["title"] = rscdata[0].title
        resource_dict["container"] = rscdata[0].container
        resource_dict["modifieddate"] = rscdata[0].modifieddate
        resource_dict["status"] = data.status
        resource_list[rscdata[0].course_id].append(resource_dict)
    return resource_list

def sort_courses_by_classschedule(course_to_be_taken, mode="course_id"):
    courses = [(i.course_id,i.coursename,i.classschedule) for i in course_to_be_taken]
    order = ['mon1','mon2','mon3','mon4','mon5','tue1','tue2','tue3','tue4','tue5','wed1','wed2','wed3','wed4','wed5',\
        'thu1','thu2','thu3','thu4','thu5','fri1','fri2','fri3','fri4','fri5','oth']
    sorted_courses = sorted(courses,key=lambda x:order.index(x[2]))
    if mode == "course_id":
        return [i[0] for i in sorted_courses]
    elif mode == "course_id_name":
        return [(i[0],i[1]) for i in sorted_courses]
    else:
        return []

def get_student(studentid: str, db_ses) -> student.Student:
    """
        データベースを参照してstudent_idからstudentの情報を返す
    """
    studentdata = db_ses.query(student.Student).filter(student.Student.student_id == studentid).all()
    if len(studentdata) != 0:
        studentdata = studentdata[0]
    else:
        studentdata = None
    return studentdata


def get_show_year_semester():
    """
        show_year_semesterを取得する
    """
    with open('./year_semester.json', 'r') as f:
        year_semesters = json.load(f)
        show_year_semester = year_semesters["show_year_semester"]
        return show_year_semester
