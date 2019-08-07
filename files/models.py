#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/7/31 15:05
from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME, DATE
from sqlalchemy.ext.declarative import declarative_base
import datetime

base = declarative_base()


class Express(base):
    # 电话号码和入库时间为联合主键
    __tablename__ = 'express'
    express_number = Column(String(64), nullable=False)
    phone_number = Column(String(64), primary_key=True, nullable=False)  # 主键
    name = Column(String(64))
    date = Column(DATE(), default=datetime.datetime.now().date())
    time = Column(DATETIME(), primary_key=True, default=datetime.datetime.now)  # 主键
