#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/7/31 15:04
import xlrd

workbook = xlrd.open_workbook('电子单号测试.xlsx')
sheet = workbook.sheet_by_index(0)


def change_to_dict():
    D = dict.fromkeys(['name', 'express_number', 'phone_number'])
    # print(D)
    # print(D.keys())
    # D['name'] = sheet.col_values()

    D['name'] = sheet.col_values(1)[1:]
    D['express_number'] = sheet.col_values(2)[1:]
    D['phone_number'] = sheet.col_values(3)[1:]
    return D
