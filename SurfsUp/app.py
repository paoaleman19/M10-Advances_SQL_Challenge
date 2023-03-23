#Import Dependencies
import matplotlib
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Station = Base.classes.station
Measurements = Base.classes.measurement


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Paola's challenge API!<br/>"
        f"Available Routes:<br/>"
        
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        
        f"/api/v1.0/stations<br/>"
        f"- Station names and totals <br/>"
        
        f"/api/v1.0/tobs<br/>"
        f"- List of previous year temperatures <br/>"
        
        f"/api/v1.0/<start><br/>" 
        f"- Calculation of the AVG/MIN/MAX temperature for dates greater than or equal to a specific date <br/>"
        
        f"/api/v1.0/<start>/<end><br/>" 
        f"-For a specified start, calculate TMIN, TAVG, and TMAX for all the dates between a given start and end date <br/>"
        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Starting from the most recent data point in the database. 
    most_recent_date = session.query(func.max(measurement.date)).scalar()

    #to make it into a date type
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    
    # Calculate the date one year from the last date in data set.
    year_ago= most_recent_date - timedelta(days=365)

    precipitation_year_ago = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).order_by(measurement.date).all()
    
    #Create a list
    precipitation_totals = []
    for result in precipitation:
        row = {}
        row["date"] = precipitation[0]
        row["prcp"] = precipitation[1]
        precipitation_totals.append(row)
    #Return a JSON list of stations from the dataset.
    return jsonify(precipitation_totals)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query the dates and temperature observations of the most-active station for the previous year of data.
    stations = session.query(measurement.station, func.count(measurement.date)).group_by(measurement.station).order_by(func.count(measurement.date).desc()).all()

    session.close()

    #Create a list
    stations_list: []
    for station,count in stations:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["count"] = count
        stations_list.append(stations_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Most active station data
    USC00519281_data = session.query(func.max(measurement.date)).filter(measurement.station == 'USC00519281').scalar()
    USC00519281_data = datetime.strptime(USC00519281_data, '%Y-%m-%d').date()
    
    # Calculate the date one year from the last date in data set.
    USC00519281_last12mo = USC00519281_data - timedelta(days=365)
   
    #Query the last year
    USC00519281_temp = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date > USC00519281_last12mo).order_by(measurement.date).all()

    session.close()

    #Create a list
    USC00519281_temp_list: []
    for date,tobs in USC00519281_temp_list:
        USC00519281_temp_dict = {}
        USC00519281_temp_dict ["date"] = date
        USC00519281_temp_dict ["tobs"] = tobs
        USC00519281_temp_list.append(USC00519281_temp_dict)
    return jsonify(USC00519281_temp_list)

@app.route("/api/v1.0/<start>")
def trip(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the min, max, and avg temperatures for all dates greater than or equal to the start date
    start_temps = session.query(func.avg(measurement.tobs)), func.min(measurement.tobs),func.max(measurement.tobs).filter(measurement.date >= start).all()

    session.close()
    #Create a dictionary for the temperature data
    temps_dict = {}
    temps_dict ['TAVG'] = start_temps [0][0]
    temps_dict ['TMIN'] = start_temps [0][1]
    temps_dict ['TMAX'] = start_temps [0][2]

    return jsonify(temps_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_to_end(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Convert the start and end date strings to datetime objects  
    start_date= datetime.strptime(start, '%Y-%m-%d').date()
    end_date= datetime.strptime(end,'%Y-%m-%d').date()

    # Query the min, max, and avg temperatures for a specified start date and end date
    temp_data = session.query(func.avg(measurement.tobs)),func.min(measurement.tobs), func.max(measurement.tobs).filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    session.close()

    #Dictionary to store temp data
    temperature_dict = {}
    temperature_dict ['start_date'] = start_date
    temperature_dict ['end_date'] = end_date
    temperature_dict ['TAVG']= temperature_data [0][0]
    temperature_dict ['TMIN']= temperature_data [0][1]
    temperature_dict ['TMAX']= temperature_data [0][2]

    return jsonify(temperature_dict)

if __name__ == '__main__':
    app.run(debug=True)