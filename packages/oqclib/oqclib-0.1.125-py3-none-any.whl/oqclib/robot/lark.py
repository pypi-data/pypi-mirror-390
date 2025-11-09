import json
import logging
from time import sleep
from oqclib.utils.http_util import send_post_request_with_retries
from enum import Enum


logger = logging.getLogger(__name__)

class LarkMsg():
    def __init__(self, keys_dict):
        self.keys_dict = keys_dict
        self.request_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/'

    def show_lark(self):
        '''
        show available lark config
        :return: lark keys available in config
        '''
        print(self.keys_dict.keys())

    def send_msg(self, robot: str, msg: str):
        '''
        send lark message
        :param msg: message to send
        :return:
        '''
        key = self.keys_dict[robot]

        mentioned_list = ['@all']

        textJSON = [[{'tag': 'text', 'text': msg}]]

        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }

        textMsg = {
            'msg_type': 'post',
            'content': {'post': {'en_us': {'content': textJSON}}}
        }

        se = json.dumps(textMsg)
        #r = requests.post(self.request_url + key, data=se, headers=headers)
        url = self.request_url + key
        r = send_post_request_with_retries(url, se, headers=headers)
        return r.json()
        # logger.info("Sending lark resp: {}".format(r.text))


    def send_card(self, robot, card_body: dict):
        '''
        send lark message card
        :param title: lark card title
        :param msg: message to send
        :param robot: lark key name as defined in lark_config
        :return:
        '''
        key = self.keys_dict[robot]
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        textMsg = {
            "msg_type": "interactive",
            "card": card_body
        }
        se = json.dumps(textMsg)
        #r = requests.post(self.request_url + key, data=se, headers=headers)
        url = self.request_url + key
        # INFO       2025-09-07 00:00:01,649 -8s  11  : POST Response: 200 {"code":11232,"data":{},"msg":"frequency limited psm[lark.oapi.app_platform_runtime]appID[1500]"}

        retries = 3
        json_data = {}
        for i in range(retries + 1):
            r = send_post_request_with_retries(url, se, headers=headers)
            json_data = r.json()
            if json_data.get('code', 0) == 0:
                break
            sleep(0.7)
        return json_data
        # logger.info("Sending lark resp: {}".format(r.text))


class StatusColor(Enum):
    BLUE = "BLUE"
    GRAY = "GRAY"
    INDIGO = "INDIGO"
    WATHET = "WATHET"
    GREEN = "GREEN"
    TURQUOISE = "TURQUOISE"
    YELLOW = "YELLOW"
    LIME = "LIME"
    RED = "RED"
    ORANGE = "ORANGE"
    PURPLE = "PURPLE"
    VIOLET = "VIOLET"
    CARMINE = "CARMINE"
