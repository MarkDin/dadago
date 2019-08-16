#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/7/30 20:53
import string

import re
import urllib
import requests
from files.my_log import debug_logger, static_logger
import time, hashlib, json


def detect(express_number):
    '''

    :param express_number:
    :return: 快递公司代码
    '''

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/75.0.3770.142 Safari/537.36 ',
        'Host': 'www.kuaidi100.com',
        'Referer': 'https: // www.kuaidi100.com /'
    }
    api = 'https://www.kuaidi100.com/autonumber/autoComNum?resultv2=1&text={}'.format(express_number)
    response = requests.get(url=api, headers=headers).text
    res = re.search(r'\[{"comCode":"(.*?)"', response)
    if res:
        print(res.group(1))
        return res.group(1)
    else:
        print('detect查询异常')
        return 'error'


def get_exp_code(dect_code):
    '''
    转换公司编码
    :param dect_code: 快递100检测出的快递公司编码
    :return:快递鸟对应的公司编码
    '''
    code = {
        # 快递100检测出错
        'error': 'ERROR',
        # 顺风
        'shunfeng': 'SF',
        # 中通
        'zhongtong': 'ZTO',
        # 申通
        'shentong': 'STO',
        # 圆通
        'yuantong': 'YTO',
        # 韵达
        'yunda': 'YD',
        # 邮政平邮
        'youzhengguonei': 'YZPY',
        # EMS
        'ems': 'EMS',
        # 德邦物流
        'debangwuliu': 'DBL'
    }
    res = 'YTO'  # 默认设置为圆通
    res = code[dect_code]
    print('转换的快递鸟公司编码为: ' + res)
    return res


def parse_address(text):
    '''
    将text解析成 '收件人姓名	手机/电话	省	市	区	地址	 物品名称 备注 数量	销售金额'的格式
    :param text:需要解析的文本
    :return: 字典格式的数据
    '''
    # 构建返回的数据字典
    data = {
        'name': '',
        'phone_number': '',
        'province': '',
        'city': '',
        'district': '',
        'address': '',
        'item': '',
        'note': '',
        'count': '',
        'price': '',
    }
    # 检测文本是否为空
    if text is not None:
        pass
    else:
        debug_logger.debug('传入的文本为空')
        return 1


def md5(ts, method):
    '''
    :param ts: 时间戳的string形式
    :param method:调用的api方法名称
    :return:返回md5加密后的 (app_id + api_key + method)
    '''
    app_id = '104123'
    api_key = 'b140b2b5081cb4482f30677fa1ddc17afa048c7c'
    code = app_id + method + ts + api_key
    m = hashlib.md5(code.encode())
    return m.hexdigest()


def address_correct_api(address):
    '''
    :param 地址信息文本
    :type string
    :return: 处理后的地址信息字典 包含:province city district address
    :type: dict
    '''
    url = 'https://kop.kuaidihelp.com/api'
    ts = str(int(time.time()))
    # 构造参数
    data = {
        "multimode": False,
        "address": address,
        "cleanTown": False
    }
    # 转换成json格式
    data = json.dumps(data)
    payload_list = {}
    payload_list['app_id'] = '''104123'''
    payload_list['method'] = '''cloud.address.cleanse'''
    payload_list['ts'] = ts
    payload_list['sign'] = md5(ts, 'cloud.address.cleanse')
    payload_list['data'] = data
    # 发起请求
    response = requests.post(url, data=payload_list)
    # 转换为字典格式
    dict_data = json.loads(response.text)
    # 提取返回的code值
    code = dict_data['code']
    # 返回值为1 出错
    if code is not 0:
        static_logger.error('address_correct_api返回code值为1')
        debug_logger.debug('address_correct_api返回code值为1')
        return 1
    else:
        # 返回提取的四个值: 省 市 区 地址
        address = {}
        address['province'] = dict_data['data'][0]['province']
        address['city'] = dict_data['data'][0]['city']
        address['district'] = dict_data['data'][0]['district']
        address['address'] = dict_data['data'][0]['address']
        # print(address)
        return address


