#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/7/31 15:05
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Express, base
from my_log import debug_logger, static_logger
import re

'''
因为一个项目总会有很多不同的应用需要操作同一个数据库或者多个不同的数据库(甚至是不同类型的数据库),
需要生成不同的可操作性的数据库对像来区分,传入的engine参数就代表了不同的数据库连接
'''
engine = create_engine("mysql+pymysql://root:154310@116.62.4.61/dadago", isolation_level="READ UNCOMMITTED",
                       encoding='utf-8', echo=False)
mysql_dbsession = scoped_session(sessionmaker())
# 将engine连接的数据库绑定到mysql_dbsession
mysql_dbsession.configure(bind=engine)


def create_table(engine):
    '''
    先判断表是否存在, 不存在则创建
    :param engine:
    :return: 1:存在; 0:不存在,创建成功
    '''
    sql = "show tables;"
    tables = [engine.execute(sql).fetchall()]
    table_list = re.findall('(\'.*?\')', str(tables))
    table_list = [re.sub("'", '', each) for each in table_list]
    # 如果表已经存在
    if 'express' in table_list:
        return 1
    # 不存在
    else:
        # 创建表
        base.metadata.create_all(engine)
        return 0


def insert_into_database(D):
    '''

    :param D: Excel表格提取字段的字典格式
    :return:
    '''
    size = len(D['name'])
    # 批量插入到数据库
    mysql_dbsession.bulk_insert_mappings(
        Express,  # 表名
        [
            # 构造字典list
            dict(name=D['name'][i], express_number=D['express_number'][i], phone_number=D['phone_number'][i])
            for i in range(size)
        ],
    )
    # 提交
    try:
        mysql_dbsession.commit()
        return 0
    except:
        return 1


def query_express_by_phone_number(number):
    '''

    :param number: 要查询的电话号码
    :return: 单号不存在:1; 存在:单号加姓名的list list里面元素为元组(姓名,单号,日期)
    '''
    # 使用sqlalchemy的query查询有问题 直接执行SQL语句
    sql_str = 'select express.`name`, express.express_number, express.date FROM express WHERE express.phone_number = {} AND ABS(DATEDIFF(date,CURDATE())) < 15 ORDER BY express.date desc'.format(
        number)
    res = []
    try:
        # 注意返回的res是list类型
        res = engine.execute(sql_str).fetchall()
    except:
        # 表不存在,创建表
        if create_table(engine):
            res = []

    # 结果不为空

    if len(res) is not 0:
        return res
    else:
        debug_logger.info('您要查询的手机号码不存在,请核对后查询\n')
        return 1
