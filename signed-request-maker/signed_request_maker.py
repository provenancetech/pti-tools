from hashlib import sha256
from time import gmtime
import requests
import urllib.parse
import argparse
from jwcrypto import jwk, jws
from jwcrypto.common import json_encode, json_decode
from requests_toolbelt.utils import dump
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key-path", help="Path to the JWK private key.")
parser.add_argument("-d", "--data", help="The data to POST; implies POST.")
parser.add_argument("-c", "--clientId", help="PTI client ID (guid)")
parser.add_argument("--destination", help="Where to send the request")
parser.add_argument("--content-type", default="application/json; charset=utf-8")
parser.add_argument("--debug", action='store_true', help="Output the calculated Payload and the Signature to stderr")
parser.add_argument("url")
args = parser.parse_args()

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

def get_content_sha256(data):
    m = sha256(data)
    return m.hexdigest().upper()

def sign(client_id, payload, compact=True):
    key = jwk.JWK.from_json(open(args.key_path, 'rb').read())
    public_key = jwk.JWK()
    public_key.import_key(**json_decode(key.export_public()))
    jwstoken = jws.JWS(payload)
    jwstoken.add_signature(key, None,
                            json_encode({"alg": "RS512",
                                         "cid": client_id,
                                         "kid": public_key.thumbprint()}), None)
    signed_payload = jwstoken.serialize(compact)
    return signed_payload

if __name__ == """__main__""":

    method = "GET"
    if args.data:
        method = "POST"

    payload = method + "\n"
    if method == "POST":
        payload = payload + get_content_sha256(args.data.encode('UTF-8')) + "\n"
        payload = payload + 'content-type:' + args.content_type + "\n"
    else:
        payload + "\n\n"

    date = get_http_gmt()
    payload = payload + 'date:' + date + '\n'
    payload = payload + f'x-pti-client-id:{args.clientId}' + '\n'
    payload = payload + urllib.parse.urlparse(args.url).path
    signature = sign(args.clientId, payload.encode('UTF-8'))

    if args.debug:
        print(f'Payload: {payload}', file=sys.stderr)
        print(f'Signature (JWS): {signature}', file=sys.stderr)

    if args.destination is None:
        args.destination = args.url

    if method == "POST":
        resp = requests.post(args.destination, data = args.data.encode('UTF-8'), headers={"Content-Type": args.content_type, "Date": date, "x-pti-signature": signature, "x-pti-client-id": args.clientId})
    else:
        resp = requests.get(args.destination, headers={"Date": date, "x-pti-signature": signature,  "x-pti-client-id": args.clientId})

    data = dump.dump_all(resp).decode('utf-8')
    response_idx = data.rfind('\r\n> \r\n')
    print(data[:response_idx], file=sys.stderr)
    print(data[response_idx+4:])

