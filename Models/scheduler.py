import os
import schedule
import time
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.telegram_notifier import TelegramNotifier
from utils.error_history import get_tracker


def job():
    os.system("./arima_forecaster.py 1")
    print('Done with ARIMA, running smoothing models')
    os.system("./smoothing_forecaster.py 1")
    print('Done with smoothing models, running RNN models')
    os.system("./rnn_forecaster.py 1")
    print('Done')
    return None


def evaluate_forecast_and_notify(actual_value, predicted_value, model_name, forecast_date=None):
    """
    Calculate forecast error and send notification if error exceeds threshold
    
    Args:
        actual_value (float): Actual observed load value
        predicted_value (float): Model's predicted load value
        model_name (str): Name of the forecasting model
        forecast_date (str, optional): Date of the forecast in YYYY-MM-DD format
    
    Returns:
        float: Error percentage
    """
    # Calculate absolute percentage error
    if actual_value == 0:  # Prevent division by zero
        error_pct = float('inf') if predicted_value != 0 else 0
    else:
        error_pct = abs((actual_value - predicted_value) / actual_value) * 100
    
    print(f"{model_name} forecast error: {error_pct:.2f}%")
    
    # Use current date if not provided
    if forecast_date is None:
        forecast_date = datetime.now().strftime('%Y-%m-%d')
    
    # Initialize stats dictionary with default values
    stats = {
        'avg': None,
        'min': None,
        'max': None,
        'count': 0
    }
    
    # Save error to history
    try:
        # Get error history tracker
        tracker = get_tracker()
        
        # Calculate additional metrics
        additional_metrics = {
            'actual': float(actual_value),
            'predicted': float(predicted_value),
            'abs_error': abs(float(actual_value) - float(predicted_value))
        }
        
        # Add error to history
        tracker.add_error(
            model_name=model_name,
            error_value=error_pct,
            forecast_date=forecast_date,
            additional_metrics=additional_metrics
        )
        
        # Get error statistics for context
        stats = tracker.get_error_statistics(model_name, days=7)
        if stats['avg'] is not None:
            print(f"{model_name} 7-day avg error: {stats['avg']:.2f}% (min: {stats['min']:.2f}%, max: {stats['max']:.2f}%)")
        
    except Exception as e:
        print(f"Failed to save error history: {str(e)}")
    
    # Check if error exceeds threshold (5%)
    if error_pct > 5.0:
        try:
            # Initialize notifier
            notifier = TelegramNotifier()
            
            # Prepare message based on error severity
            if error_pct > 10.0:
                level = "critical"
                message = f"Critical forecast deviation detected. Immediate review required."
            else:
                level = "error"
                message = f"Forecast error exceeds acceptable threshold. Manual review recommended."
            
            # Include trend information in the message if available
            if stats['avg'] is not None:
                if error_pct > stats['avg'] * 1.5:
                    message += f"\n\nThis error is {(error_pct/stats['avg']):.1f}x higher than the 7-day average ({stats['avg']:.2f}%)."
            
            # Send the notification
            notifier.send_alert(
                message=message,
                error_level=level,
                model_name=model_name,
                error_value=error_pct
            )
            
            print(f"Alert notification sent for {model_name}")
            
        except Exception as e:
            print(f"Failed to send notification: {str(e)}")
    
    return error_pct
schedule.every().day.at("00:15").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)  # wait one minute
