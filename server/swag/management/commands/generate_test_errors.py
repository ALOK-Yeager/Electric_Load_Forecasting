"""
Management command to generate sample error history for testing the dashboard.
"""
import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

class Command(BaseCommand):
    help = 'Generate sample error history data for testing the dashboard'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Number of days of history to generate')
        parser.add_argument('--models', nargs='+', default=['ARIMA', 'LSTM', 'GRU', 'SMA'], help='Models to include')
        parser.add_argument('--clear', action='store_true', help='Clear existing history before generating')

    def handle(self, *args, **options):
        days = options['days']
        models = options['models']
        clear_existing = options['clear']
        
        # Define path to error history JSON file
        data_dir = project_root / 'data'
        data_dir.mkdir(exist_ok=True)
        history_file = data_dir / 'error_history.json'
        
        # Load existing data or start fresh
        if history_file.exists() and not clear_existing:
            try:
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                self.stdout.write(f"Loaded existing history with {len(history_data)} models")
            except (json.JSONDecodeError, IOError):
                history_data = {}
                self.stdout.write("Could not load existing history, starting fresh")
        else:
            history_data = {}
            if clear_existing:
                self.stdout.write("Clearing existing history data")
        
        # Generate data for each model
        for model in models:
            if model not in history_data:
                history_data[model] = {}
            
            # Generate random error values for each day
            for day in range(days):
                date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
                
                # Only add if doesn't exist yet or we're clearing
                if date not in history_data[model] or clear_existing:
                    # Generate realistic error values with occasional threshold violations
                    if random.random() < 0.8:  # 80% of the time, generate low errors
                        error = random.uniform(1.5, 4.8)  # Under threshold
                    else:
                        error = random.uniform(5.1, 12.0)  # Over threshold
                    
                    # Add some variance by model
                    if model == 'ARIMA':
                        error *= 1.1
                    elif model == 'LSTM':
                        error *= 0.9
                        
                    # Create the entry
                    actual = random.uniform(350, 450)
                    predicted = actual * (1 + (error / 100) * (1 if random.random() > 0.5 else -1))
                    
                    history_data[model][date] = {
                        'error': error,
                        'timestamp': datetime.now().isoformat(),
                        'actual': actual,
                        'predicted': predicted,
                        'abs_error': abs(actual - predicted)
                    }
        
        # Save the data
        with open(history_file, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        # Count total entries
        total_entries = sum(len(dates) for model, dates in history_data.items())
        
        self.stdout.write(self.style.SUCCESS(
            f"Successfully generated {total_entries} error entries for {len(history_data)} models"
        ))
        self.stdout.write(f"Data saved to: {history_file}")