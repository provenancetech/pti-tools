import uuid
import requests
from subprocess import check_output
import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("url")
args = parser.parse_args()

if __name__ == """__main__""":
        try:
            os.mkdir('users')
        except:
            print("Creation of the directory %s failed")

        for cpt in range(10) :
            result = check_output(["./getToken.sh", args.url + "/auth/jwt", os.environ['KEYFILE'], os.environ['CLIENT_ID'], '{"url":"/users","method": "POST"}'])
            req = json.loads(result)
            token = req["accessToken"]
            userId = str(uuid.uuid4())
            firstName = str(uuid.uuid4())
            lastName = str(uuid.uuid4())
            headers = dict([("Content-Type", "application/json"),
                        ("x-pti-client-id", os.environ['CLIENT_ID']),
                        ("x-pti-token", token)])
            body = '{"id":"' + userId + '","type": "PERSON","name":{"firstName": "' + firstName + '","lastName":"' + lastName + '"}}'
            newUserResult = requests.post(args.url + "/users", body, headers = headers)
            newUser = json.loads(newUserResult.content)
            f = open('users/' + str(cpt) + ".json", "a")
            jsonString = json.dumps(newUser)
            f.write(jsonString)

