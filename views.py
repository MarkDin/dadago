#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/8/4 17:29
from flask import Flask, render_template, url_for, jsonify, request
from files import mysql_manager, excel_manager
from files.my_log import static_logger, debug_logger
from functions import detect, get_exp_code
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
    return render_template('new_index.html')


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
    # datas是列表
    datas = mysql_manager.query_express_by_phone_number(phone_number)  # 元组(姓名,单号,日期)
    # 单号存在
    if datas is not 1:
        exp_codes = []
        exp_numbers = []
        exp_dates = []
        for data in datas:
            # 查询快递公司编码
            exp_code = get_exp_code(detect(data[1]))
            exp_codes.append(exp_code)
            exp_numbers.append(data[1])
            exp_dates.append(str(data[2]))
            # debug_logger.debug(data[2])
        contents = []
        # 构建content字典 添加到contentslist中
        for exp_number, exp_code, exp_date in zip(exp_numbers, exp_codes, exp_dates):
            content = {
                # 姓名
                'name': datas[0][0],
                # 快递公司编号 expCode为ERROR时,快递公司编码检测出错
                'exp_code': exp_code,
                # 快递单号
                'exp_number': exp_number,
                # 快递日期
                'exp_date': exp_date,
            }
            contents.append(content)
        debug_logger.debug('express_query函数返回contents列表')
        return render_template('express.html', contents=contents)
    else:  # 单号不存在
        print('您查询的手机号码的对应快递单号不存在,请核对后查询')
        error_msg = '您查询的手机号码的对应快递单号不存在,请核对后查询'
        return render_template('error.html', error_msg=error_msg)


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
        file_dir = os.path.join(my_path.ProjectPath, 'Excels', 'upload')
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
