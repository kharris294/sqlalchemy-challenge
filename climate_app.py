import numpy as np

import datetime as dt
from datetime import timedelta, datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct, text, desc

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
#engine = create_engine("sqlite:///Resources/hawaii.sqlite")
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<br/>"
        f"/api/v1.0/"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation data"""
    # Query all passengers
    annual_rainfall = session.query(Measurement.date,  Measurement.prcp).order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    all_rain = dict(annual_rainfall)

    return jsonify(all_rain)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation data"""
    # Query all passengers
    station_list_query = session.query(Measurement.station).group_by(Measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_list_query))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """determine the most active station within the past year and return the temperature values for it."""
    # Query all passengers
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_date = list(np.ravel(date))[0]
    last_date = dt.datetime.strptime(end_date,'%Y-%m-%d' )
    begin_date = last_date - timedelta(days=365)
    station_ranking = session.query(Measurement.station, func.count(Measurement.date).label('station_count')).filter(Measurement.date >= begin_date).group_by(Measurement.station).order_by(desc('station_count')).all()
    top_station = station_ranking[0][0]
    tobs_query = session.query(Measurement.date,  Measurement.tobs).filter(Measurement.date >= begin_date).filter(Measurement.station == top_station).order_by(Measurement.date).all()
    tobs_list = list(np.ravel(tobs_query))
    session.close()

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):

#  check to see if the date format is correct before query

    try:
        start_date = dt.datetime.strptime(start,'%Y-%m-%d' )
    except ValueError:
        message = {"error": f"enter a date with the format YYYY-MM-DD"}
        return jsonify(message), 404

    # Create our session (link) from Python to the DB
    session = Session(engine)

#run query on the date entered
#determine last date of data

    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end_date = dt.datetime.strptime(list(np.ravel(date))[0],'%Y-%m-%d' )

#determine first date of data

    date = session.query(Measurement.date).order_by(Measurement.date).first()
    begin_date = dt.datetime.strptime(list(np.ravel(date))[0],'%Y-%m-%d' )

#check if range is correct
    if (start_date >= begin_date) & (start_date <= end_date):
        temp_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs) ).filter(Measurement.date >= start_date).all()
        temp_summary = list(np.ravel(temp_query))
        message = temp_summary
    else:
        message = {"error": f"date {start} is not within the range of {begin_date} and {end_date}."}
        return jsonify(message), 404

    session.close()

    return jsonify(message)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    try:
        start_date = dt.datetime.strptime(start,'%Y-%m-%d' )
        end_date = dt.datetime.strptime(end,'%Y-%m-%d' )
    except ValueError:
        message = {"error": f"enter a date with the format YYYY-MM-DD"}
        return jsonify(message), 404

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #run query on the date entered
    #determine last date of data

    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(list(np.ravel(date))[0],'%Y-%m-%d' )

    #determine first date of data

    date = session.query(Measurement.date).order_by(Measurement.date).first()
    begin_date = dt.datetime.strptime(list(np.ravel(date))[0],'%Y-%m-%d' )

    #check if range is correct
    date_range_bool = (start_date >= begin_date) & (start_date <= last_date) & (end_date >= begin_date) & (end_date <= last_date)
    if date_range_bool :
        temp_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs) ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
        temp_summary = list(np.ravel(temp_query))
        message = temp_summary
    else:
        message = {"error": f"start date {start_date} or end date {end_date} is not within the range of {begin_date} and {end_date}."}
        return jsonify(message), 404

    session.close()

    return jsonify(message)

if __name__ == '__main__':
    app.run(debug=True)