import uuid
from subprocess import check_output
import json
import os
import random
from datetime import datetime
from locust import HttpUser, task, between

class PtiLoadTests(HttpUser):
    wait_time = between(5, 9)


    @task(1)
    def request(self):
        #self = {"client":{"base_url":"https://load.apidev.pticlient.com/v0"}}
        filepath = "./users/" + str(random.randint(0, 9)) + ".json";
        print(filepath)
        print(os.environ['KEYFILE'])
        f = open(filepath, "r")
        user = json.loads(f.read())
        userId = user['id']
        url = '/users/' + userId + '/transactions/fiat/funding'
        result = check_output(
            ["./getToken.sh", self.client.base_url + "/auth/jwt", os.environ['KEYFILE'], os.environ['CLIENT_ID'],
             '{"url":"' + url + '","method": "POST"}'])
        req = json.loads(result)
        token = req["accessToken"]
        requestId = str(uuid.uuid4())
        headers = dict([("Content-Type", "application/json"),
                        ("x-pti-client-id", os.environ['CLIENT_ID']),
                        ("x-pti-request-id", requestId),
                        ("x-pti-token", token)])

        f = open("./requests/encryptedFiatIn.json", "r")
        body = json.loads(f.read())
        body['initiator'] = user
        body['date'] = datetime.now().astimezone().replace(microsecond=0).isoformat()
        self.client.post(self.client.base_url + url, json.dumps(body), headers=headers)