import pandas as pd
import logging
import numpy as np

pd.set_option('display.max_columns', None)  # Ensures all columns are shown
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)  # Prevents breaking columns into multiple lines


def prepare_plot_data(data, value_vars, value_name):
    """
    Prepare data for plotting by melting it.
    Parameters:
        data (pd.DataFrame): Input dataset.
        value_vars (list): List of column names to include in the melting process.
        value_name (str): Name for the values in the resulting melted DataFrame.
    Returns:
        pd.DataFrame: Reshaped DataFrame ready for plotting.
    """
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # Ensure value_vars is a list
    if isinstance(value_vars, str):
        #logging.warning("value_vars should be a list of column names, not a string. Converting to a list.")
        value_vars = [value_vars]

    #logging.debug(f"Provided value_vars: {value_vars}")
    #logging.debug(f"Input data columns: {list(data.columns)}")

    # Ensure the provided value_vars actually exist in the input data
    matched_vars = [col for col in value_vars if col in data.columns]
    missing_vars = [col for col in value_vars if col not in data.columns]

    if missing_vars:
        logging.warning(f"The following value_vars are missing in the input data: {missing_vars}")
    if not matched_vars:
        logging.warning("No valid columns found for melting. Returning empty DataFrame.")
        return pd.DataFrame()

    # Proceed with melting
    melted = data.melt(
        id_vars=['minutes'],
        value_vars=matched_vars,
        var_name='Metric',
        value_name=value_name
    )
    #logging.debug(f"Data after melting:\n{melted.head()}")

    # Adjust 'Metric' for readability
    melted['Metric'] = melted['Metric'].str.replace('_', ' ').str.capitalize()
    #logging.debug(f"Data after transforming 'Metric' column:\n{melted.head()}")

    return melted






import pandas as pd
import logging

def extend_data_without_merge(data, column_name):
    """
    Extend the data by ensuring the last row is at 90 minutes or the maximum minute,
    duplicating the previous value for the specified column (e.g., Cumulative xG or Total Goals).

    Parameters:
        data (pd.DataFrame): Input data with columns 'minutes' and the column to extend.
        column_name (str): The column to calculate cumulative metrics for (e.g., 'Cumulative xG').

    Returns:
        pd.DataFrame: Data with a final row at the last minute added (if needed).
    """
    import pandas as pd
    import logging

    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    #logging.info("Starting extend_data_without_merge function.")

    # Ensure 'minutes' is clean and numeric
    data['minutes'] = pd.to_numeric(data['minutes'], errors='coerce').fillna(0).astype(int)
    #logging.debug(f"Cleaned 'minutes' column:\n{data[['minutes']].head()}")

    # Check for missing or unexpected values
    missing_minutes = data['minutes'].isnull().sum()
    missing_column_data = data[column_name].isnull().sum()
    #logging.info(f"Missing 'minutes': {missing_minutes}, Missing '{column_name}': {missing_column_data}")

    # Find the last minute in the data
    last_minute = data['minutes'].max()
    final_minute = max(last_minute, 90)  # Final minute is the greater of 90 or the max minute
    #logging.debug(f"Last minute in data: {last_minute}, Final minute to ensure: {final_minute}")

    # Add a row with the same values if the last minute is less than the final minute
    if last_minute < final_minute:
        last_row = data.iloc[-1].copy()
        last_row['minutes'] = final_minute
        data = pd.concat([data, pd.DataFrame([last_row])], ignore_index=True)
        #logging.info(f"Added final row at minute {final_minute}. Data now has {len(data)} rows.")

    #logging.info(f"Final extended data contains {len(data)} rows.")
    #logging.debug(f"Final extended data preview:\n{data.head()}")

    return data






