#import dependencies
import datetime as dt
import numpy as np
import pandas as pd
#import sqlalchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#import flask
from flask import Flask, jsonify

#set up database
engine = create_engine("sqlite:///hawaii.sqlite")
#reflect DB into a model and reflect tables
Base=automap_base()
Base.prepare(engine, reflect=True)
#save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
#create session from Pythont to DB
session = Session(engine)

#set up flask
app = Flask(__name__)
@app.route('/')
def welcome():
    return ('''
    Welcome to the Climate Analysis API</br>
    Available Routes:</br>
    /api/v1.0/precipitation</br>
    /api/v1.0/stations</br>
    /api/v1.0/tobs</br>
    /api/v1.0/temp/start/end</br>
    ''')

@app.route('/api/v1.0/precipitation')
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    precip={date:prcp for date, prcp in precipitation}
    session.close()
    return jsonify(precip)

@app.route('/api/v1.0/stations')
def stations():
    stations=session.query(Station.station).all()
    stations = list(np.ravel(stations))
    session.close()
    return jsonify(stations=stations)

@app.route('/api/v1.0/tobs')
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    session.close()
    return jsonify(temps=temps)

@app.route('/api/v1.0/temp/<start>')
@app.route('/api/v1.0/temp/<start>/<end>')
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results = session.query(*sel).filter(Measurement.date <= start).all()
        temps = list(np.ravel(results))
        session.close()
        return jsonify(temps)

    results = session.query(*sel).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    session.close()
    return jsonify(temps=temps)
        