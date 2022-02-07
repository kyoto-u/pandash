from flask import Flask, request, render_template, url_for, redirect
import logging
from pprint import pprint


app = Flask(__name__)

@app.route('/<name>')
def main(name):
    templname = name + '.htm'
    announcements = {}
    n = 50
    for i in range(n):
        announcements[i] = {"title":"お知らせ"+str(i),"subject":"test","publish_date":"2022/02/07","html_file":"<h1>hogehoge</h1>"}

    announce={"title":"OAサンプル","subject":"サイト１","publish_date":"2021/12/27","html_file":"<h1>hogehoge</h1>"}

    return render_template(templname, path=name, announce=announce, announcements=announcements,num=n,per_page=15)

@app.route('/')
def root():
    return redirect(url_for('main', name='tasklist'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


