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

def cumulative_stats(team_data):
    team_data['goals']=team_data['shot_outcome'].apply(lambda x: 1 if x == 'Goal' else 0)
    team_data.replace(-999, 0, inplace=True)
    team_data=team_data.sort_values('minute')
    team_data['cum_goals']=0
    team_data['cum_xg']=0
    team_data['cum_goals']=team_data['goals'].cumsum()
    team_data['cum_xg']=team_data['shot_statsbomb_xg'].cumsum()
    return team_data