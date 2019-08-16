#!/usr/bin/python 
# -*- coding: utf-8 -*-
# @Author: 丁珂
# @Time: 2019/8/1 11:36
import os
import sys

ProjectPath = os.path.abspath(os.path.dirname(__file__))
EXCELS_PATH = os.path.join(ProjectPath, 'Excels')

sys.path.append(ProjectPath)
sys.path.append(os.path.join(ProjectPath, 'files'))
# print(curPath)
# print(rootPath)
# print(PathProject)
