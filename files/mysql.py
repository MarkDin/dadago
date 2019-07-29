#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/7/26 11:08
import datetime

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

engine = create_engine("mysql+pymysql://root:154310@116.62.4.61/dadago", isolation_level="READ UNCOMMITTED",
                       encoding='utf-8', echo=False)
base = declarative_base()

DBSession = scoped_session(sessionmaker())
DBSession.configure(bind=engine)


# class User(base):
#     __tablename__ = 'user'
#     # id = Column(Integer)
#     name = Column(String(32), primary_key=True, nullable=False)
#     phone_number = Column(String(64), primary_key=True, nullable=False)
#     # express_id = relationship('Express')


class Express(base):
    __tablename__ = 'express'
    express_number = Column(String(64), nullable=False)
    phone_number = Column(String(64), primary_key=True, nullable=False)  # 电话号码为主键
    name = Column(String(64))
    time = Column(DATETIME(), primary_key=True, default=datetime.datetime.now)


# res = session.query(User).filter(User.name == 'jack').first()
# print(res)

# e1 = Express(express_id='12354645', user_name='rose', user_phone='84856473689')
# DBSession.add(e1)
# DBSession.commit()


def insert_into_database(D):
    size = len(D['name'])
    print('size: ', size)
    DBSession.bulk_insert_mappings(
        Express,
        [
            dict(name=D['name'][i], express_number=D['express_number'][i], phone_number=D['phone_number'][i])
            for i in range(size)
        ],
        return_defaults='yes'
    )
    DBSession.commit()


def test_query_express_number_by_phone():
    try:

        while 1:
            user_input = input('请输入手机号码查询快递,或者"0"退出查询\n')
            # 输入为0时break跳出循环
            if user_input is '0':
                print('正在退出查询')
                break
            # 进行查询
            res = DBSession.query(Express).filter(Express.phone_number == user_input).order_by(Express.time).first()
            if res is not None:
                print('快递单号为: ' + res.express_number + '\n收件人为: ' + res.name + '\n')
            else:
                print('您要查询的手机号码不存在,请核对后查询\n')
    except:
        print('查询异常')


def query_express_number_by_phone(number):
    res = DBSession.query(Express).filter(Express.phone_number == number).order_by(Express.time).first()

    if res is not None:
        #print('快递单号为: ' + res.express_number + '\n收件人为: ' + res.name + '\n')
        # return '快递单号为: ' + res.express_number + '\n收件人为: ' + res.name + '\n'
        return 0
    else:
        print('您要查询的手机号码不存在,请核对后查询\n')
        return 1


def test(number):
    sql_str = 'select express_number, name from express WHERE express.phone_number = {} ORDER BY express.time LIMIT 1'.format(
        number)
    res = engine.execute(sql_str).fetchall()[0]
    if res is not None:
        print(res)
        return res
    else:
        print('您要查询的手机号码不存在,请核对后查询\n')
        return 1


def get_test_data():
    file = './error_phone_number'
    data = []
    flag = 0
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line is not '\n':
                # print(line.strip())
                data.append(line.strip())
            else:
                flag = 1
    if flag:
        print('测试出有空行')
    return data


def check_1():
    data = get_test_data()
    cnt = 0
    for i in range(len(data)):
        if test(data[i]):
            cnt += 1
    print('cnt:' + str(cnt))


def check_2():
    data = get_test_data()
    error = []
    cnt = 0
    for i in range(len(data)):
        if query_express_number_by_phone(data[i]) is not 0:
            cnt += 1
            error.append(data[i])

    print('cnt:' + str(cnt))
    print('2\n',error)
    with open('error_phone_number', 'a+') as f:
        for _ in error:
            f.write(_+'\n')
        f.write('----------\n')


if __name__ == '__main__':
    # base.metadata.drop_all(engine)
    # base.metadata.create_all(engine)  # 创建表
    # D = {}
    # D['name'] = ['a', 'b']
    # D['express_number'] = ['1234', '5678']
    # D['phone_number'] = ['120', '110']
    # D = change_to_dict()
    # insert_into_database(D)

    check_1()
