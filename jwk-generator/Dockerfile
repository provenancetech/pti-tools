FROM python:3.8-slim

WORKDIR /app
RUN pip install jwcrypto
ADD keygen.py /app/keygen.py

ENTRYPOINT ["python3","-u","/app/keygen.py"]
