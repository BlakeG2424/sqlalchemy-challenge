# Import all dependencies:
#################################################

import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
import numpy as np
from flask import Flask, jsonify, render_template

# Create connection to Hawaii.sqlite file
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# # Save references to the measurement and station tables in the database
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session
session = Session(engine)

app = Flask(__name__)


@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start><br>"
        f"/api/v1.0/temp/<start>/<end>"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    session.close()

    print(precipitation)

    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    session.close()

    print(results)
    print()
    print(np.ravel(results))

    stations = list(np.ravel(results))
    print(stations)

    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    lateststr = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year - 1, latestdate.month, latestdate.day)
    sel = [Measurement.date, Measurement.tobs]
    result = session.query(*sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobs_list = []
    for date, tobs in result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/temp/<start><br>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # start = dt.datetime.strptime(start, "%m/%d/%Y")
        # # calculate TMIN, TAVG, TMAX for dates greater than start
        # results = session.query(*sel).\
        #     filter(Measurement.date >= start).all()
        # # Unravel results into a 1D array and convert to a list
        # temps = list(np.ravel(results))
        # return jsonify(temps)

        start = dt.datetime.strptime(start, "%m%d%Y")
        return_list = []

        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        
        for date, min, avg, max in results:
         ct_dict = {}
        ct_dict["Date"] = date
        ct_dict["TMIN"] = min
        ct_dict["TAVG"] = avg
        ct_dict["TMAX"] = max
        return_list.append(ct_dict)

        session.close()

        #temps = return_list(np.ravel(results))
        return jsonify(return_list)

    # calculate TMIN, TAVG, TMAX with start and stop
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]


    return_list = []

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    

    for date, min, avg, max in results:
        ct_dict = {}
        ct_dict["Date"] = date
        ct_dict["TMIN"] = min
        ct_dict["TAVG"] = avg
        ct_dict["TMAX"] = max
        return_list.append(ct_dict)

    session.close()

    # Unravel results into a 1D array and convert to a list
    #temps = return_list(np.ravel(results))
    return jsonify(return_list) 
  
if __name__ == '__main__':
    app.run(debug=True)
