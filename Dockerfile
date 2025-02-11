# Dockerfile, Image, Container
FROM python:3.11

ADD main.py .

RUN pip install requests python-dotenv twilio

CMD ["python", "./main.py"]