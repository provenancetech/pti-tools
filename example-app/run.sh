#!/bin/sh
export FLASK_APP=example_passthrough.py
export TARGET_SERVER=https://forte.ptidev.xyz
export KEY_FILE=~/keys_pti/forte_test.jwk
export CLIENT_ID=745e2d99-0be3-411f-8325-cb7a9ccfef35
flask run