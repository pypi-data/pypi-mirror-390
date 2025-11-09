import time
import hmac
import hashlib
import base64
import json
from urllib.parse import quote_plus
from oqclib.utils.http_util import send_post_request_with_retries
import logging

logger = logging.getLogger(__name__)


class DingTalkRobot:
    def __init__(self, keys_dict):
        self.keys_dict = keys_dict
        self.request_url = 'https://oapi.dingtalk.com/robot/send'

    def generate_sign(self, timestamp, secret: str):
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = quote_plus(base64.b64encode(hmac_code))
        return sign

    def get_request_url(self, robot):
        timestamp = str(round(time.time() * 1000))
        key = self.keys_dict[robot]

        sign = self.generate_sign(timestamp, key['secret'])

        url = self.request_url + '?access_token=' + key['token'] + '&timestamp=' + timestamp + '&sign=' + sign
        return url

    def send_msg(self, robot: str, message: str):
        url = self.get_request_url(robot)

        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        logger.info(f"Sending message to DingTalk Robot: {robot}, message: {message}")

        response = send_post_request_with_retries(url, headers=headers, data=json.dumps(data))
        return response.json()

    def send_card(self, robot: str, card: dict):
        url = self.get_request_url(robot)

        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data = {
            "msgtype": "markdown",
            "markdown": card
        }
        logger.info(f"Sending message to DingTalk Robot: {robot}, message: {card}")

        response = send_post_request_with_retries(url, headers=headers, data=json.dumps(data))
        return response.json()
