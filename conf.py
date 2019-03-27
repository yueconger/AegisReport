# -*- coding: utf-8 -*-
# @Time    : 2019/2/27 14:45
# @Author  : yueconger
# @File    : conf.py
import requests

CAUSE_ID = '5c1859c2ba92937fab837faf'  # 民间借贷
SUBJECT_ID = '5c185a67ba92937fb0af7a42'  # 民间借贷纠纷

FLAG = True  # 注 首次抓取为True,有HTML生成后再次抓取改为False

FILEPATH_DOWN = r'E:\LocalServer\擎盾_评估\智能评估\html/'

TYPE_SOFT = '民间借贷/'
FILENAME = r'E:\LocalServer\擎盾_评估\智能评估\民间借贷.xml'

MONGDB_HOST = '127.0.0.1'
PORT = 27017
MONGODB_DBNAME = '擎盾_评估'  # 数据库名
MONGODB_COL_AL = '评估结果'  # 表名

HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://znys-m.aegis-info.com',
    'Referer': 'https://znys-m.aegis-info.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}


