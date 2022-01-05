from flask import Flask, request, render_template, url_for, redirect
import logging
from pprint import pprint


app = Flask(__name__)


def button_clicked(button_name):
    if button_name == "button1":
        return "button1 clicked"
    elif button_name == "button2":
        return "button2 clicked"
    else:
        return "No button clicked"

app.jinja_env.globals['button_clicked'] = button_clicked


@app.route('/<name>')
def main(name):
    templname = name + '.htm'
    announce={"title":"OAサンプル","subject":"サイト１","publish_date":"2021/12/27","html_file":"<h1>hogehoge</h1>"}

    return render_template(templname, path=name, announce=announce, button_clicked = button_clicked)

@app.route('/')
def root():
    return redirect(url_for('main', name='tasklist'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


