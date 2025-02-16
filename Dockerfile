# Dockerfile, Image, Container
FROM python:3.11

ADD main.py .
ADD .env .

RUN pip install requests python-dotenv pandas matplotlib plotly aqipy-atmotech streamlit

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]