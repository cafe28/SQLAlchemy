# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from dateutil import parser, relativedelta


from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Instructions/Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
app.route("/")


# List all the available routes.
def welcome():
    return f"Available Routes:<br/>" f"/api/v1.0/precipitation<br/>" f"/api/v1.0/stations<br/>" f"/api/v1.0/tobs<br/>" f"/api/v1.0/start_date<br/>" f"/api/v1.0/start_date/end_date"


# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = parser.parse(last_date[0])
    year_ago = last_date - relativedelta.relativedelta(years=1)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    session.close()
    precip = {date: prcp for date, prcp in results}
    return jsonify(precip)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(results))
    return jsonify(stations)


# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = parser.parse(last_date[0])
    year_ago = last_date - relativedelta.relativedelta(years=1)
    most_active = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).filter(Measurement.station == most_active[0]).all()
    session.close()
    tobs = list(np.ravel(results))
    return jsonify(tobs)


# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()
    start = list(np.ravel(results))
    return jsonify(start)


# Run the Flask app on port 5001
if __name__ == "__main__":
    app.run(port=5001, debug=True)

# Close the session
session.close()
