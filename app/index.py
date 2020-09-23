from flask import Flask, request, render_template, url_for, redirect
import logging
from pprint import pprint


app = Flask(__name__)



@app.route('/<name>')
def main(name):
    templname = name + '.htm'
    return render_template(templname, path=name)

@app.route('/')
def root():
    return redirect(url_for('main', name='tasklist'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


