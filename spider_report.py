# -*- coding: utf-8 -*-
# @Time    : 2019/2/26 14:08
# @Author  : yueconger
# @File    : spider_report.py
import json
import re

import os
import requests
from lxml import etree
from pymongo import MongoClient
from conf import FLAG, FILENAME, FILEPATH_DOWN, TYPE_SOFT
from conf import HEADERS
import conf
from process_tree import Tree


# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# # 禁用安全请求警告
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class AegisAssessment(object):
    def __init__(self):
        self.first_question = 'https://znys-m.aegis-info.com/intelligentpretrial/znys/first/question'
        self.next_url = 'https://znys-m.aegis-info.com/intelligentpretrial/znys/next/question'
        self.falvyijian = 'https://casefindinges6.aegis-info.com/api/prejudge/similarCase?qId={report_id}'
        self.xingdongjianyi = 'https://znys-m.aegis-info.com/intelligentpretrial/android/law_push/Law_Comment?qid={report_id}'
        self.susong = 'https://casefindinges6.aegis-info.com/api/prejudge/cost?qId={report_id}'
        self.headers = HEADERS
        self.form_data = {
            'cause_id': conf.CAUSE_ID,
            'subject_id': conf.SUBJECT_ID
        }

    def start_parse(self, ):
        url = self.first_question
        data = self.form_data
        response = self.post_body(url, HEADERS, data=data)
        return response

    def qustion_page(self, response):
        try:
            json_con = json.loads(response)
        except:
            print('未返回json数据')
        else:
            status_code = json_con['code']
            if status_code != 200:
                print('返回失败')
            else:
                # 正常返回
                data = json_con['data']
                if 'question' in data:
                    # 第一个问题
                    report_id = ''  # 第一次访问 无record_id
                    iw = data['choice_type']
                    id_question = data['id']
                    id_question_txt = data['question']
                    temp_choice_tags = data['temp_choice_tags']
                else:
                    # 非第一个问题
                    report_id = data['record_id']
                    iw = data['questions'][0]['choice_type']
                    id_question = data['questions'][0]['id']
                    id_question_txt = data['questions'][0]['question']
                    temp_choice_tags = data['questions'][0]['temp_choice_tags']

                if iw == '1':
                    message, report_id = self.choice_normal(iw, temp_choice_tags, id_question, id_question_txt, report_id)
                else:
                    message, report_id = self.choice_all(iw, temp_choice_tags, id_question, id_question_txt, report_id)
                print(message)
                return message, report_id

    def choice_normal(self, iw, temp_choice_tags, id_question, id_question_txt, report_id):
        """单选"""
        # iw = 1 或 iw 0
        item_list = []  # 选项列表
        item_list_txt = []  # 选项名称列表
        for temp_choice_tag in temp_choice_tags:
            colloquial = temp_choice_tag['colloquial']
            id = temp_choice_tag['id']
            item_list.append(id)
            item_list_txt.append(colloquial)

        message = {
            'iw': int(iw),
            'id_question': id_question,
            'id_question_txt': id_question_txt,
            'items': item_list,
            'items_txt': item_list_txt,
        }

        return message, report_id

    def choice_all(self, iw, temp_choice_tags, id_question, id_question_txt, report_id):
        item_list = []  # 选项列表
        item_list_txt = []  # 选项名称列表
        for temp_choice_tag in temp_choice_tags:
            colloquial = temp_choice_tag['colloquial']
            id = temp_choice_tag['id']
            item_list.append(id)
            item_list_txt.append(colloquial)

        message = {
            'iw': int(iw),
            'id_question': id_question,
            'id_question_txt': id_question_txt,
            'items': item_list,
            'items_txt': item_list_txt,
        }

        return message, report_id

    def process_message(self, iw, message, report_id):
        """
        向原网站提交数据
        """
        response = ''
        form_data_next = {
            'cause_id': conf.CAUSE_ID,
            'subject_id': conf.SUBJECT_ID,
            'record_id': report_id,
            'qid': message['id_question'],
            'tags': '["' + message['items'][0] + '"]'
        }
        print(form_data_next)
        if report_id == '':
            pass
        else:
            form_data_next['record_id'] = report_id
        if iw == 1:  # 单选
            response = self.post_body(self.next_url, headers=self.headers, data=form_data_next)
        if iw == 2:  # 多选
            response = self.post_body(self.next_url, headers=self.headers, data=form_data_next)
        return response, report_id

    def process_result(self, response):
        """处理生成报告"""
        json_con = json.loads(response)
        print(json_con)
        if 'record_id' in json_con['data']:
            report_id = json_con['data']['record_id']
            questions = json_con['data']['questions']
            if questions == []:
                # 生成评估报告
                response = self.get_body(self.falvyijian.format(report_id=report_id), headers=self.headers)
                try:
                    json_data = json.loads(response)
                    code = json_data['code']
                    if code == 200:
                        print('获取内容正常', report_id)
                        item = {}
                        law_info = json_data['data']['law']
                        case_info = json_data['data']['cases']
                        item['report_id'] = report_id
                        item['case_info'] = case_info
                        item['law_info'] = law_info
                        self.con2mongodb(item)

                        legal_advice = json_data['data']['action']

                        try:
                            res = self.get_body(self.xingdongjianyi.format(report_id=report_id), headers=self.headers)
                            json_d = json.loads(res)
                            code = json_d['code']
                            if code == 200:
                                move_advice = json_d['data']['action_comment']
                                message = {}
                                message['iw'] = 99
                                message['report'] = report_id
                                self.file_download(legal_advice, move_advice, report_id)
                                return message
                            else:
                                message = self.qustion_page(response)
                                return message
                        except:
                            print('行动建议获取失败', report_id)
                    else:
                        message, report_id = self.qustion_page(response)
                        return message, report_id

                except:
                    print('获取失败', report_id)
            else:
                message, report_id = self.qustion_page(response)
                return message, report_id
        else:
            message, report_id = self.qustion_page(response)
            return message, report_id

    def file_download(self, legal_advice, move_advice, report_id):
        file_path = FILEPATH_DOWN + TYPE_SOFT
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        content = '法律意见\n' + legal_advice + '\n\n行动建议\n' + move_advice
        file_name = ''.join([file_path, '/', report_id, '.html'])
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)
        print(report_id, '下载完毕!')

    def get_body(self, url, headers):
        response = requests.get(url, headers=headers)
        html = response.content.decode()
        return html

    def post_body(self, url, headers, data):
        """
        返回类json数据
        """
        response = requests.post(url, data=data, headers=headers)
        html = response.content.decode()
        return html

    def con2mongodb(self, answer_infos):
        client = MongoClient(
            host=conf.MONGDB_HOST,
            port=conf.PORT
        )
        db = client[conf.MONGODB_DBNAME]
        collection = db[conf.MONGODB_COL_AL]
        collection.insert(answer_infos)

    def main(self):
        pass


