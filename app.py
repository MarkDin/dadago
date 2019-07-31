from flask import Flask, request
from flask import render_template, url_for, jsonify
from files import mysql
from files import mysql_manager
from func import detect, get_exp_code

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query_express/<phone_number>', methods={'get', 'post'})
def hello_world(phone_number):
    if type(phone_number) is not str:
        phone_number = str(phone_number)
    info = mysql_manager.query_express_number_by_phone(phone_number)
    if info is not 1:
        return '快递单号: ' + info[0] + '\n姓名: ' + info[1]
    else:
        return '你要查询的手机号码关联的快递号不存在,请核对后查询'


@app.route('/express_query', methods={'get', 'post'})
def express_query():
    # 获取ajax传来的快递单号
    phone_number = request.form.get('phone_number').strip()
    expNo = mysql_manager.query_express_by_phone_number(phone_number)  # 确保这里拿到的phone_number不为空
    # 单号存在
    if expNo is not 1:
        expCode = detect(expNo)
        expCode = get_exp_code(expCode)
        content = {
            # 服务类型
            'serviceType': 'B',
            # 快递公司编号 expCode为ERROR时,快递公司编码检测出错
            'expCode': expCode,
            # 快递单号
            'expNo': expNo[0][0],
            # HTML中显示快递信息的组件的id
            'container': "showExpress",
            # 检测数据库中是否有单号
            'flag': '0'
        }
        print('expNo_type: ', type(expNo))
        print('返回json')
        return jsonify(content)
    else:  # 单号不存在
        print('号码对应的单号不存在,请核对后重新输入')
        return jsonify({'flag': '1'})


if __name__ == '__main__':
    app.run(threaded=True, debug=True)
