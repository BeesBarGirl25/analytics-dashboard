# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

def time_adjustment(data):
    """
    Adjusts timestamps in the given dataset and calculates minutes based on specific time periods.
    
    Parameters:
        data (pd.DataFrame): A pandas DataFrame containing the following columns:
            - 'timestamp' (str): Original timestamps in string format.
            - 'period' (int): Period values (e.g., 1, 2, 3, etc.).
    
    Returns:
        pd.DataFrame: A pandas DataFrame with the following modifications:
            - Converts 'timestamp' column to datetime format, handling invalid timestamps by dropping the affected rows.
            - Creates a new column, 'adjusted_timestamp', which adds time adjustments (in minutes) to the timestamp based on the period:
                * Period 2: Add 45 minutes.
                * Period 3: Add 90 minutes.
                * Period 4: Add 105 minutes.
                * Period 5: Add 120 minutes.
                * Period 1 (default): No time adjustment.
            - Creates a new column, 'minutes', which calculates the total minutes from the adjusted timestamps.
            - Ensures 'minutes' does not exceed the maximum allowed minutes for the given period (calculated as period * 45).
    """

    # Convert timestamps to datetime
    data = data.copy()
    data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
    # Drop rows with invalid timestamps
    data = data.dropna(subset=['timestamp'])

    # Add time adjustments for each period
    data['adjusted_timestamp'] = data['timestamp'] + pd.to_timedelta(
        np.select(
            [data['period'] == 2, data['period'] == 3, data['period'] == 4, data['period'] == 5],
            [45, 90, 105, 120],
            default=0  # Default value for period 1
        ),
        unit='m'
    )

    # Calculate minutes from adjusted timestamps
    data['minutes'] = data['adjusted_timestamp'].dt.hour * 60 + data['adjusted_timestamp'].dt.minute

    # Cap minutes at the maximum multiple of 45 for the period
    data['minutes'] = np.minimum(
        data['minutes'],  # Current calculated minutes
        data['period'] * 45  # Maximum allowed minutes based on period
    )
    return data
