#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/7/31 15:04
import xlrd
from my_log import debug_logger, static_logger


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
    # print(D)
    # print(D.keys())
    # D['name'] = sheet.col_values()
    # 联系人
    D['name'] = sheet.col_values(1)[1:]
    # 快递号码
    D['express_number'] = sheet.col_values(2)[1:]
    # 电话
    D['phone_number'] = sheet.col_values(3)[1:]
    if len(D['name']) == len(D['express_number']) == len(D['phone_number']):
        return D
    else:
        static_logger.error('导入Excel数据异常')
        debug_logger.debug('导入Excel数据异常')
