FROM python:3.11

ADD main.py .
ADD app.py .
ADD .env .

RUN mkdir -p /data
RUN mkdir -p /assets
ADD data/* /data/
ADD assets/* /assets/

RUN pip install --no-cache-dir requests python-dotenv pandas matplotlib plotly aqipy-atmotech streamlit seaborn

EXPOSE 8501

HEALTHCHECK CMD ["curl", "-f", "http://localhost:8501"] # Add a healthcheck

CMD ["sh", "-c", "python3 main.py"]