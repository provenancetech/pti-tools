#!/bin/sh
python ../signed-request-maker/signed_request_maker.py --k $2 --clientId "$3"  --data '{"url":"/api/transactions/worldpay","method": "POST"}' $1
