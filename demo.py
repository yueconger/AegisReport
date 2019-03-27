# -*- coding: utf-8 -*-
# @Time    : 2019/3/27 15:31
# @Author  : yueconger
# @File    : demo.py
import json
import re

import os
import requests
from lxml import etree
from conf import FLAG, FILENAME, FILEPATH_DOWN, TYPE_SOFT
import conf
from process_tree import Tree


# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# # 禁用安全请求警告
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ReportClawer(object):
    def __init__(self):
        self.start_url = 'https://wxfxpg.susong51.com/ssfxpg-wx/ssfxpg/anon/createSession'
        self.start_url_html = 'https://wxfxpg.susong51.com/ssfxpg-wx/ssfxpg/anon/startSsfxpg?fy=3750&sjmlbh=4943D4AA142111C7E2BC6E9A4357478D'
        self.do_next_url = 'https://wxfxpg.susong51.com/ssfxpg-wx/ssfxpg/anon/doNext'
        self.finish_url = 'https://wxfxpg.susong51.com/ssfxpg-wx/ssfxpg/anon/doFinish'
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'wxfxpg.susong51.com',
            'Origin': 'https://wxfxpg.susong51.com',
            'Referer': 'https://wxfxpg.susong51.com/ssfxpg-wx/ssfxpg/anon/startSsfxpg?fy=3750&sjmlbh=4943D4AA142111C7E2BC6E9A4357478D&fyId=3835',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.report_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': 'JSESSIONID=ssfxpgmanage1wrj5h4ygutw6a3vsu9rd44ou.ssfxpgmanage',
            'Host': 'wxfxpg.susong51.com',
            'Referer': 'https://wxfxpg.susong51.com/ssfxpg-wx/ssfxpg/anon/startSsfxpg?fy=3750&sjmlbh=4943D4AA142111C7E2BC6E9A4357478D',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        }
        self.finish_headers = {
            'Accept': 'application/json, text/javascript',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Origin': 'https://wxfxpg.susong51.com',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'JSESSIONID=ssfxpgmanage1wrj5h4ygutw6a3vsu9rd44ou.ssfxpgmanage',
            'Host': 'wxfxpg.susong51.com',
            'Referer': 'https://wxfxpg.susong51.com/ssfxpg-wx/ssfxpg/anon/startSsfxpg?fy=3750&sjmlbh=4943D4AA142111C7E2BC6E9A4357478D',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
        }
        self.referer = 'https://wxfxpg.susong51.com/ssfxpg-wx/ssfxpg/anon/startSsfxpg?fy=3750&sjmlbh={}'
        self.form_data_next = {'sessionbh': '', 'wtbh': '', 'czms': ''}

    def start_parse(self):
        print('--------------------------')
        headers = self.headers
        headers['Cookie'] = conf.get_session()
        # 抓取流程已存入本地文件 读取文件内参数，构造post请求
        local_home_path = r'测试首页.json'
        with open(local_home_path, 'r', encoding='utf-8') as jf:
            home_dict = json.load(jf)
        type_list = home_dict['dataInfo']['childMlList']
        fySbBh = home_dict['fySbBh']
        # for i in range(len(type_list)):
        #     type_info = type_list[i]
        #     sjMlBh = type_info['cBh']
        type_info = type_list[1]  # 租赁合同纠纷
        sjMlBh = type_info['cBh']
        type_name = type_info['cMc']
        # print('当前模块为: %s' % type_name)
        data = {'sjMlBh': sjMlBh, 'fySbBh': fySbBh}
        res = self.post_body(self.start_url, headers, data)  # 问答流程开始
        response = json.loads(res)
        return headers, response

    def question_page(self, response, iw):
        # 对返回值处理
        response = str(response).replace("'", '"')
        res = json.loads(response)
        try:
            messages = res['messages']
        except Exception as e:
            print('json数据出错', e)
        else:
            messages = str(messages).replace("'", '"')
            message_info = json.loads(messages)
            sessionbh = message_info['sessionInfo']['cBh']
            wtbh = message_info['currentWt']['twxsData']['twxsInfo']['cWtBh']
            cWttg = message_info['currentWt']['twxsData']['twxsInfo']['cWttg']
            id_question = wtbh  # 问题字段
            id_question_txt = cWttg  # 问题名称

            option_list = message_info['currentWt']['twxsData']['xxList']
            if iw == 1:
                message = self.choice_normal(iw, option_list, id_question, id_question_txt, sessionbh)
            elif iw == 2:
                message = self.choice_all(iw, option_list, id_question, id_question_txt, sessionbh)
            else:
                message = {}
            return message

    def choice_normal(self, iw, option_list, id_question, id_question_txt, sessionbh):
        """单选"""
        # iw = 1 或 iw 0
        item_list = []  # 选项列表
        item_list_txt = []  # 选项名称列表
        for option_info in option_list:
            choice_para = option_info['cBh']
            choice_name = option_info['cMc']
            item_list.append(choice_para)
            item_list_txt.append(choice_name)

        message = {
            'iw': iw,
            'id_question': id_question,
            'id_question_txt': id_question_txt,
            'items': item_list,
            'items_txt': item_list_txt,
        }
        return message

    def choice_all(self, iw, option_list, id_question, id_question_txt, sessionbh):
        """多选"""
        # iw = 10
        item_list = []  # 选项列表
        item_list_txt = []  # 选项名称列表
        for option_info in option_list:
            choice_para = option_info['cBh']
            choice_name = option_info['cMc']
            item_list.append(choice_para)
            item_list_txt.append(choice_name)

        message = {
            'iw': iw,
            'id_question': id_question,
            'id_question_txt': id_question_txt,
            'item': item_list,
            'items_txt': item_list_txt,
        }
        return message, sessionbh

    def process_message(self, iw, message, sessionbh, headers):
        """
        向原网站提交数据
        """
        response = ''
        if iw == 1:  # 单选
            form_data_next = {
                'sessionbh': sessionbh,
                'wtbh': message['id_question'],
                'czms': message['items'][0]
            }
            response = self.post_body(self.do_next_url, headers=headers, data=form_data_next)
        if iw == 2:  # 多选
            form_data_next = {
                'sessionbh': sessionbh,
                'wtbh': message['id_question'],
                'czms': message['item'][0]
            }
            response = self.post_body(self.do_next_url, headers=headers, data=form_data_next)
        return response

    def process_results(self, response, headers):
        """
        处理生成最终报告
        :param response:
        :return:
        """
        response = str(response).replace("'", '"')
        response = json.loads(response)
        ending_flag = response['messages']['finish']
        sessionbh = response['messages']['sessionInfo']['cBh']
        if ending_flag != 'false':
            # 生成评估报告
            finish_headers = self.finish_headers
            finish_headers['Cookie'] = headers['Cookie']
            finish_form_data = {"sessionbh": sessionbh}
            finish_res = self.post_body(url=self.finish_url, data=finish_form_data, headers=finish_headers)
            report_url = 'https://wxfxpg.susong51.com/ssfxpg-wx/ssfxpg/anon/fxbgDetail?sessionbh={}'.format(sessionbh)
            message = {}
            message['iw'] = 99
            message['report'] = sessionbh
            cookie = headers['Cookie']
            report_headers = self.report_headers
            report_headers['Cookie'] = cookie
            self.html_download(report_url, report_headers)
            return message, sessionbh
        else:
            cookie = headers['Cookie']
            message = self.question_page(response, iw)
            return message, sessionbh

    def html_download(self, report_url, headers):
        """
        获取报告生成页 并保存
        :return:
        """
        file_path = FILEPATH_DOWN + TYPE_SOFT
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        response = requests.get(report_url, headers=headers)
        html = response.content.decode()
        down_id = report_url.split('sessionbh=')[-1]
        file_name = ''.join([file_path, '/', down_id, '.html'])
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(html)
        print(down_id, '下载完毕!')

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
        html = html.replace('\\', '')
        html = html.replace('"messages":"', '"messages":').replace('}}"', '}}')
        html = html.replace('true', '"true"').replace('false', '"false"')
        return html


