# Dockerfile, Image, Container
FROM python:3.11

ADD main.py .
ADD app.py .
ADD .env .

RUN pip install requests python-dotenv pandas matplotlib plotly aqipy-atmotech streamlit 

EXPOSE 8501

CMD ["sh", "-c", "python main.py & streamlit run app.py"]