export KEYFILE=~/keys_pti/cucumber_key.pem
export CLIENT_ID=3450582c-1955-11eb-adc1-0242ac120002
locust -f ./load-test.py --host  https://load.apidev.pticlient.com/v0 > result.txt