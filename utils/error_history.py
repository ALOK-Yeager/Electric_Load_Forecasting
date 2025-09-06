"""
Error History Tracking Module

This module provides functionality to track and maintain a history of
forecast errors for various models in the Electric Load Forecasting system.
"""

import os
import json
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

class ErrorHistoryTracker:
    """
    Track and maintain a history of forecast errors.
    
    This class handles saving error metrics to a JSON file,
    limiting the history to a specified number of days,
    and providing access to historical error data.
    
    Attributes:
        history_file (Path): Path to the JSON file storing error history
        max_days (int): Maximum number of days to keep in history
        history (dict): Dictionary containing error history data
    """
    
    def __init__(self, history_file=None, max_days=30):
        """
        Initialize the ErrorHistoryTracker.
        
        Args:
            history_file (str, optional): Path to history JSON file.
                                          Defaults to 'data/error_history.json'.
            max_days (int, optional): Maximum days of history to maintain. Defaults to 30.
        """
        # Set default history file if not provided
        if history_file is None:
            data_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'data'
            data_dir.mkdir(exist_ok=True)  # Create data directory if it doesn't exist
            self.history_file = data_dir / 'error_history.json'
        else:
            self.history_file = Path(history_file)
        
        self.max_days = max_days
        self.history = self._load_history()
    
    def _load_history(self):
        """
        Load error history from JSON file.
        
        Returns:
            dict: Dictionary containing error history data
        """
        if not self.history_file.exists():
            logger.info(f"No history file found at {self.history_file}. Creating a new one.")
            return {}
        
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            logger.info(f"Loaded error history from {self.history_file}")
            return history
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {self.history_file}. Creating a new history.")
            return {}
        except Exception as e:
            logger.error(f"Error loading history file: {str(e)}. Creating a new history.")
            return {}
    
    def _save_history(self):
        """Save the current history to the JSON file."""
        try:
            # Create directory if it doesn't exist
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.info(f"Saved error history to {self.history_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving history file: {str(e)}")
            return False
    
    def add_error(self, model_name, error_value, forecast_date=None, additional_metrics=None):
        """
        Add a new error entry to the history.
        
        Args:
            model_name (str): Name of the forecasting model
            error_value (float): Error percentage or value
            forecast_date (str, optional): Date of the forecast. Defaults to today.
            additional_metrics (dict, optional): Additional metrics to store. Defaults to None.
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Use provided date or today's date
        if forecast_date is None:
            forecast_date = datetime.now().strftime('%Y-%m-%d')
        
        # Initialize the model in history if not exists
        if model_name not in self.history:
            self.history[model_name] = {}
        
        # Create the error entry
        entry = {
            'error': float(error_value),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add additional metrics if provided
        if additional_metrics and isinstance(additional_metrics, dict):
            entry.update(additional_metrics)
        
        # Add to history
        self.history[model_name][forecast_date] = entry
        
        # Prune old entries
        self._prune_old_entries()
        
        # Save the updated history
        return self._save_history()
    
    def _prune_old_entries(self):
        """Remove entries older than max_days from the history."""
        cutoff_date = (datetime.now() - timedelta(days=self.max_days)).strftime('%Y-%m-%d')
        
        for model_name in self.history:
            # Create a new dict with only recent entries
            recent_entries = {
                date: entry 
                for date, entry in self.history[model_name].items()
                if date >= cutoff_date
            }
            self.history[model_name] = recent_entries
    
    def get_model_history(self, model_name):
        """
        Get error history for a specific model.
        
        Args:
            model_name (str): Name of the forecasting model
        
        Returns:
            dict: Dictionary of error entries for the model or empty dict if model not found
        """
        return self.history.get(model_name, {})
    
    def get_recent_errors(self, model_name, days=7):
        """
        Get recent error entries for a model.
        
        Args:
            model_name (str): Name of the forecasting model
            days (int, optional): Number of days to look back. Defaults to 7.
        
        Returns:
            list: List of (date, error_value) tuples, sorted by date
        """
        model_history = self.get_model_history(model_name)
        
        if not model_history:
            return []
        
        # Calculate the cutoff date
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get recent entries
        recent_entries = [
            (date, entry['error'])
            for date, entry in model_history.items()
            if date >= cutoff_date
        ]
        
        # Sort by date
        return sorted(recent_entries, key=lambda x: x[0])
    
    def get_error_statistics(self, model_name, days=30):
        """
        Calculate error statistics for a model over a period of days.
        
        Args:
            model_name (str): Name of the forecasting model
            days (int, optional): Number of days to include. Defaults to 30.
        
        Returns:
            dict: Dictionary with error statistics
        """
        recent_errors = [error for _, error in self.get_recent_errors(model_name, days)]
        
        if not recent_errors:
            return {
                'count': 0,
                'min': None,
                'max': None,
                'avg': None,
                'above_threshold_count': 0  # Errors above 5%
            }
        
        return {
            'count': len(recent_errors),
            'min': min(recent_errors),
            'max': max(recent_errors),
            'avg': sum(recent_errors) / len(recent_errors),
            'above_threshold_count': sum(1 for e in recent_errors if e > 5.0)
        }


# Create a singleton instance
_tracker = None

def get_tracker(history_file=None, max_days=30):
    """
    Get or create the ErrorHistoryTracker singleton.
    
    Args:
        history_file (str, optional): Path to history file. Defaults to None.
        max_days (int, optional): Maximum days of history. Defaults to 30.
    
    Returns:
        ErrorHistoryTracker: The error history tracker instance
    """
    global _tracker
    
    if _tracker is None:
        _tracker = ErrorHistoryTracker(history_file, max_days)
    
    return _tracker