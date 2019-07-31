#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/7/30 20:53
import re
import requests


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
