import uuid
from locust import HttpUser, task, between
from subprocess import check_output
import json
import os

class PtiUser(HttpUser):
    wait_time = between(5, 9)

    @task(5)
    def request(self):
        result = check_output(["./getToken.sh", self.client.base_url + "/auth", os.environ['KEYFILE'], os.environ['CLIENT_ID']])
        req = json.loads(result)
        token = req["accessToken"]
        uuidStr = str(uuid.uuid4())
        headers = dict([("Content-Type", "application/json"),
                    ("x-pti-client-id", os.environ['CLIENT_ID']),
                    ("x-pti-token", token)])
        body = '{"statementMessage": "pti-load-test","orderDescription": "toto","orderCode": "' + uuidStr + '","orderContent": "<a>test</a>","fullName": "Alexandre Begin","tokenizedPaymentData": "eyJhbGciOiJSU0ExXzUiLCJlbmMiOiJBMjU2R0NNIiwia2lkIjoiMSIsImNvbS53b3JsZHBheS5hcGlWZXJzaW9uIjoiMS4wIiwiY29tLndvcmxkcGF5LmxpYlZlcnNpb24iOiIxLjAuMiIsImNvbS53b3JsZHBheS5jaGFubmVsIjoiamF2YXNjcmlwdCJ9.x1C4bkBej9dy6Ij14IONjyd9WwJ-y-xcEncalprEAYjRmDtDVJ993IZBFZclWFeQFi_TckSKA4zRov5j8VJAoqr1OmnruHrqpXxscJjYO_DO5pvzTLhaaUMdyQAxeBzzHChrnPaacjAQJox0X1iA3xPcgYrszgP5o5zoPIepRYCdRxQlSkVMfhbOvyT4aBUZgJdwYizeaywOCP4DiC4wBe7ckDaA7ExY8dgCOzlMG9eUrLdxDLyuZhHQM68257nRzCT1JaOUAdY40Cpb_2xBDdIPaPhGbRNuv1Rmh-NGGQKCCN70kArLFMm8pePaDn3-ZFs5DkewsaUZbI9BTEh4Jw.uCWFJKmOHy_CfU_z.0xeUdg-EcLeYnRkCKG8ISWGcVJgNZ3H5jIx5YX3umaPG3Jk2PCRE9gXowZBQADkFbdJJmiR0bdhPYUUqPdmul1VEnJbaHkTE1J7KxUmnGFFMYXNuhDfRQtRKxSEHQwgBP_-B4cJOe4sTW0gquTDQOgbe._lZhufFsXYZ7LgU_WYNSNA","address": {"streetAddress": "address","city": "city","postalCode": "AAAAA","stateCode": {"code": "US-CA"},"country": {"code": "US"}},"amount": 10.515,"currency": "USD"}'
        self.client.post(self.client.base_url + "/transactions/worldpay", body, headers = headers)
