#!/home/eee/ug/15084015/miniconda3/envs/btp/bin/python
"""
The script is to run half an hour after midnight. Scrap last day's data and update monthsdata.csv
"""
import os
import logging
from math import sqrt
from subprocess import call
from datetime import datetime, timedelta
import csv
import requests
import numpy as np
import pandas as pd
import statsmodels.api as sm
from bs4 import BeautifulSoup
from statsmodels.tsa.arima_model import ARIMAResults
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.telegram_notifier import TelegramNotifier
from Models.scheduler import evaluate_forecast_and_notify  # Import the function we created
from utils.compat import (
    bs_find_all, bs_find_children, pd_read_csv_compat,
    load_arima_model, save_arima_model, get_model_prediction
)


def get_load_data(date):
    url = "http://www.delhisldc.org/Loaddata.aspx?mode="
    logger.info("Scraping " + date)
    resp = requests.get(url + date)  # send a get request to the url, get response
    soup = BeautifulSoup(resp.text, "lxml")  # Yummy HTML soup
    table = soup.find(
        "table", {"id": "ContentPlaceHolder3_DGGridAv"}
    )  # get the table from html
    
    # Check if table was found before accessing
    if table is None:
        logger.error(f"Could not find load data table for {date}")
        return
        
    # Use our compatibility function for BeautifulSoup
    trs = bs_find_all(table, "tr")  # extract all rows of the table
    
    if not trs:
        logger.error(f"No rows found in table for {date}")
        return
        
    if len(trs[1:]) == 288:  # no need to create csv file, if there's no data
        with open(
            "monthdata.csv", "a"
        ) as f:  #'a' makes sure the values are appended at the end of the already existing file
            writer = csv.writer(f)
            for tr in trs[1:]:
                # Use our compatibility function for finding children
                font_elements = bs_find_children(tr, "font")
                if len(font_elements) >= 2:
                    time, delhi = font_elements[:2]
                    writer.writerow([date + " " + time.text, delhi.text])
                else:
                    logger.warning(f"Missing data in row for {date}")
    
    if len(trs[1:]) != 288:
        logger.info("Some of the load values are missing..")
    else:
        logger.info("Done")


def get_data():
    # Use our compatibility function for pandas read_csv
    return pd_read_csv_compat(
        "monthdata.csv",
        header=None,
        index_col=["datetime"],
        names=["datetime", "load"],
        parse_dates=["datetime"],
        infer_datetime_format=True,
    )


# to store the log in a file called 'arima_log.txt'
logging.basicConfig(
    filename="aws_arima_log.txt",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)
logger = logging.getLogger()
console = logging.StreamHandler()
logger.addHandler(console)

"""Check if monthdata.csv exists, if no then create one, if yes then update it with yesterday's data and clip it so that it contains only last 30 days of data,
as the model is to be trained on last 30 days of data."""
if os.path.exists("monthdata.csv"):
    data = get_data()
    # import pdb; pdb.set_trace()
    if (datetime.today() - timedelta(1)).date().strftime('%Y-%m-%d') != str(data.index.date[-1]):  # yesterdays data not present, scrap it
        # only need to scrap for yesterday's data and append it to already existing file
        yesterday = datetime.today() - timedelta(1)
        yesterday = yesterday.strftime("%d/%m/%Y")
        get_load_data(yesterday)
        # re read updated monthdata.csv and clip data in monthdata.csv to last 30 days only
        data = get_data()
        day_to_clip_from = datetime.today() - timedelta(30)
        logger.info("Clipping data from " + day_to_clip_from.strftime("%d/%m/%Y"))
        data = data[day_to_clip_from.strftime("%d/%m/%Y"):]
        data.to_csv(
            "monthdata.csv", header=False
        )  # IMP: don't add any header to the monthdata.csv
    else:
        logger.info('Yesterday"s load already scrapped!')
else:  # scrap for last 30 days, prepare monthdata.csv
    for i in range(31, 0, -1):
        yesterday = datetime.today() - timedelta(i)
        yesterday = yesterday.strftime("%d/%m/%Y")
        get_load_data(yesterday)
    data = get_data()

