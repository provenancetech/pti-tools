from jwcrypto import jwk, jwt, jws
from jwcrypto.common import json_encode, json_decode
import sys
import os

if os.path.isfile(sys.argv[1]):
    key = jwk.JWK.from_json(open(sys.argv[1]).read())
    print(key.export_public())
else:
    key = jwk.JWK.generate(kty='RSA', size=4096, kid=sys.argv[1])
    print(key.export(private_key=True))
