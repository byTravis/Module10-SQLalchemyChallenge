# Import the dependencies.

from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Functions
#################################################

# Calculates date range for queries
def date_range(days):
   # Find most recent date, format that to datetime format
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = format_date(recent_date[0])

    # Find the date range of 1 year by subtracting 1 year.
    date_start = recent_date - dt.timedelta(days=days)
    return(date_start)



# Formats a string into datetime format
def format_date(date):    
    formatted_date = dt.datetime.strptime(date, "%Y-%m-%d").date()
    return(formatted_date)



#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>" 
        f"/api/v1.0/ &lt;start&gt;/&lt;end&gt;<br/>"
    )




@app.route("/api/v1.0/precipitation")
def precipitation():
    """List precipitation for the last 12 months of data."""

    # Queries function to return the staring date.  Passes the number of days for datetime math.
    date_start = date_range(365)

    # Query to find the precipitation within that date range, then close the session.
    prcp_12mos = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_start).order_by(Measurement.date).all()
    session.close()

    # Convert the query into a list so it can be jsonified
    prcp_12mos_list = [{"date": p.date, "prcp": p.prcp} for p in prcp_12mos]

    # Display the JSON results
    return jsonify(prcp_12mos_list)




@app.route("/api/v1.0/stations")
def stations():
    """List all stations from data."""

    # Query the database to return a list of stations.  Then close the query.
    stations = session.query(Station.station)
    session.close()

    # Turn the query into a list so it can be jsonified
    station_list = [s.station for s in stations]

    # Display the JSON results
    return jsonify(station_list)




@app.route("/api/v1.0/tobs")
def tobs():
    """Dates and temperature observations of the most-active station for the previous year of data."""

    # Find the most active station with the most number of observations.
    active_stations = session.query(Measurement.station, func.count()).group_by(Measurement.station).order_by(func.count().desc()).all() 
    active_station_most = active_stations[0][0]

    # Queries function to return the staring date.  Passes the number of days for datetime math.
    date_start = date_range(365)

    # Query the database, only returning results from the most active station.  Then close the session.
    active_station_summery = session.query(Measurement.date, Measurement.tobs).filter_by(station = active_station_most).filter(Measurement.date >= date_start).order_by(Measurement.date).all()
    session.close()


    # Turn the query into a list so it can be jsonified
    active_station_summery_list = [{"date": a.date, "tobs": a.tobs} for a in active_station_summery]
    
    # Display the JSON results
    return jsonify(active_station_summery_list)




@app.route("/api/v1.0/<start>")
def start_tobs(start):
    """List minimum, average, and maximum teperature from start date and above."""
    # Parses the start date and checks the format.  If correct, it formats the start date in datetime format.  If it fails, it gives an error with instructions.
    try:
        query_start = format_date(start)
    except ValueError:
        return "Error: Invalid date format. Please use YYYY-MM-DD format when entering a query."
    
    # Queries database, returning only records from start date and greater.  Returns Min, Avg, and Max, then closes session
    start_tobs_query = session.query(func.min(Measurement.tobs), func.round(func.avg(Measurement.tobs), 1), func.max(Measurement.tobs)).filter(Measurement.date >= query_start).all()
    session.close()

    # Turn the query into a list so it can be jsonified
    start_tobs_list = [{"tmin": q[0], "tavg": q[1], "tmax": q[2]} for q in start_tobs_query]

    # Display the JSON results
    return jsonify(start_tobs_list)




@app.route("/api/v1.0/<start>/<end>")
def start_end_tobs(start, end):
    """List minimum, average, and maximum teperature between start date and end date."""
    # Parses the start and end dates and checks the format.  If correct, it formats the start and end dates in datetime format.  If it fails, it gives an error with instructions.
    try:
        query_start = format_date(start)
        query_end = format_date(end)
    except ValueError:
        return "Error: Invalid date format. Please use YYYY-MM-DD format when entering a query."

    # Queries database, returning only records between start and end date.  Returns Min, Avg, and Max, then closes session
    start_end_tobs_query = session.query(func.min(Measurement.tobs), func.round(func.avg(Measurement.tobs), 1), func.max(Measurement.tobs)).filter(Measurement.date >= query_start).filter(Measurement.date <= query_end).all()
    session.close()

    # Turn the query into a list so it can be jsonified
    start_end_tobs_list = [{"tmin": q[0], "tavg": q[1], "tmax": q[2]} for q in start_end_tobs_query]

    # Display the JSON results
    return jsonify(start_end_tobs_list)



if __name__ == "__main__":
    app.run(debug=True)