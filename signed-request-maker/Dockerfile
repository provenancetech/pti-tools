FROM python:3.8-slim

RUN pip install jwcrypto requests requests_toolbelt
WORKDIR /app
ADD signed_request_maker.py /app/

ENTRYPOINT ["python3","-u","signed_request_maker.py"]
