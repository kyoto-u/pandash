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

    return render_template(templname, path=name, announcements=announcements,num=n,per_page=15)

@app.route('/')
def root():
    return redirect(url_for('main', name='tasklist'))



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


