from flask import Flask, request
from flask import render_template, url_for, jsonify
from files import mysql_manager, excel_manager
from files.my_log import static_logger, debug_logger
from func import detect, get_exp_code
import datetime
import os
import time
import my_path

app = Flask(__name__)


def file_rename(file_path, file_name, file_ext, cnt=1):
    '''
    注意返回的不是单个文件名 而是路径
    :param file_path: 文件所在文件夹路径
    :param file_name: 文件名(不包含后缀)
    :param file_ext: 文件后缀
    :param cnt: 构造不同的文件名的数字
    :return: 完整的文件的路径
    '''
    new_file_path = os.path.join(file_path, file_name + '_' + str(cnt) + '.' + file_ext)
    # 若当前文件名不存在
    if not os.path.exists(new_file_path):
        return new_file_path
    # 若当前文件名存在
    else:
        # 文件后缀数字加一
        cnt += 1
        # 继续重命名
        return file_rename(file_path, file_name, file_ext, cnt)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/query_express/<phone_number>', methods={'get', 'post'})
def express_api(phone_number):
    if type(phone_number) is not str:
        phone_number = str(phone_number)
    info = mysql_manager.query_express_by_phone_number(phone_number)
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


@app.route('/upload')
def up_load():
    return render_template('upload.html')


@app.route('/excel_upload', methods={'get', 'post'})
def excel_upload():
    try:
        file = request.files['file']
    except:
        return '空文件'
    # 获取文件的后缀
    file_ext = file.filename.split('.', 1)[1].strip().lower()
    #  检查文件名是否合法
    if file_ext in ['xls', 'xlsx']:
        #  保存的文件名为当天日期
        file_name = str(datetime.date.today())  # 不含文件后缀名
        # file_dir = '.\\Excels'
        # 文件名不存在
        file_dir = os.path.join(my_path.ProjectPath, 'Excels')
        if not os.path.exists(os.path.join(file_dir, file_name + '.' + file_ext)):
            # 保存文件到Excel目录

            # 文件完整路径
            file_path = os.path.join(file_dir, file_name + '.' + file_ext)
            file.save(file_path)
        # 调用file_rename函数命名
        else:
            debug_logger.debug('文件名重复了')
            file_path = file_rename(file_dir, file_name, file_ext, 1)
            file.save(file_path)
    debug_logger.debug('file_path: ' + file_path)
    debug_logger.debug('上传完成')
    #  转换数据
    try:
        time.sleep(2)
        Data = excel_manager.change_to_dict(file_path)
    except:
        static_logger.error('使用change_to_dict转换' + file_path + '失败')
        debug_logger.debug('使用change_to_dict转换' + file_path + '失败')
        return '数据转换dict失败'
    # 写入数据库
    flag = mysql_manager.insert_into_database(Data)
    # 插入失败
    if flag:
        debug_logger.debug('数据插入失败')
        static_logger.error('数据插入失败')
        return '插入数据库失败'
    else:
        return 'everything is ok'


if __name__ == '__main__':
    app.run(threaded=True, debug=True)
