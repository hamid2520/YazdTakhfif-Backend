import json
import os
from http.client import HTTPSConnection




LOGIN_BODY_ID = 964987
LOGIN_DATA = "{\n      \"name\": \"CODE\",\n      \"value\": \"000000\"\n    }"


class SmsCenter:
    def __init__(self, sms_body, receivers, sms_template_id=None):
        self.receivers = receivers
        self.sms_template_id = int(sms_template_id)
        if sms_template_id:
            self.sms_body = self.get_body(sms_body)
        else:
            self.sms_body = sms_body

    def get_body(self, data):
        if self.sms_template_id == LOGIN_BODY_ID:
            sms_body = LOGIN_DATA.replace('000000', data)
            return sms_body

    def send_sms(self):
        if isinstance(self.receivers, list):
            for phone_number in self.receivers:
                self.send_by_sms_type(phone_number)
        else:
            result = self.send_by_sms_type(self.receivers)
            if result['status'] != 1:
                return self.send_sms()
            else:
                return result
    def send_by_sms_type(self, phone_number):
        if self.sms_template_id:
            return self.send_sms_with_template(phone_number)
        else:
            # call function for sms without template
            pass

    def send_sms_with_template(self, phone_number):
        conn = HTTPSConnection("api.sms.ir")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain',
            'x-api-key': os.getenv("SMS_APIKEY", 'GN8Vl0fjusksXpijEq2msm2Qpr6gmfeKl3siGFv3TSD5BnPkQG2DpXoew2VHXPLR')
        }
        conn.request("POST", "/v1/send/verify", self.generate_payload(phone_number), headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))


    def generate_payload(self, phone_number):
        payload = "{\n  \"mobile\": \"Your Mobile\",\n  \"templateId\": YourTemplateID,\n \"parameters\": [\n    dictionary  ]\n}"
        payload = payload.replace("YourTemplateID", str(self.sms_template_id))
        payload = payload.replace("Your Mobile", phone_number)
        payload = payload.replace("dictionary", self.sms_body)
        return payload