# Run 'pip install pandas datetime alpha_vantage pygal scikit-learn'
import pandas as pd
from datetime import datetime
from alpha_vantage.timeseries import TimeSeries
import pygal
from sklearn.preprocessing import MinMaxScaler
from flask import Flask, render_template, request, url_for, flash, redirect, abort
import sys
import os
os.environ["PYTHONUNBUFFERED"] = "0"
app = Flask(__name__)
app.config["DEBUG"]=True
app.config['SECRET_KEY'] = 'your secret key'

################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
################################################################################################################################################



def filter_by_date_range(data, start_date, end_date):
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    data = data.sort_index()
    filtered_data = data.loc[start_date:end_date]
    return filtered_data



################################################################################################################################################
################################################################################################################################################
################################################################################################################################################
    

def get_data(stock_symbol,APIkey,series):
    #Creating Timeseries object
    ts = TimeSeries(key = APIkey ,output_format='pandas')

    #getting the data on the stock based on chosen series
    if (series == 1):
        data, meta = ts.get_intraday(symbol = stock_symbol, interval = '15min',outputsize='full')
    elif (series == 2):
        data, meta = ts.get_daily(symbol = stock_symbol,outputsize='full')
    elif (series == 3):
        data, meta = ts.get_weekly(symbol = stock_symbol)
    elif (series ==4):
        data, meta = ts.get_monthly(symbol = stock_symbol)
    else:
        data, meta = None

    #return the raw data and metadata
    return data, meta




################################################################################################################################################
################################################################################################################################################
################################################################################################################################################


def plot_data(df, chart_type, time_series, symbol,start_date,end_date):
    #Get rid of the numbers on the column headers
    rename_dict = {'1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close'}
    df.rename(columns=rename_dict, inplace=True)

    # Create a line or bar chart based on user input
    if chart_type == "line":
        chart = pygal.Line(x_label_rotation=20, x_value_formatter=lambda dt: dt.strftime('%d-%m-%Y %H:%M:%S'))
    elif chart_type == "bar":
        chart = pygal.Bar(x_label_rotation=45)  # Rotate x-labels by 45 degrees
    else:
        return

    # Add title and labels
    chart.title = 'Stock Data for '+symbol+": "+start_date+" to "+end_date
    chart.x_title = 'Date'
    chart.y_title = 'Value'

    # Change the date format to include time if time_series is 1 (intraday)
    if time_series == 1:
        chart.x_labels = map(lambda d: d.strftime('%Y-%m-%d %H:%M:%S'), df.index)
    else:
        chart.x_labels = map(lambda d: d.strftime('%Y-%m-%d'), df.index)

    # Convert each column to numeric and drop non-numeric rows
    for col in ['Open', 'High', 'Low', 'Close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=[col])
        # Add data to chart
        chart.add(col, df[col].tolist())
    
    # Return chart object
    return chart


################################################################################################################################################
################################################################################################################################################
################################################################################################################################################



@app.route('/', methods = ('GET', 'POST'))
def index():
    
    #initialize variables
    chart_picture = None
    error = None
    chart = None

    #import stock symbols and make into a list
    symbols_csv = pd.read_csv('stocks.csv')
    symbols_list = symbols_csv['Symbol'].tolist()

    #If method is POST (when the submit button is hit)
    if request.method == "POST":

        #Getting the user inputs from the POST
        symbol = request.form['symbol']
        chart_type = request.form['chartType']
        time_series = int(request.form["timeSeries"])
        end_date = request.form["endDate"]
        start_date =  request.form["startDate"]

        #Querying the API and formatting the data
        data, meta = get_data(symbol, '67ZV81HC5LKYSLBY', time_series )
        filtered_data = filter_by_date_range(data, start_date, end_date)

        #generating an error message if there is too much data making the chart unreadable
        if ((len(filtered_data)) > 64 ):
            error = True
        #creating the chart and chart picture
        else:
            chart  = plot_data(filtered_data, chart_type, time_series, symbol,start_date,end_date)
            chart_picture = chart.render_data_uri()

    #rendering the page    
    return render_template('index.html',chart_picture=chart_picture, error = error,symbols_list = symbols_list)




#running the app on port 5001 
app.run(host="0.0.0.0")