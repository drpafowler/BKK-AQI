# Project Title
## My package
This is a project to create an app that does stuff.  The stuff that it does is to access an air quality API periodically.  When the airquality is bad, e.g. in the unhealthy range, it sends an alert to the user.  The user can then take action to protect their health.  It also sends an air quality forecast for the day at 6AM.  

## Author(s)
Philip Fowler

# Usage
Instructions on how to use your project.
You will need an WAQI API key from https://aqicn.org/api/ to use this project  

## Installation  
### Phone Notifications - Proof of Concept - located in the archived folder
First, use the .env example file to add your own information.  Save it as .env Then, run the following command to install the necessary packages:
```
# Dockerfile, Image, Container
FROM python:3.11

ADD main.py .
ADD .env .

RUN pip install requests python-dotenv twilio

CMD ["python", "./main.py"]
```
Note: the first version of this used Twilio.  The subsequent version used pushover.  Pushover is a better choice.

### Air Quality Notebook - Used to determine how to perform calculations
This was done in the notebook file AQI-Analysis.ipynb
The notebook was developed in conjunction with the bkk_aqi.db database.  The database was created by running consumer.py.




