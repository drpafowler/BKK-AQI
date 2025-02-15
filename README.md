# Project Title
## My package
This is a project to create an app that does stuff.  The stuff that it does is to access an air quality API periodically.  When the airquality is bad, e.g. in the unhealthy range, it sends an alert to the user.  The user can then take action to protect their health.    

There are a number of different approaches to calculating an air quality index.  Different countries have different formulas for doing so.  The dashboard for this project willl compare the different formulas and show the results of several different approaches.  The notification program will use the US EPA formula to determine the air quality index.

Note that the AQI is a number that is used to communicate how polluted the air is.  The higher the number, the more polluted the air is.  The AQI is calculated based on the concentration of pollutants in the air.  The pollutants that are used to calculate the AQI are: PM2.5, PM10, O3, NO2, SO2, and CO.  The AQI is calculated based on the concentration of these pollutants in the air.  In many places on the interweb you will see the PM2.5 value reported as the AQI.  PM25 is a measure of a certain size of particulate. However, sometimes it is not the particulates that are the problem.  Sometimes it is the gases that are the problem.  Thus, a properly calculated AQI will take into account all of the pollutants.  


## Author(s)
Philip Fowler

# Usage
## Instructions on how to use this project.
You will need an WAQI API key from https://aqicn.org/api/ to use this project  
You will need a Pushover account to use this project.  You can get one at https://pushover.net/

You will need to create a .env based on the env example template.

Create your usual virtual environment based on python 3.11. This won't work with 3.12. I am assuming that you know how to do this. If you don't, you can find instructions at https://docs.python.org/3/library/venv.html

## You will need to install the necessary packages.  You can do this by running the following command:

```python
pip install -r requirements.txt
```

## You are going to need to start your usual Kafka and Zookeeper services.  You can do this by running the following command:

```
docker-compose up
```

Or be lazy like I am and just click the Docker Desktop icon on your toolbar.  This will start the services for you too.

## Start the producer by running the following command:

```
python3.11 producer.py
```

## Start the consumer by running the following command:
```
python3.11 consumer.py
```

Note: The consumer will create a database called bkk_aqi.db.  This database will be used to store the air quality data.  


## To start the notification program, you will need to run the following command:
``` 
python3.11 main.py
```

## To start the streamlit dashboard, you will need to run the following command:

```
streamlit run app.py
```


# Archived Materials - This is just for reference  
## Phone Notifications - Proof of Concept - located in the archived folder
First, use the .env example file to add your own information.  Save it as .env Then, run the following command to install the necessary packages:

# Dockerfile, Image, Container
FROM python:3.11

ADD main.py .
ADD .env .

RUN pip install requests python-dotenv twilio

CMD ["python", "./main.py"]
```
Note: the first version of this used Twilio.  The subsequent version used pushover.  Pushover is a better choice.

## Air Quality Notebook - Used to determine how to perform calculations
This was done in the notebook file AQI-Analysis.ipynb
The notebook was developed in conjunction with the bkk_aqi.db database.  The database was previously created by running consumer.py
The notebook does not automatically update from the database.  You will have to keep clicking run all to update things.  This is not ideal.  However, it is a proof of concept.  The final version will be a streamlit dashboard that will automatically update.




