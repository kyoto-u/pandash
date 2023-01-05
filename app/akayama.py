from flask import Flask, request, render_template, url_for, redirect
import logging
from pprint import pprint


app = Flask(__name__)


@app.route('/manage_reply', methods=['POST'])
def manage_reply():
    reply_content = request.json['reply_content']
    form_id = request.json['form_id']
    print(reply_content,form_id)    
    return 'success'

@app.route('/<name>')
def main(name):
    templname = name + '.htm'
    dashboard = {"unique_data": {}, "total-data": {}, "labels": {}}


    dashboard["unique_data"] = {
        "d_thismon": 12,
        "d_1": 12,
        "d_2": 12,
        "d_3": 12,
        "d_4": 12,
        "d_5": 12,
        "d_6": 12,
        "d_7": 12,
    }
    dashboard["total_data"] = {
        "d_thismon": 12,
        "d_1": 12,
        "d_2": 12,
        "d_3": 12,
        "d_4": 12,
        "d_5": 12,
        "d_6": 12,
        "d_7": 12,
    }
    dashboard["labels"] = {
        "l_thismon": "thismon",
        "l_1": "l_1",
        "l_2": "l_2",
        "l_3": "l_3",
        "l_4": "l_4",
        "l_5": "l_5",
        "l_6": "l_6",
        "l_7": "l_7",
    }

    frms = [{},{},{}]
    frms[0] = {
        "forum_id":"forum1",
        "createdate":"2020/11/2",
        "title":"フォーラム１",
        "contents":"問い合わせ内容１",
        "reply_contents":"返信内容１",
        "replied":1
    }
    frms[1] = {
        "forum_id": "forum2",
        "createdate": "2020/3/2",
        "title": "フォーラム２",
        "contents": "問い合わせ内容２",
        "reply_contents": "返信内容２",
        "replied": 0
    }
    frms[2] = {
        "forum_id": "forum3",
        "createdate": "2020/5/2",
        "title": "フォーラム３",
        "contents": "問い合わせ内容３",
        "reply_contents": "返信内容３",
        "replied": 0
    }
    log=["samplelog1","samplelog2","samplelog3"]
    return render_template(templname, path=name,dashboard=dashboard,frms=frms,log=log)


@app.route('/')
def root():
    return redirect(url_for('main', name='tasklist'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
