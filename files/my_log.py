#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/7/31 17:51
import logging
import my_path
import os

debug_logger = logging.getLogger('debug_logger')
# 只有在loger设置的日志级别有效
debug_logger.setLevel(logging.DEBUG)
static_logger = logging.getLogger('static_logger')
# 只有在loger设置的日志级别有效
static_logger.setLevel(logging.ERROR)
#  配置logger
debug_handler = logging.StreamHandler()
# 将日志级别设置为10
# debug_handler.setLevel(logging.DEBUG)
debug_logger.addHandler(debug_handler)
static_handler = logging.FileHandler(filename=os.path.join(my_path.ProjectPath, 'logs\\static_log'))
static_logger.addHandler(static_handler)
#  配置formatter
debug_formatter = logging.Formatter(
    '%(asctime)s %(name)s %(levelname)s 模块名:%(module)s 函数名:%(funcName)s msg:%(message)s')
static_formatter = logging.Formatter(
    '%(asctime)s %(name)s %(levelname)s 模块名:%(module)s 函数名:%(funcName)s msg:%(message)s')
# 对应的Handler设置Formatter
debug_handler.setFormatter(debug_formatter)
static_handler.setFormatter(static_formatter)
