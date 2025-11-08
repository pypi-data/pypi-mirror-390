import logging
import psutil
import os
import csv
from datetime import datetime

logger = logging.getLogger(__name__)

def capture_system_metrics(event="N/A", output_file: str = "system_metrics.csv") -> dict:
    """Capture current system metrics (CPU, memory percentage, battery level) and write to a CSV file.
    This function captures a single snapshot of metrics and adds one line to the CSV file.
    
    Args:
        output_file (str, optional): Output CSV file path. Defaults to "system_metrics.csv".
        
    Returns:
        dict: Dictionary containing the captured metrics
        
    Raises:
        RuntimeError: When unable to capture metrics or write to file
    """
    try:
        # Check if file exists and create headers if it doesn't
        file_exists = os.path.isfile(output_file)
        
        # Get current metrics
        timestamp = datetime.now().isoformat()
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        # Get battery percentage if available
        battery_percent = "N/A"
        if hasattr(psutil, "sensors_battery") and psutil.sensors_battery() is not None:
            battery_percent = psutil.sensors_battery().percent
        
        # Create metrics dictionary
        metrics = {
            'timestamp': timestamp,
            'event': event,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'battery_percent': battery_percent
        }
        
        # Define headers for CSV
        headers = list(metrics.keys())
        
        # Open file in append mode to add new reading
        with open(output_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            
            # Write headers if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write the metrics to CSV
            writer.writerow(metrics)
        
        logger.debug(f"Captured metrics and save to {output_file} - CPU: {cpu_percent}%, Memory: {memory_percent}%, Battery: {battery_percent}%")
        return metrics
    except Exception as e:
        logger.error(f"Error capturing system metrics: {str(e)}")
        raise RuntimeError(f"Failed to capture system metrics: {str(e)}")