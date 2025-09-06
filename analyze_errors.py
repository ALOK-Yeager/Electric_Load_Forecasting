#!/usr/bin/env python3
"""
Error Analysis Script for Electric Load Forecasting

This script analyzes the forecast error history and generates reports.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Add the project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.error_history import get_tracker


def print_summary_report(model=None, days=30):
    """
    Print a summary report of forecast errors.
    
    Args:
        model (str, optional): Model name to filter by. Defaults to None (all models).
        days (int, optional): Number of days to analyze. Defaults to 30.
    """
    tracker = get_tracker()
    
    # Get list of models from history
    models = list(tracker.history.keys())
    if not models:
        print("No error history found.")
        return
    
    if model and model not in models:
        print(f"Model '{model}' not found in history. Available models: {', '.join(models)}")
        return
    
    models_to_analyze = [model] if model else models
    
    print(f"\n{'=' * 60}")
    print(f"FORECAST ERROR SUMMARY REPORT ({days} days)")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")
    
    for model_name in models_to_analyze:
        stats = tracker.get_error_statistics(model_name, days=days)
        recent_errors = tracker.get_recent_errors(model_name, days=days)
        
        print(f"\nMODEL: {model_name}")
        print(f"  - Forecasts analyzed: {stats['count']}")
        
        if stats['count'] == 0:
            print("  - No error data available")
            continue
        
        print(f"  - Average error: {stats['avg']:.2f}%")
        print(f"  - Min error: {stats['min']:.2f}%")
        print(f"  - Max error: {stats['max']:.2f}%")
        print(f"  - Forecasts exceeding 5% threshold: {stats['above_threshold_count']} ({(stats['above_threshold_count']/stats['count']*100):.1f}%)")
        
        # Most recent errors (last 5 days)
        if recent_errors:
            print("\n  RECENT ERRORS (last 5 days):")
            for date, error in sorted(recent_errors, key=lambda x: x[0], reverse=True)[:5]:
                status = "✓" if error <= 5.0 else "✗"
                print(f"    {date}: {error:.2f}% {status}")
    
    print(f"\n{'=' * 60}")


def generate_error_plot(output_file=None, model=None, days=30):
    """
    Generate a plot of forecast errors over time.
    
    Args:
        output_file (str, optional): Path to save the plot. Defaults to 'error_plot.png'.
        model (str, optional): Model to filter by. Defaults to None (all models).
        days (int, optional): Number of days to analyze. Defaults to 30.
    """
    tracker = get_tracker()
    
    # Get list of models from history
    models = list(tracker.history.keys())
    if not models:
        print("No error history found.")
        return
    
    if model and model not in models:
        print(f"Model '{model}' not found in history.")
        return
    
    models_to_plot = [model] if model else models
    
    plt.figure(figsize=(12, 6))
    
    for model_name in models_to_plot:
        recent_errors = tracker.get_recent_errors(model_name, days=days)
        if not recent_errors:
            continue
        
        dates, errors = zip(*recent_errors)
        plt.plot(dates, errors, marker='o', linestyle='-', label=model_name)
    
    plt.axhline(y=5.0, color='r', linestyle='--', alpha=0.7, label='5% Threshold')
    
    plt.title(f'Forecast Error History (Last {days} Days)')
    plt.xlabel('Date')
    plt.ylabel('Error (%)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file)
        print(f"Plot saved to {output_file}")
    else:
        # Use a default filename in the data directory
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'error_plot.png')
        plt.savefig(output_path)
        print(f"Plot saved to {output_path}")


def export_error_data(output_file=None, format='csv', model=None, days=30):
    """
    Export error data to a file.
    
    Args:
        output_file (str, optional): Path to save the data. Defaults to auto-generated.
        format (str, optional): Format to export ('csv' or 'json'). Defaults to 'csv'.
        model (str, optional): Model to filter by. Defaults to None (all models).
        days (int, optional): Number of days to analyze. Defaults to 30.
    """
    tracker = get_tracker()
    
    # Get list of models from history
    models = list(tracker.history.keys())
    if not models:
        print("No error history found.")
        return
    
    if model and model not in models:
        print(f"Model '{model}' not found in history.")
        return
    
    models_to_export = [model] if model else models
    
    # Prepare data for export
    export_data = {}
    
    for model_name in models_to_export:
        model_history = tracker.get_model_history(model_name)
        
        # Filter by date
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        recent_entries = {
            date: entry 
            for date, entry in model_history.items()
            if date >= cutoff_date
        }
        
        if recent_entries:
            export_data[model_name] = recent_entries
    
    if not export_data:
        print("No data to export.")
        return
    
    # Generate default output path if not provided
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        model_suffix = f"_{model}" if model else ""
        output_file = os.path.join(output_dir, f"error_export{model_suffix}_{timestamp}.{format}")
    
    if format.lower() == 'json':
        # Export as JSON
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"Data exported to {output_file} in JSON format")
    
    elif format.lower() == 'csv':
        # Flatten data for CSV
        rows = []
        
        for model_name, entries in export_data.items():
            for date, entry in entries.items():
                row = {
                    'model': model_name,
                    'date': date,
                    'error': entry['error']
                }
                
                # Add additional metrics if available
                for key, value in entry.items():
                    if key not in ['error', 'timestamp']:
                        row[key] = value
                
                rows.append(row)
        
        # Convert to DataFrame and save
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(output_file, index=False)
            print(f"Data exported to {output_file} in CSV format")
        else:
            print("No data to export.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze forecast error history')
    
    # Command options
    parser.add_argument('--report', action='store_true', help='Generate a summary report')
    parser.add_argument('--plot', action='store_true', help='Generate an error plot')
    parser.add_argument('--export', action='store_true', help='Export error data')
    
    # Filtering options
    parser.add_argument('--model', type=str, help='Filter by model name')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze (default: 30)')
    
    # Output options
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--format', type=str, choices=['csv', 'json'], default='csv',
                        help='Export format (default: csv)')
    
    args = parser.parse_args()
    
    # If no command specified, show report
    if not (args.report or args.plot or args.export):
        args.report = True
    
    # Run selected commands
    if args.report:
        print_summary_report(args.model, args.days)
    
    if args.plot:
        generate_error_plot(args.output, args.model, args.days)
    
    if args.export:
        export_error_data(args.output, args.format, args.model, args.days)