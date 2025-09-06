import os
import json
from pathlib import Path
from datetime import datetime, timedelta

def get_formatted_error_history(days=30):
    """
    Load and format error history data for dashboard display.
    
    Args:
        days (int): Number of days of history to include
        
    Returns:
        dict: Formatted error history or empty dict if file doesn't exist
    """
    # Define path to error history JSON file
    base_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    history_file = base_dir / 'data' / 'error_history.json'
    
    # Initialize empty result structure
    result = {
        'has_data': False,
        'models': {},
        'dates': [],
        'overall_stats': {
            'avg_error': 0,
            'threshold_violations': 0,
            'total_forecasts': 0
        }
    }
    
    # Check if history file exists
    if not history_file.exists():
        return result
    
    try:
        # Load JSON data
        with open(history_file, 'r') as f:
            history_data = json.load(f)
        
        if not history_data:
            return result
            
        # Calculate date cutoff (for filtering)
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get unique sorted dates across all models
        all_dates = set()
        for model, dates in history_data.items():
            for date in dates:
                if date >= cutoff_date:
                    all_dates.add(date)
        
        # Sort dates chronologically
        sorted_dates = sorted(list(all_dates))
        result['dates'] = sorted_dates
        
        # Format data by model
        total_errors = []
        total_forecasts = 0
        threshold_violations = 0
        
        for model, dates in history_data.items():
            model_data = {
                'name': model,
                'errors': [],
                'avg_error': 0,
                'max_error': 0,
                'min_error': float('inf'),
                'violations': 0
            }
            
            # Filter for recent dates and collect errors
            model_errors = []
            for date in sorted_dates:
                if date in dates:
                    error_value = dates[date]['error']
                    model_errors.append(error_value)
                    total_errors.append(error_value)
                    total_forecasts += 1
                    
                    # Add to result with formatting
                    model_data['errors'].append({
                        'date': date,
                        'value': error_value,
                        'formatted': f"{error_value:.2f}%",
                        'is_violation': error_value > 5.0
                    })
                    
                    # Track threshold violations
                    if error_value > 5.0:
                        model_data['violations'] += 1
                        threshold_violations += 1
                    
                    # Update min/max
                    model_data['max_error'] = max(model_data['max_error'], error_value)
                    model_data['min_error'] = min(model_data['min_error'], error_value)
                else:
                    # Add placeholder for missing dates
                    model_data['errors'].append({
                        'date': date,
                        'value': None,
                        'formatted': "-",
                        'is_violation': False
                    })
            
            # Calculate average if we have data
            if model_errors:
                model_data['avg_error'] = sum(model_errors) / len(model_errors)
                # Format the stats
                model_data['avg_formatted'] = f"{model_data['avg_error']:.2f}%"
                model_data['max_formatted'] = f"{model_data['max_error']:.2f}%"
                model_data['min_formatted'] = f"{model_data['min_error']:.2f}%" if model_data['min_error'] != float('inf') else "-"
                # Add to result
                result['models'][model] = model_data
        
        # Calculate overall stats
        if total_errors:
            result['overall_stats']['avg_error'] = sum(total_errors) / len(total_errors)
            result['overall_stats']['avg_formatted'] = f"{result['overall_stats']['avg_error']:.2f}%"
            result['overall_stats']['threshold_violations'] = threshold_violations
            result['overall_stats']['total_forecasts'] = total_forecasts
            result['overall_stats']['violation_rate'] = (threshold_violations / total_forecasts) * 100 if total_forecasts > 0 else 0
            result['overall_stats']['violation_rate_formatted'] = f"{result['overall_stats']['violation_rate']:.1f}%"
            result['has_data'] = True
            
        return result
        
    except (json.JSONDecodeError, IOError, Exception) as e:
        # Return empty structure if any error occurs
        return result