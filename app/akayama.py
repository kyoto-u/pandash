from flask import Flask, request, render_template, url_for, redirect
import logging
from pprint import pprint
import time


app = Flask(__name__)

def get_announcement(id):
    result = {}
    result["title"] = "お知らせ"+str(id)
    result["subject"] = "test"
    result["publish_date"] = "2022/02/07"
    result["html_file"] = "<h1>hogehoge" + str(id) + "</h1>"
    return result

@app.route('/manage_reply', methods=['POST'])
def manage_reply():
    reply_content = request.json['reply_content']
    form_id = request.json['form_id']
    print(reply_content,form_id)    
    return 'success'

@app.route('/r_announcement_clicked', methods=["POST"])
def r_announcement_clicked():
    r_id = request.json['r_id']
    s_id = r_id[0].split("_")[1]
    print(s_id)
    announcement = get_announcement(int(s_id))
    print(announcement)
    return announcement


@app.route('/<name>', methods=["GET"])
def main(name):
    templname = name + '.htm'
    announcements = {}
    n = 50
    for i in range(n):
        announcements[i] = {"id":str(i),"title":"お知らせ"+str(i),"subject":"test","publish_date":"2022/02/07"}

    search_condition = "全て"
    sampletask1 = {"status": "未",
                   "assignment_url": "#",
                   "assignmentid": 1,
                   "time_left": {"msg": "2日", "judge": ""},
                   "deadline": "2022/3/2",
                   "subject": "サンプルサイト",
                   "clicked":0,
                   "quiz":True,
                   "taskname": "サンプル課題１"
                   }
    tasks = [sampletask1]
    last_update = "2020/3/2"
    data = {}
    for i in range(1, 6):
        data["mon"+str(i)] = {"searchURL": "#", "shortname": "サンプル月"+str(i)}
        data["tue"+str(i)] = {"searchURL": "#", "shortname": "サンプル火"+str(i)}
        data["wed"+str(i)] = {"searchURL": "#", "shortname": "サンプル水"+str(i)}
        data["thu"+str(i)] = {"searchURL": "#", "shortname": "サンプル木"+str(i)}
        data["fri"+str(i)] = {"searchURL": "#", "shortname": "サンプル金"+str(i)}
    data["mon4"]["tasks"] = [sampletask1]
    data["others"] = [{"shortname": "サンプルその他科目", "tasks": [sampletask1, sampletask1]}, {
        "shortname": "サンプルその他科目", "tasks": [sampletask1, sampletask1]}]
    sample_announcement = {"subject": "サンプルコース１", "checked": False, "title": "サンプルお知らせ１",
                           "publish_date": "2022/08/01 12:55", "html_file": "<h1>abc</h1>"}
    announcements = [sample_announcement]
    return render_template(templname, path=name, announcements=announcements,num=n,per_page=15,data=data,search_condition=search_condition,tasks=tasks)

@app.route('/')
def root():
    return redirect(url_for('main', name='tasklist'))



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