# exit()
logger.info(data.shape)
data = data.asfreq(freq="30Min", method="bfill")  # sample the data in hourly manner

# initialize the model
model = sm.tsa.statespace.SARIMAX(
    data,
    order=(3, 1, 1),
    seasonal_order=(3, 0, 0, 24),
    enforce_stationarity=False,
    enforce_invertibility=False,
)

# fit the model with the data
logger.info("Starting model fitting...")
model = model.fit()

logger.info("Model fitting done!!")
logger.info(model.summary().tables[1])
logger.info(model.summary())

# save the model using our compatibility function
save_arima_model(model, "ARIMA_month_model.pkl")

# generate the predictions
todays_date = datetime.today().strftime("%d/%m/%Y")
tommorows_date = (datetime.today() + timedelta(1)).strftime("%d/%m/%Y")

# Use our compatibility function to get predictions
try:
    data_shape = data.shape[0] if hasattr(data, 'shape') else 0
    
    # Get prediction using compatibility function
    pred = get_model_prediction(
        model,
        start=data_shape,  # start from end of data
        end=data_shape+48,  # predict next 48 values (half hourly, for 24 hours)
        dynamic=False
    )
except Exception as e:
    logger.error(f"Error generating prediction: {str(e)}")
    pred = None
# Make sure the predictions directory exists
os.makedirs("predictions/ARIMA", exist_ok=True)

date = datetime.today().strftime(format="%d-%m-%Y")

# Handle prediction results safely
if pred is not None:
    try:
        # Extract predictions, handling different formats from different statsmodels versions
        if hasattr(pred, 'predicted_mean'):
            predictions = pred.predicted_mean
        elif isinstance(pred, (list, np.ndarray)):
            predictions = pd.Series(pred, name="load")
        else:
            predictions = pd.Series([p for p in pred], name="load")
            
        # Set datetime index if not already set
        if not isinstance(predictions.index, pd.DatetimeIndex):
            start_time = datetime.today().replace(hour=0, minute=0, second=0)
            time_range = pd.date_range(start=start_time, periods=len(predictions), freq='30Min')
            predictions.index = time_range
            
        # Resample to 5-minute intervals
        predictions = predictions.asfreq(freq="5Min", method="bfill")
        
        # Save to CSV
        predictions.to_csv(
            f"predictions/ARIMA/{date}.csv", index_label="datetime", header=["load"]
        )
        logger.info(f"Successfully saved predictions to predictions/ARIMA/{date}.csv")
    except Exception as e:
        logger.error(f"Error processing predictions: {str(e)}")
else:
    logger.error("Failed to generate predictions")


def generate_arima_forecast(data, forecast_date=None):
    """
    Generate an ARIMA forecast for a specific date
    
    Args:
        data (DataFrame): Historical load data
        forecast_date (str, optional): Date to forecast for. Defaults to tomorrow.
    
    Returns:
        float: Forecast average load value for the date
    """
    if forecast_date is None:
        forecast_date = (datetime.today() + timedelta(1)).strftime('%Y-%m-%d')
    
    logger.info(f"Generating ARIMA forecast for {forecast_date}")
    
    try:
        # Load the model if it exists, otherwise use the current one
        forecast_model = None
        
        if os.path.exists("ARIMA_month_model.pkl"):
            # Use our compatibility function to load the model
            forecast_model = load_arima_model("ARIMA_month_model.pkl")
            if forecast_model is None:
                logger.warning("Could not load saved model, using current model")
                forecast_model = model
        else:
            forecast_model = model
        
        # Generate prediction for the date
        forecast_start = pd.to_datetime(forecast_date)
        forecast_end = forecast_start + timedelta(days=1) - timedelta(minutes=30)
        
        # Convert to periods for prediction
        data_size = len(data) if hasattr(data, '__len__') else 0
        start_pos = data_size
        end_pos = start_pos + 48  # 48 half-hour periods in a day
        
        # Use our compatibility function to get predictions
        pred = get_model_prediction(
            forecast_model,
            start=start_pos,
            end=end_pos,
            dynamic=False
        )
        
        if pred is None:
            logger.error("Failed to generate prediction")
            return None
            
        # Get the forecast values
        if hasattr(pred, 'predicted_mean'):
            forecast_values = pred.predicted_mean
        elif isinstance(pred, (list, np.ndarray)):
            forecast_values = pd.Series(pred)
        else:
            forecast_values = pd.Series([p for p in pred])
        
        # Calculate average for the day
        forecast_avg = forecast_values.mean()
        
        logger.info(f"ARIMA forecast for {forecast_date}: {forecast_avg:.2f}")
        return forecast_avg
        
    except Exception as e:
        logger.error(f"Error generating ARIMA forecast: {e}")
        return None


