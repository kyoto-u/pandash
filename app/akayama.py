from flask import Flask, request, render_template, url_for, redirect
import logging
from pprint import pprint


app = Flask(__name__)



@app.route('/<name>')
def main(name):
    templname = name + '.htm'
    darktheme = True
    search_condition = "全て"
    sampletask1 = {"status": "未", 
                    "assignment_url": "#", 
                    "assignmentid": 1,
                    "time_left": {"msg": "2日", "judge": "two_day"}, 
                    "deadline": "2022/3/2",
                    "subject":"サンプルサイト",
                    "taskname":"サンプル課題１"
                    }
    tasks = [sampletask1]
    last_update = "2020/3/2"
    data = {}
    for i in range(1,6):
        data["mon"+str(i)] = {"searchURL": "#", "shortname": "サンプル月"+str(i)}
        data["tue"+str(i)] = {"searchURL": "#", "shortname": "サンプル火"+str(i)}
        data["wed"+str(i)] = {"searchURL": "#", "shortname": "サンプル水"+str(i)}
        data["thu"+str(i)] = {"searchURL": "#", "shortname": "サンプル木"+str(i)}
        data["fri"+str(i)] = {"searchURL": "#", "shortname": "サンプル金"+str(i)}
    data["mon1"]["tasks"] = [sampletask1]
    data["others"] = [{"shortname": "サンプルその他科目", "tasks": [sampletask1, sampletask1]}, {
        "shortname": "サンプルその他科目", "tasks": [sampletask1, sampletask1]}]
    with open("./test_html.txt",encoding="utf-8") as f:
        html = f.read()
    return render_template(templname,html=html, numofcourses=2,path=name, data=data,darktheme = darktheme,search_condition=search_condition,tasks = tasks,last_update = last_update,num=20,per_page=10,page=1)

@app.route('/')
def root():
    return redirect(url_for('main', name='tasklist'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
