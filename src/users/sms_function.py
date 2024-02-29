import json
import os
import requests
from background_task import background



LOGIN_BODY_ID = '723480'
LOGIN_DATA = {"name": "Code", "value": ''}


class SmsCenter:
    def __init__(self, sms_body, receivers, sms_template_id=None):
        self.receivers = receivers
        self.sms_template_id = sms_template_id
        if sms_template_id:
            self.sms_body = self.get_body(sms_body)
        else:
            self.sms_body = sms_body

    def get_body(self, data):
        if self.sms_template_id == LOGIN_BODY_ID:
            sms_body = LOGIN_DATA
            sms_body['value'] = data
            return sms_body

    def send_sms(self):
        if isinstance(self.receivers, list):
            for phone_number in self.receivers:
                self.send_by_sms_type(phone_number)
        else:
            self.send_by_sms_type(self.receivers)

    def send_by_sms_type(self, phone_number):
        if self.sms_template_id:
            self.send_sms_with_template(phone_number)
        else:
            # call function for sms without template
            pass

    def send_sms_with_template(self, phone_number):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain',
            'x-api-key': os.getenv('SMS_APIKEY')
        }
        send_url = "https://api.sms.ir/v1/send/verify"
        body_send_sms = {
            "mobile": "{}".format(phone_number),
            "templateId": self.sms_template_id,
            "parameters": [
                self.sms_body
            ]
        }
        response = requests.post(send_url, data=body_send_sms, headers=headers)
        json_data = json.loads(response.text)
        return json_data


