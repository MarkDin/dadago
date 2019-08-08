#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/7/31 15:04
import datetime

import xlrd
import openpyxl
import os

from openpyxl import load_workbook

import my_path
from my_log import debug_logger, static_logger


def remove_white_space(data):
    '''
    取掉字符串中的空格
    :return:
    '''
    new_data = []
    for i in data:
        i = str(i)
        new_data.append(i.replace(' ', ''))
    return new_data


def get_phone_numbers(sheet):
    '''
    遍历电话号码 判断如果是小数就转换为整数
    :param sheet:
    :return: 整数类型的电话号码list
    :type: list
    '''
    phone_numbers = []
    # 遍历电话号码
    nrows = sheet.nrows
    # 电话号码在表格中的列的位置
    col = 3
    for i in range(1, nrows):
        # 数据类型
        ctype = sheet.cell(i, col).ctype
        # 值
        value = sheet.cell_value(i, col)
        # 如果是小数
        if ctype == 2 and value % 1 == 0.0:
            # 转换成整数
            value = int(value)
        phone_numbers.append(value)
    return phone_numbers


def change_to_dict(file_path):
    '''
    将给定的Excel表格中需要的数据提取出来转换成dict返回
    :param file_path:
    :return: dict格式的数据
    '''
    # 读取文件
    try:
        workbook = xlrd.open_workbook(filename=file_path)
    except FileNotFoundError:
        static_logger.error('上传的Excel文件未找到')
        debug_logger.debug('上传的Excel文件未找到')

    # 选择第一个sheet
    sheet = workbook.sheet_by_index(0)
    # 构建dict
    D = dict.fromkeys(['name', 'express_number', 'phone_number'])
    D['name'] = remove_white_space(sheet.col_values(1)[1:])
    # 快递号码
    D['express_number'] = remove_white_space(sheet.col_values(2)[1:])
    # 电话
    D['phone_number'] = get_phone_numbers(sheet)
    # 看数据有无异常
    if len(D['name']) == len(D['express_number']) == len(D['phone_number']):
        return D
    else:
        static_logger.error('导入Excel数据异常')
        debug_logger.debug('导入Excel数据异常')


def write(data, username):
    # 检测用户对应的文件名是否存在
    file_name = str(datetime.date.today()) + username + '.xlsx'
    file_path = os.path.join(my_path.EXCELS_PATH, 'download', file_name)
    # 存在对应文件则载入
    if os.path.exists(file_path):
        workbook = load_workbook(file_path)
    else:
        # 不存在从模板获取workbook
        workbook = select_template_as_file()
    # 文件不存在则创建
    if workbook:
        # grab the active worksheet
        sheet = workbook.active
        sheet.append(data)
        # Save the file
        workbook.save(os.path.join(my_path.EXCELS_PATH, 'download', file_name))
        # row = [u'收件人姓名', u'手机/电话', u'省', u'市', u'区', u'地址', u'物品名称', u'备注', u'数量', u'销售金额']
        return 0
    return 1


def select_file_as_template(file_path):
    '''
    载入Excel表格作为使用的模板
    :param file_path: 指定的excel表格的路径
    :return:
    '''
    # 加载源文件

    workbook = load_workbook(file_path)
    # 提取没有后缀名的文件路径
    file_path_without_ext = file_path.rsplit('.', 1)[0]
    debug_logger.debug(file_path_without_ext)
    # 保存为xltx格式的模板文件
    workbook.save(file_path_without_ext + '.xltx')
    static_logger.error('读取' + file_path + '失败')

    return 0


def select_template_as_file():
    '''
    返回从模板新创建的workbook对像
    :return: workbook
    :type: openpyxl.worksheet成功; 1失败
    '''
    workbook = 1
    try:
        workbook = load_workbook(os.path.join(my_path.ProjectPath, 'templates', 'template.xltx'))
        sheet = workbook.active
        workbook.template = False
    except:
        static_logger.error('使用Excel模板文件失败')
    return workbook


def test(x, y, *data):
    print(data)
    print(x, y)


if __name__ == '__main__':
    # write(os.path.join('..\Excels\download', str(datetime.date.today()) + 'username' + '.xlsx'))

    # use_template(os.path.join('..\Excels\download', str(datetime.date.today()) + 'username' + '.xltx'))

    res = remove_white_space(['df dfdf', '1 234 454', '  3543 353  '])
    print(res)
