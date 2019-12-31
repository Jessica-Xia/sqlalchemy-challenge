import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
    """List all routes that are available."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<date><br/>"
        f"/api/v1.0/<start_date>/<end_date><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a Dictionary using date as the key and prcp as the value"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()

    # Convert list of tuples into normal list
    all_precipitation= list(np.ravel(results))
    all_precipitation = {all_precipitation[i]: all_precipitation[i + 1] for i in range(0, len(all_precipitation), 2)} 
    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stationlisting():
    # Return a JSON list of stations from the dataset.
    session = Session(engine)
    results = session.query(Station.name, Station.station, Station.elevation).all()

    session.close()

    station_list=[]
    for i in results:
        row={}
        row['name']=i[0]
        row['station']=i[1]
        row['elevation']=i[2]
        station_list.append(row)
    
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    #query for the dates and temperature observations from a year from the last data point.
    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    session = Session(engine)
    results=session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-24", Measurement.date <= "2017-08-23" ).all()
    
    session.close()

    tobs_list = []
    for result in results:
        row = {}
        row["Station"] = result[0]
        row["Date"] = result[1]
        row["Temperature"] = int(result[2])
        tobs_list.append(row)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<given_date>")
def time_test(given_date):
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given date
    session = Session(engine)
    results=session.query(func.max(Measurement.tobs), func.avg(Measurement.tobs),func.min(Measurement.tobs)).\
        filter(Measurement.date >= given_date).all()
    
    session.close()

    thedate_list =[]
    for result in results:
        row = {}
        row["max_tobs"]=result[0]
        row["avg_tobs"]=result[1]
        row["min_tobs"]=result[2]
        thedate_list.append(row)

    return jsonify(thedate_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def period_test(start_date, end_date):
    session = Session(engine)
    results=session.query(Measurement.date, func.max(Measurement.tobs), func.avg(Measurement.tobs),func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    
    session.close()

    theperiod_list =[]
    for result in results:
        row = {}
        row['date']=result[0]
        row["max_tobs"]=result[1]
        row["avg_tobs"]=result[2]
        row["min_tobs"]=result[3]
        theperiod_list.append(row)

    return jsonify(theperiod_list)

if __name__ == '__main__':
    app.run(debug=True)
