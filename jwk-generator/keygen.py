import argparse
import os
import sys
import uuid
from jwcrypto import jwk, jwt, jws
from jwcrypto.common import json_encode, json_decode

def environ_or_default(key, default):
    return (
        {'default': os.environ.get(key)} if os.environ.get(key)
        else {'default': default}
    )

p = argparse.ArgumentParser()
subparsers = p.add_subparsers(help='sub-command help', dest='subparser_name')
p_genkey = subparsers.add_parser('genkey', help='Generates a new private key and writes it to stdout')
p_genkey.add_argument('--kid', help='ID of the generated key. UUID by default.', **environ_or_default('KEY_ID', str(uuid.uuid4())))
p_pubkey = subparsers.add_parser('pubkey', help='Reads a private key from stdin and writes a public key to stdout')
p_pubkey.add_argument('-t', '--thumbprint', action='store_true', help='Get only the thumbprint of the public key')
args = p.parse_args()

if args.subparser_name is None:
    p.print_help()
    exit(-1)

if args.subparser_name == 'genkey':
    key = jwk.JWK.generate(kty='RSA', size=4096, kid=args.kid)
    print(key.export(private_key=True))
elif args.subparser_name == 'pubkey':
    key = jwk.JWK.from_json(sys.stdin.read())
    if args.thumbprint:
        print(key.thumbprint())
    else:
        print(key.export_public())
