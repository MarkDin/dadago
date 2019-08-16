#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/7/31 15:05
from sqlalchemy import Column, Integer, String, ForeignKey, DATE
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
base = declarative_base()
'''
因为一个项目总会有很多不同的应用需要操作同一个数据库或者多个不同的数据库(甚至是不同类型的数据库),
需要生成不同的可操作性的数据库对像来区分,传入的engine参数就代表了不同的数据库连接
'''
engine = create_engine("mysql+pymysql://root:154310@116.62.4.61/dadago", isolation_level="READ UNCOMMITTED",
                       encoding='utf-8', echo=False)
mysql_dbsession = scoped_session(sessionmaker())
# 将engine连接的数据库绑定到mysql_dbsession
mysql_dbsession.configure(bind=engine)

class Express(base):
    # 电话号码和入库时间为联合主键
    __tablename__ = 'express'
    # query = mysql_dbsession.query_property()
    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    express_number = Column(String(64), nullable=False)
    phone_number = Column(String(64), primary_key=True, nullable=False)  # 主键
    name = Column(String(64))
    date = Column(DATE(), default=datetime.datetime.now().date())
    # time = Column(DATETIME(), primary_key=True, default=datetime.datetime.now)  # 主键


class ExcelUser(base):
    __tablename__ = 'excelUser'
    # query = mysql_dbsession.query_property()
    id = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    username = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    name = Column(String(32), nullable=False)

    def __init__(self, username, password, name):
        self.username = username
        self.password = password
        self.name = name