if __name__ == '__main__':
    flag = FLAG
    aegis_result = AegisAssessment()
    response = aegis_result.start_parse()
    if flag:
        tree = Tree(FILENAME)
        message, report_id = aegis_result.qustion_page(response)
    else:
        tree = Tree(FILENAME, follow_pre=True)
        path = tree.next_path()
        print('==========', path)
    while True:
        if flag:
            path = tree.construct(message)
        while not path:
            message, report_id = aegis_result.process_result(response)
            iw = message['iw']
            response, report_id = aegis_result.process_message(iw, message, report_id)
            message_pro, report_id = aegis_result.process_result(response)
            path = tree.construct(message_pro)
        tree = Tree(FILENAME, follow_pre=True)
        if not tree.curnode:
            break
        response = aegis_result.start_parse()
        response = json.loads(response)

        for i in path:
            print(i)
            iw = i['iw']
            if iw == '1':
                form_data = {
                    'cause_id': conf.CAUSE_ID,
                    'subject_id': conf.SUBJECT_ID,
                    'qid': i['id_question'],
                    'tags': str([i['items'][0]])
                }
                if 'record_id' in response['data']:
                    report_id = response['data']['record_id']
                    form_data['record_id'] = report_id
                response = aegis_result.post_body(aegis_result.next_url, aegis_result.headers, form_data)
            else:
                form_data = {
                    'cause_id': conf.CAUSE_ID,
                    'subject_id': conf.SUBJECT_ID,
                    'qid': i['id_question'],
                    'tags': str([i['items'][0]])
                }
                if 'record_id' in response['data']:
                    report_id = response['data']['record_id']
                    form_data['record_id'] = report_id
                response = aegis_result.post_body(aegis_result.next_url, aegis_result.headers, form_data)
            message, report_id = aegis_result.process_result(response)
            flag = True