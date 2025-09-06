# Error History Tracking

The Electric Load Forecasting system includes an automated error history tracking system that:

1. Records forecast errors for all models
2. Maintains a rolling 30-day history
3. Provides statistical analysis
4. Enhances alert notifications with trend data

## Using Error History Data

### Basic Usage

The error history tracking is integrated with the forecasting system. When `evaluate_forecast_and_notify()` is called, errors are automatically saved.

```python
from utils.error_history import get_tracker

# Get the tracker
tracker = get_tracker()

# Add an error manually (normally handled by evaluate_forecast_and_notify)
tracker.add_error(
    model_name="ARIMA",
    error_value=4.25,
    forecast_date="2023-09-07",
    additional_metrics={
        'actual': 450,
        'predicted': 430,
        'abs_error': 20
    }
)

# Get error statistics
stats = tracker.get_error_statistics("ARIMA", days=7)
print(f"Average error: {stats['avg']:.2f}%")
```

### Analyzing Error History

Use the `analyze_errors.py` script to work with error history data:

```bash
# Generate a summary report
python analyze_errors.py --report

# Generate a plot of errors over time
python analyze_errors.py --plot

# Export error data to CSV
python analyze_errors.py --export --format csv

# Filter by model and time period
python analyze_errors.py --model ARIMA --days 14 --report --plot
```

## How It Works

1. **Storage**: Error metrics are stored in `data/error_history.json`
2. **Pruning**: Old entries (>30 days) are automatically removed
3. **Data Format**: JSON structure by model name and date
4. **Performance**: Optimized for quick read/write operations

## Data Structure

The error history is stored in this format:

```json
{
  "ARIMA": {
    "2023-09-07": {
      "error": 4.25,
      "timestamp": "2023-09-07T08:30:45.123456",
      "actual": 450,
      "predicted": 430,
      "abs_error": 20
    },
    "2023-09-06": {
      "error": 3.75,
      "timestamp": "2023-09-06T08:30:12.654321",
      "actual": 440,
      "predicted": 425,
      "abs_error": 15
    }
  },
  "LSTM": {
    "2023-09-07": {
      "error": 3.25,
      "timestamp": "2023-09-07T08:30:46.123456",
      "actual": 450,
      "predicted": 435,
      "abs_error": 15
    }
  }
}
```

## Benefits

1. **Enhanced Alerts**: Notification messages now include context about whether an error is trending higher than average
2. **Historical Analysis**: Track model performance over time
3. **Model Comparison**: Compare different forecasting approaches
4. **Trend Detection**: Identify declining model performance early