# -*- coding: utf-8 -*-

import urllib.request
import json
import time

class Yougile:
    def __init__(self, bearer):
        self.__bearer = bearer

    def call(self, method, url, data):
        headers = {
            "Authorization": "Bearer " + self.__bearer,
            "Content-Type": "application/json"
        }

        encoded_data = None
        jsondata = None
        if data is not None:
            jsondata = json.dumps(data)
            encoded_data = jsondata.encode("utf-8")

        req = urllib.request.Request(url, encoded_data, headers, method=method)

        print("Method = " + method + ", url = " + url + ", body=\'" + str(jsondata) + "\'")

        time.sleep(1.5)
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as ex:
            print("Error: " + str(ex))

        if 200 <= response.status < 300:
            response_data = response.read().decode("utf-8")
            return json.loads(response_data)
        else:
            raise "Error reading url " + url + ": response" + str(response.status)

    def get(self, url, data=None):
        return self.call('GET', url, data)

    def post(self, url, data):
        return self.call('POST', url, data)

    def get_existing_users(self):
        data = self.get("https://yougile.com/api-v2/users")
        ret = {}
        for info in data['content']:
            ret[info['email']] = info['id']
        return ret

    def get_existing_boards(self):
        data = self.get("https://yougile.com/api-v2/boards")
        # todo