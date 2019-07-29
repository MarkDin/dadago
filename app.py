from flask import Flask
from files import mysql
from flask import url_for, render_template, request, flash, redirect, get_flashed_messages, send_from_directory

app = Flask(__name__)


@app.route('/express_query/<phone_number>', methods={'get', 'post'})
def hello_world(phone_number):
    if type(phone_number) is not str:
        phone_number = str(phone_number)
    info = mysql.test(phone_number)
    return '快递单号: '+info[0] + '\n姓名: '+ info[1]



if __name__ == '__main__':
    app.run(threaded=True)
