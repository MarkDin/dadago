#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/8/4 17:29
import my_path
from flask import Flask, render_template, url_for, jsonify, request, Response, redirect, flash, session, make_response, \
    send_from_directory
from files import mysql_manager, excel_manager
from files.my_log import static_logger, debug_logger
from functions import detect, get_exp_code, info_split, customer_info_parse
from models import ExcelUser
import datetime
import os
import time

app = Flask(__name__)
app.secret_key = '12345'


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


@app.errorhandler(404)
def page_404(e):
    return render_template('error.html', error_msg='404error'), 404


@app.errorhandler(500)
def page_404(e):
    return render_template('error.html', error_msg='500error'), 500


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
    phone_number = request.form.get('phone_number')
    print('1' + phone_number + '1', len(phone_number))
    if len(phone_number) == 0:
        return render_template('error.html', error_msg='手机号码为空')
        # return redirect_with_msg('/', '手机号码为空', 'express_query')
    else:
        # datas是列表
        datas = mysql_manager.query_express_by_phone_number(phone_number.replace(' ', ''))  # 元组(姓名,单号,日期)
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
            error_msg = '您要查询的手机号码暂无单号,请等待上传数据或者核对后查询'
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
            file_path = file_rename(file_dir, file_name, file_ext, 1)
            file.save(file_path)
    debug_logger.debug('file_path: ' + file_path)
    debug_logger.debug('上传完成')
    # 转换数据
    data = excel_manager.change_to_dict(file_path)
    if data is 1:
        # 删除文件
        os.remove(file_path)
        return render_template('upload.html', msg='数据转换dict失败')
    # 写入数据库
    flag = mysql_manager.insert_into_database(data)
    # 插入失败
    if flag:
        debug_logger.debug('数据插入失败')
        static_logger.error('数据插入失败')
        # 删除文件
        os.remove(file_path)
        return render_template('upload.html', msg='插入数据库失败')
    else:
        return render_template('upload.html', msg='数据入库成功')


@app.route('/resolve')
def resolve():
    return login_check()
    # return render_template('info_split.html')


@app.route('/info_resolve', methods={'get', 'post'})
def info_resolve():
    # 获取输入的文本
    text = request.form.get('text')
    # debug_logger.debug(text)
    # 初步将信息分割
    data = info_split(text, ',')
    # 结合搜的数据格式不对
    if data['error']:
        return jsonify({'info': [], 'msg': '数据格式有误,请核对后输入'})
    mp = {'name': '姓名', 'mobile': '手机号码', 'province': '省份', 'city': '城市', 'district': '区域地址', 'address': '详细地址',
          'item': '商品名称', 'note': '备注', 'number': '商品数量', 'price': '商品价格'}
    msg = ''
    # 检查是否有缺失数据
    for key, value in data.items():
        # 没有返回数据
        if len(str(value)) == 0 and key != 'note':
            # 加入提示信息
            msg += mp[key] + ','

    res = []
    # 获取用户名
    username = request.cookies.get('username')
    # 添加数据
    res.append(data['name'])
    res.append(data['mobile'])
    res.append(data['province'])
    res.append(data['city'])
    res.append(data['district'])
    res.append(data['address'])
    res.append(data['item'])
    res.append(username + data['note'])
    res.append(int(data['number']))
    res.append(int(data['price']))
    # 如果有信息缺失
    if msg != '':
        return jsonify({'info': res, 'msg': '缺失的信息有' + msg})
    # 返回值为1 则excel表格被其他程序占用 或者workbook获取失败
    if excel_manager.write(res, username):
        return jsonify({'info': [], 'msg': '写入Excel表格失败'})
    else:
        excel_manager.write(res, 'admin')
        return jsonify({'info': res, 'msg': '成功!'})


@app.route('/address_resolve', methods={'POST', 'GET'})
def address_resolve():
    mp = {'name': '姓名', 'mobile': '手机号码', 'province': '省份', 'city': '城市', 'district': '区域地址', 'address': '详细地址'}
    msg = ''

    if request.method == 'POST':
        # 获取用户输入
        text = request.form.get('text')
        data = customer_info_parse(text)
        msg = ''
        # 检查是否有缺失数据
        for key, value in data.items():
            # 没有返回数据
            if len(str(value)) == 0:
                # 加入提示信息
                msg += mp[key] + ' '
        res = []
        res.append(data['name'])
        res.append(data['mobile'])
        res.append(data['province'])
        res.append(data['city'])
        res.append(data['district'])
        res.append(data['address'])
        if len(msg) == 0:
            return jsonify({'info': res, 'msg': msg + 'ok'})
        else:
            return jsonify({'info': res, 'msg': '缺失: ' + msg})
    else:
        return render_template('address_split.html')


def redirect_with_msg(target, msg, category):
    if msg is not None:
        flash(msg, category=category)
    return redirect(target)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register_check', methods={'post'})
def register_check():
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    name = request.form.get('name').strip()
    confirm = request.form.get('confirm').strip()

    if len(username) == 0 or len(password) == 0 or len(name) == 0:
        return redirect_with_msg('/register', '用户名密码姓名不能为空', 'REGISTER')
    if mysql_manager.mysql_dbsession.query(ExcelUser).filter_by(username=username).first() is not None:
        return redirect_with_msg('/register', '用户已经存在', 'REGISTER')
    if password != confirm:
        return redirect_with_msg('/register', '两次密码不相同', 'REGISTER')
    user = ExcelUser(username=username, password=password, name=name)
    mysql_manager.mysql_dbsession.add(user)
    mysql_manager.mysql_dbsession.commit()
    return redirect_with_msg(url_for('login1'), '恭喜你, 注册成功', 'REGISTER')


@app.route('/login')
def login1():
    return render_template('login1.html')


@app.route('/logout')
def logout():
    # 清除cookie
    for mykey in request.cookies.keys():
        Response().delete_cookie(key=mykey)
    # 清除session
    session.clear()
    return redirect('/login')


@app.route('/login_check', methods={'post', 'get'})
def login_check():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        if len(username) == 0 or len(password) == 0:
            return redirect_with_msg('/login', '用户名密码不能为空', 'LOGIN_ERROR')
        user = mysql_manager.mysql_dbsession.query(ExcelUser).filter_by(username=username).first()
        if user is None:
            return redirect_with_msg('/login', '用户名不存在', 'LOGIN_ERROR')
        if password == user.password:
            session['user'] = username
            session['is_login'] = True
            session.permanent = True
            response = make_response(redirect('/resolve'))
            # 添加username到cookie
            response.set_cookie(key='username', value=username, max_age=60 * 60 * 24)
            return response
            # return redirect('/resolve')
        else:
            return redirect_with_msg('/login', '密码错误', 'LOGIN_ERROR')
    if session.get('is_login'):
        return render_template('info_split.html')
    else:
        return redirect('/login')


@app.route('/downloadpath')
def excel_download():
    date = str(datetime.date.today())
    filename = date + request.cookies.get('username') + '.xlsx'
    dir_path = os.path.join(my_path.EXCELS_PATH, 'download')
    if not os.path.exists(os.path.join(dir_path, filename)):
        # return Response('未成功录入核对信息前,文件未创建,请先输入核对信息')
        return render_template('error.html', error_msg='未成功录入核对信息前,文件不会被创建,请先输入核对信息')
    return send_from_directory(dir_path, filename, as_attachment=True, cache_timeout=0)