def info_resolve_api(info):
    '''
    解析文本信息中的 姓名 电话 省 市 区 等信息
    :param info:
    :return:
    '''
    url = 'https://kop.kuaidihelp.com/api'
    ts = str(int(time.time()))
    # 构造参数
    data = {
        "text": info,
        "multimode": False
    }
    # 转换成json格式
    data = json.dumps(data)
    payload_list = {}
    payload_list['app_id'] = '''104123'''
    payload_list['method'] = '''cloud.address.resolve'''
    payload_list['ts'] = ts
    payload_list['sign'] = md5(ts, 'cloud.address.resolve')
    payload_list['data'] = data
    # 发起请求
    response = requests.post(url, data=payload_list).text
    dict_data = json.loads(response)
    # 提取返回的code值
    code = dict_data['code']
    # 返回值为1 出错
    if code is not 0:
        static_logger.error('info_resolve_api返回code值为1')
        debug_logger.error('info_resolve_api返回code值为1')
        return 1
    else:
        # debug_logger.debug(dict_data['data'])
        data = {}
        data['name'] = dict_data['data'][0]['name']
        data['mobile'] = dict_data['data'][0]['mobile']
        data['province'] = dict_data['data'][0]['province_name']
        data['city'] = dict_data['data'][0]['city_name']
        data['district'] = dict_data['data'][0]['county_name']
        data['address'] = dict_data['data'][0]['detail']
        return data


def customer_info_parse(info):  # 信息必须在一行
    '''
    先调用info_resolve_api将电话 姓名解析出来,然后在源信息中去掉姓名电话 再调用address_correct_api
    :param info:
    :return: data{'name', 'city'........}
    '''
    data = info_resolve_api(info)
    # 返回的所需信息完整
    if data['province'] == data['city'] == data['district'] == '':
        name = data['name']
        mobile = data['mobile']
        # 进行替换
        info = info.replace('电话', '')
        info = info.replace('收件人', '')
        info = info.replace('收', '')
        info = info.replace(name, '')
        info = info.replace(mobile, '')
        # info = info.translate(str.maketrans('', '', '电子：'))
        data = address_correct_api(info)
        data['name'] = name
        data['mobile'] = mobile
        # debug_logger.debug('1 ' + str(data))
        return data
    else:
        # debug_logger.debug('2: ' + str(data))
        return data


def info_split(text, sign):
    data = {'error': 0}
    # 将中文逗号用英文逗号替换
    text = text.replace('，', ',')
    try:
        info = text.split(sign, 4)
        # 商品名称和尺码
        data['item'] = info[0].replace(' ', '')
        # 零售价格
        data['price'] = re.search('\d+', info[1]).group().replace(' ', '')
        # 商品数量
        data['number'] = re.search('\d+', info[2]).group().replace(' ', '')
        # 备注信息 eg:分开发 补差价 退换货
        data['note'] = info[3].replace(' ', '')
        # 顾客发的信息
        data['customer_info'] = info[4]

        # 检查商品价格和商品数量是否需要交换位置
        if len(str(data['price'])) < len(str(data['number'])):
            data['price'], data['number'] = data['number'], data['price']
        # 如果是退换货 则商品数量设为0
        if data['note'] == '退换货':
            data['number'] = 0
    except:
        data['error'] = 1
        return data
        # print(data)
    D = customer_info_parse(data['customer_info'])
    for key, value in D.items():
        data[key] = value
    return data




if __name__ == '__main__':
    # data = customer_info_parse(info)
    # print(data['province'])
    # print(data['city'])
    # print(data['district'])
    # print(data['address'])
    # 前山工业园福溪工业区福田路10号博杰电子电话：15886648166收件人：周宏杰
    info_split('B类特价三叶草金标贝壳头3号36.5!零售199! 2! 退换货! 长沙市雨花区左家塘街道桂花二村附20栋2单元404丁姚   15574996073', '!')
