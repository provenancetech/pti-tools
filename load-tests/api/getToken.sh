#!/bin/sh
python ../../signed-request-maker/signed_request_maker.py --k $2 --clientId "$3"  --data "$4" $1
