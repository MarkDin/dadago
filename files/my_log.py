#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/7/31 17:51
import logging

debug_logger = logging.getLogger('debug_logger')
static_logger = logging.getLogger('static_logger')

#  配置logger
debug_handler = logging.StreamHandler()
debug_logger.addHandler(debug_handler)

static_handler = logging.FileHandler(filename=r'./logs/static_log')
static_logger.addHandler(static_handler)
#  配置formatter
debug_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s')
static_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s')
# 对应的Handler设置Formatter
debug_handler.setFormatter(debug_formatter)
static_handler.setFormatter(static_formatter)