def get_actual_value_if_available(forecast_date):
    """
    Retrieve actual load value for a date if available
    
    Args:
        forecast_date (str): Date to get actual value for in YYYY-MM-DD format
        
    Returns:
        float: Actual average load value or None if not available
    """
    try:
        # Convert date format if needed
        date_obj = pd.to_datetime(forecast_date)
        formatted_date = date_obj.strftime("%d/%m/%Y")
        
        # Check if we have data for this date
        data_path = os.path.join("SLDC_Data", date_obj.strftime("%Y"), date_obj.strftime("%m"), 
                                f"{date_obj.strftime('%d-%m-%Y')}.csv")
        
        if os.path.exists(data_path):
            # Load the actual data
            actual_data = pd.read_csv(data_path)
            
            # Calculate average load for the day
            if 'value' in actual_data.columns:
                actual_avg = actual_data['value'].mean()
                logger.info(f"Actual load for {forecast_date}: {actual_avg:.2f}")
                return actual_avg
        
        # If we don't have data in the expected format, try scraping
        yesterday = (datetime.today() - timedelta(1)).strftime("%d/%m/%Y")
        if formatted_date == yesterday:
            try:
                # Attempt to load from monthdata.csv which should have yesterday's data
                data = get_data()
                
                # Handle TextFileReader and DataFrame differently
                if hasattr(data, 'get_chunk'):
                    # It's a TextFileReader, convert to DataFrame
                    data = pd.concat([chunk for chunk in data])
                
                if yesterday in data.index:
                    yesterday_data = data.loc[yesterday]
                    actual_avg = yesterday_data['load'].mean()
                    logger.info(f"Actual load for {forecast_date} from monthdata: {actual_avg:.2f}")
                    return actual_avg
            except Exception as e:
                logger.warning(f"Could not get yesterday's data from monthdata: {e}")
        
        logger.info(f"No actual load data available for {forecast_date}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting actual load value: {e}")
        return None


def forecast_and_evaluate(data, forecast_date=None):
    """
    Generate ARIMA forecast and evaluate against actual if available
    
    Args:
        data (DataFrame): Historical load data
        forecast_date (str, optional): Date for which to generate forecast
    
    Returns:
        dict: Forecast results including prediction and error metrics
    """
    if forecast_date is None:
        forecast_date = datetime.today().strftime('%Y-%m-%d')
    
    # Generate forecast
    forecast_value = generate_arima_forecast(data, forecast_date)
    
    # Check if we have actual data for this date to compare
    actual_value = get_actual_value_if_available(forecast_date)
    
    result = {
        'date': forecast_date,
        'forecast': forecast_value,
        'model': 'ARIMA'
    }
    
    # If actual data is available, calculate error and notify if needed
    if actual_value is not None and forecast_value is not None:
        error_pct = evaluate_forecast_and_notify(actual_value, forecast_value, 'ARIMA', forecast_date)
        result['actual'] = actual_value
        result['error_pct'] = error_pct
    
    return result


# Check if we should evaluate yesterday's forecast
yesterday = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')
result = forecast_and_evaluate(data, yesterday)

if len(sys.argv) > 1 and sys.argv[1] == '1':
    # now, send the file to the AWS server using scp
    cmd = (
        "scp -i /home/eee/ug/15084015/.ssh/btp.pem predictions/ARIMA/%s.csv ubuntu@13.126.97.91:/var/www/html/btech_project/server/predictions/ARIMA/"
        % (date)
    )
    logger.info(call(cmd.split(" ")))
    
print("ARIMA prediction done")
