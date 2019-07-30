from flask import Flask
from files import mysql
from flask import url_for, render_template, request, flash, redirect, get_flashed_messages, send_from_directory

app = Flask(__name__)


@app.route('/express_query/<phone_number>', methods={'get', 'post'})
def hello_world(phone_number):
    if type(phone_number) is not str:
        phone_number = str(phone_number)
    info = mysql.test(phone_number)
    if info is not 1:
        return '快递单号: '+info[0] + '\n姓名: '+ info[1]
    else:
        return '你要查询的手机号码关联的快递号不存在,请核对后查询'


@app.route('/')
def index():
    return 'hello, dadago'

if __name__ == '__main__':
    app.run(threaded=True)
