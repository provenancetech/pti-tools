from flask import Flask, render_template
import requests
from hashlib import sha256
import os
from time import gmtime
import urllib.parse
from jwcrypto import jwk, jws
from jwcrypto.common import json_encode, json_decode
import json

app = Flask('example_passthrough')
@app.route('/')
def payment_page():
    #Get token from server
    content_type = 'application/json; charset=utf-8'
    method = "POST"
    data = '{"url":"/api/transactions/worldpay","method": "POST"}'
    payload = method + "\n"
    payload = payload + get_content_sha256(data.encode('UTF-8')) + "\n"
    payload = payload + 'content-type:' + content_type + "\n"
    date = get_http_gmt()
    url = os.environ['TARGET_SERVER'] + "/auth"
    payload = payload + 'date:' + date + '\n'
    payload = payload + f'x-pti-client-id:{os.environ["CLIENT_ID"]}' + '\n'
    payload = payload + urllib.parse.urlparse(url).path
    signature = sign(os.environ["CLIENT_ID"], payload.encode('UTF-8'))
    resp = requests.post(url, data=data.encode('UTF-8'),
                         headers={"Content-Type": content_type, "Date": date, "x-pti-signature": signature,
                                  "x-pti-client-id": os.environ["CLIENT_ID"]})
    response_json = json.loads(resp.content)
    token = response_json["accessToken"]
    return render_template('payment_page.html', token=token,
                           fiatInUrl=os.environ['TARGET_SERVER'] + '/transactions/worldpay', clientId=os.environ["CLIENT_ID"])

def get_content_sha256(data):
    m = sha256(data)
    return m.hexdigest().upper()

def sign(client_id, payload, compact=True):
    key = jwk.JWK.from_json(open(os.environ["KEY_FILE"], 'rb').read())
    public_key = jwk.JWK()
    public_key.import_key(**json_decode(key.export_public()))
    jwstoken = jws.JWS(payload)
    jwstoken.add_signature(key, None,
                            json_encode({"alg": "RS512",
                                         "cid": client_id,
                                         "kid": public_key.thumbprint()}), None)
    signed_payload = jwstoken.serialize(compact)
    return signed_payload

def get_http_gmt():
    """ Gets http gmt time. Returns a string."""
    days = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
    months = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
    time = gmtime()
    http_time = ["{day},".format(day = days[time.tm_wday])]
    http_time.append("{:02}".format(time.tm_mday))
    http_time.append("{month}".format(month = months[time.tm_mon]))
    http_time.append("{year}".format(year = time.tm_year))
    http_time.append("{:02}:{:02}:{:02}"          .format(time.tm_hour, time.tm_min, time.tm_sec))
    http_time.append("GMT")
    return " ".join(http_time)


def run_server():
    app.run(port=8000, threaded=True, host='0.0.0.0')

if __name__ == '__main__':
    run_server()