if __name__ == '__main__':
    flag = FLAG
    report_clawer = ReportClawer()
    headers, response = report_clawer.start_parse()
    if flag:
        tree = Tree(FILENAME)
        response = str(response).replace("'", '"')
        response = json.loads(response)
        iw = response['messages']['currentWt']['twxsData']['twxsInfo']['nFxzs']
        if iw != 10:
            iw = 1
        else:
            iw = 2
        message = report_clawer.question_page(response, iw)
    else:
        tree = Tree(FILENAME, follow_pre=True)
        path = tree.next_path()
        print('==========', path)
    while True:
        if flag:
            path = tree.construct(message)
        while not path:
            message, sessionbh = report_clawer.process_results(response, headers)
            iw = message['iw']
            response = report_clawer.process_message(iw, message, sessionbh, headers)
            message_pro, sessionbh = report_clawer.process_results(response, headers)
            path = tree.construct(message_pro)
        tree = Tree(FILENAME, follow_pre=True)
        if not tree.curnode:
            break
        headers, response = report_clawer.start_parse()
        response = str(response).replace("'", '"')
        response = json.loads(response)
        sessionbh = response['messages']['sessionInfo']['cBh']
        for i in path:
            print(i)
            iw = i['iw']
            if iw == 1:
                form_data = {
                    'sessionbh': sessionbh,
                    'wtbh': i['id_question'],
                    'czms': i['item'][0]
                }
                response = report_clawer.post_body(report_clawer.do_next_url, headers, form_data)
            elif iw == 2:
                form_data = {
                    'sessionbh': sessionbh,
                    'wtbh': i['id_question'],
                    'czms': i['item'][0]
                }
                response = report_clawer.post_body(report_clawer.do_next_url, headers, form_data)
            message, sessionb = report_clawer.process_results(response, headers)
            flag = True
