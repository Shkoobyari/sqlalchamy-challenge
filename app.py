import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct, and_
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd
import statistics

# Set up DB
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# ***** FLASK APP *****
app = Flask(__name__)

@app.route("/")
def index():
    return (
        f"Available Routes:<br />"
        f"/api/v1.0/precipitation<br />"
        f"/api/v1.0/stations<br />"
        f"/api/v1.0/tobs<br />"
        f"/api/v1.0/start <br />"
        f"/api/v1.0/start/end <br />"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    print(latest_date)
    # latest_date is 2017-08-23
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_twelve_months = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).all()
    session.close()

    all_prcp = []
    for d, temp in last_twelve_months:
        prcp_dct = {}
        prcp_dct['date'] = d
        prcp_dct['temperature'] = temp
        all_prcp.append(prcp_dct)        

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    measurement_station_data = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()

    print(measurement_station_data)
    return jsonify(measurement_station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    most_active =(session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station)).all()
    most_active_station = most_active[6]

    station_id = most_active_station[0]
    most_recent_date = session.query(Measurement.date).\
        filter(Measurement.station == station_id).\
        order_by(Measurement.date.desc()).first()
    # most recent date is 2017-08-18
    query_date = dt.date(2017, 8, 18) - dt.timedelta(days=365)
    data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_date).order_by(Measurement.date.desc()).all()
    session.close()
    return jsonify(data)

@app.route("/api/v1.0/<start>")
def get_temp_from_start_date(start):
    session = Session(engine)

    query_data = session.query(Measurement.tobs).\
        filter(Measurement.date >= start).all()
    session.close()
    result_to_list_float = [i[0] for i in query_data]
    list_float_to_list_int = [int(i) for i in result_to_list_float]
    # print(list_float_to_list_int)
    df = pd.DataFrame({})
    df['temp'] = list_float_to_list_int
    
    # get avg, max, min
    tavg = df['temp'].mean()
    tmin = df['temp'].min()
    tmax = df['temp'].max()
    # print('AVG:', tavg)

    # return jsonify(query_data)
    return jsonify({
        'TAVG': tavg,
        'TMIN': tmin,
        'TMAX': tmax
    })

@app.route("/api/v1.0/<start>/<end>")
def get_temp_from_end_date(start, end):
    session = Session(engine)
    print(start, end)

    query_data = session.query(Measurement.tobs). \
        filter(Measurement.date.between(start, end)).all()
        # filter(and_(Measurement.date >= start, Measurement.date <= end)).all()
    session.close()
    result_to_list_float = [i[0] for i in query_data]
    list_float_to_list_int = [int(i) for i in result_to_list_float]
    df = pd.DataFrame({})
    df['temp'] = list_float_to_list_int

    # get avg, max, min
    tavg = df['temp'].mean()
    tmin = df['temp'].min()
    tmax = df['temp'].max()
    return jsonify({
        'TAVG': tavg,
        'TMIN': tmin,
        'TMAX': tmax
    })

if __name__ == "__main__":
    app.run(debug=True)