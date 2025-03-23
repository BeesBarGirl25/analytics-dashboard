import pandas as pd
import json
import numpy as np
from flask import current_app

def squad_categorized(categories, team_data):
    """
    Categorizes players into predefined categories based on their positions from team data.

    Parameters:
    - categories (dict): A dictionary mapping player positions (keys) to categories (values).
    - team_data (DataFrame): A pandas DataFrame containing team lineup data with columns like 'tactics.lineup'.

    Returns:
    - df (DataFrame): A pandas DataFrame where each column corresponds to a player category 
                      (e.g., 'Goalkeeper', 'Defenders'), and rows list the player names.
    - unmatched_positions (list): A list of positions that do not match any category in the categories dictionary.
    """
    
    # Prepare storage for categorized players and unmatched positions
    categorized = {"Goalkeeper": [], "Defenders": [], "Midfielders": [], "Forwards": []}
    unmatched_positions = []
    all_players = set()  # Set to track all player names globally

    # Filter out rows where 'tactics.lineup' is null
    lineups = team_data[team_data['tactics'] != -999]
    
    # Loop through all rows in 'lineups'
    for lineup in lineups['tactics']:
        for entry in lineup['lineup']:  # Loop through each player's data in the lineup
            position = entry['position']['name']
            player_name = entry['player']['name']
            
            # Add the player only if they are not already in the global set
            if player_name not in all_players:
                # Match position to category
                if position in categories:
                    category = categories[position]
                    categorized[category].append(player_name)
                    all_players.add(player_name)  # Track the player globally
                else:
                    # If position does not match any category, add to unmatched
                    unmatched_positions.append(position)

    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in categorized.items()]))
    
    return df, unmatched_positions

def calculate_team_metrics(data):
    """
    calculate_team_metrics(data)
    
    Calculates cumulative expected goals (xG) and total goals for a team based on shot data.
    
    Parameters:
        data (pd.DataFrame): A pandas DataFrame containing match event data. Expected columns include:
            - 'type.name' (str): Indicates the type of event (e.g., 'Shot').
            - 'shot.statsbomb_xg' (float): Expected goals (xG) values for each shot.
            - 'shot.outcome.name' (str): Outcome of the shot (e.g., 'Goal').
            - 'timestamp', 'adjusted_timestamp', 'minutes', 'period' (various types): Other match-related data columns.
    
    Returns:
        pd.DataFrame: A pandas DataFrame filtered and modified to include the following:
            - Only rows where 'type.name' is 'Shot'.
            - Fills missing values in 'shot.statsbomb_xg' with 0.
            - Adds 'cum_xg', a column representing the cumulative sum of xG values.
            - Adds 'goal_total', a column representing the cumulative count of goals based on the outcome of the shot.
            - Forwards fills and replaces any remaining NaN values in 'cum_xg' and 'goal_total' with 0.
            - Returns the following selected columns:
                ['team.name', 'type.name', 'shot.statsbomb_xg', 'timestamp',
                 'adjusted_timestamp', 'minutes', 'period', 'shot.outcome.name'].
    """
    data = data.copy()
    data = data[data['type.name'] == 'Shot']
    data['shot.statsbomb_xg'] = data['shot.statsbomb_xg'].fillna(0)
    data["cum_xg"] = data['shot.statsbomb_xg'].cumsum()
    data["goal_total"] = (
        ((data['shot.outcome.name'] == 'Goal')).astype(int).cumsum()
    )
    data["cum_xg"] = data["cum_xg"].ffill()  # Forward fill
    data["cum_xg"] = data["cum_xg"].fillna(0)  # Fill remaining NaNs with 0
    data["goal_total"] = data["goal_total"].ffill()  # Forward fill
    data["goal_total"] = data["goal_total"].fillna(0)  # Fill remaining NaNs with 0
    return data[['team.name', 'type.name', 'shot.statsbomb_xg', 'timestamp', 'adjusted_timestamp', 'minutes', 'period', 'shot.outcome.name', 'cum_xg', 'goal_total']]

def substitutions_summary(data):
    """
    calculate_team_metrics(data)
    
    Description:
        Calculates cumulative expected goals (xG) and total goals for a team based on shot data.
    
    Parameters:
        data (pd.DataFrame): A pandas DataFrame containing the match event data with the following columns:
            - 'type.name' (str): Type of event (e.g., 'Shot').
            - 'shot.statsbomb_xg' (float): Expected goals (xG) for each shot.
            - 'shot.outcome.name' (str): Outcome of the shot (e.g., 'Goal').
    
    Returns:
        pd.DataFrame: A pandas DataFrame filtered to include shot data with the following additional columns:
            - 'cum_xg': Cumulative xG values.
            - 'goal_total': Cumulative total of goals scored.
    """

    x = data[['minute','player.name','substitution.outcome.name','substitution.replacement.name']].dropna()
    x.columns=['Minute','Player Off', 'Substitution Reason', 'Player On']
    x.reset_index(drop=True)
    return x

def generate_team_summary_data(data):
    """
    generate_team_summary_data(data)
    
    Description:
        Generates a summary table with key statistics for a team's performance, including formations, shots, and passes.
    
    Parameters:
        data (pd.DataFrame): A pandas DataFrame containing team performance data with the following columns:
            - 'tactics.formation' (int): Team formations at different timestamps.
            - 'shot.type.name' (str): Type of shots taken.
            - 'type.name' (str): Type of events (e.g., 'Pass', 'Ball Receipt*').
    
    Returns:
        pd.DataFrame: A summary DataFrame with two columns:
            - 'Statistic': The name of the performance statistic.
            - 'Value': The corresponding value for that statistic.
    """

    summary_data = pd.DataFrame(columns=['Statistic', 'Value'])
    summary_data.loc[len(summary_data)] = ['Starting Formation',data['tactics.formation'][0]]
    summary_data.loc[len(summary_data)] = ['Ending Formation', data['tactics.formation'].unique()[-1]]
    summary_data.loc[len(summary_data)] = ['Shots', data['shot.type.name'].dropna().count()]
    summary_data.loc[len(summary_data)] = ['Passes Attempted', data['type.name'].where(data['type.name']=='Pass').count()]
    summary_data.loc[len(summary_data)] = ['Passes Completed', data['type.name'].where(data['type.name']=='Ball Receipt*').count()]
    return summary_data