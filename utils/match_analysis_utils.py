import pandas as pd
from flask import current_app


def goal_assist_data(match_data, match_overview):
    home_team = match_overview['home_team']
    away_team = match_overview['away_team']
    goals = match_data[match_data['shot_outcome'] == 'Goal']

    goals_home = {}
    assists_home = {}
    goals_away = {}
    assists_away = {}

    for id, row in goals.iterrows():
        if row['team'] == home_team[0]:
            if row['player'] not in goals_home:
                goals_home[row['player']] = []
            goals_home[row['player']].append(str(row['minute']))
            if not (row['shot_key_pass_id'] == -999):
                assist = match_data[match_data['id'] == row['shot_key_pass_id']]
                assist_player = assist['player'].iloc[0]
                if assist_player not in assists_home:
                    assists_home[assist_player] = []
                assists_home[assist_player].append(
                    str(assist['minute'].iloc[0]))  # Store all assist minutes for this player

        # Process goals for the away team
        if row['team'] == away_team[0]:
            if row['player'] not in goals_away:
                goals_away[row['player']] = []
            goals_away[row['player']].append(str(row['minute']))  # Store all minutes for this player
            if not pd.isna(row['shot_key_pass_id']):
                assist = match_data[match_data['id'] == row['shot_key_pass_id']]
                assist_player = assist['player'].iloc[0]
                if assist_player not in assists_away:
                    assists_away[assist_player] = []
                assists_away[assist_player].append(
                    str(assist['minute'].iloc[0]))  # Store all assist minutes for this player

    # Format the results with combined minutes for multiple goals/assists
    formatted_goals_home = [
        ' '.join([f"{minute}'" for minute in minutes]) + f" {player} {'⚽' * len(minutes)}"
        for player, minutes in goals_home.items()
    ]
    formatted_assists_home = [
        ' '.join([f"{minute}'" for minute in minutes]) + f" {player} {'👟' * len(minutes)}"
        for player, minutes in assists_home.items()
    ]
    formatted_goals_away = [
        ' '.join([f"{minute}'" for minute in minutes]) + f" {player} {'⚽' * len(minutes)}"
        for player, minutes in goals_away.items()
    ]
    formatted_assists_away = [
        ' '.join([f"{minute}'" for minute in minutes]) + f" {player} {'👟' * len(minutes)}"
        for player, minutes in assists_away.items()
    ]

    return formatted_goals_home, formatted_assists_home, formatted_goals_away, formatted_assists_away


# Example usage:
# Assume match_data and match_overview are pandas DataFrames
# x, y, z, a = goal_assist_data(match_data, match_overview)

def match_overview_results(match_overview, match_data):

    fields = [
        'home_managers', 'away_managers', 'stadium', 'home_team',
        'away_team', 'home_score', 'away_score', 'referee', 'competition_stage'
    ]


    # Extract the values for each field
    extracted_data = {field: match_overview[field].iloc[0] for field in fields}

    # Get goal and assist data
    home_goals, home_assists, away_goals, away_assists = goal_assist_data(match_data, match_overview)
    current_app.logger.info(f"Home Goals: {home_goals}")
    home_team_passes, away_team_passes, home_passes_complete, away_passes_complete, home_team_shots, away_team_shots = match_stats_extractor(
        match_overview, match_data)

    # Add the goal and assist data to the dictionary
    extracted_data.update({
        'home_goals': home_goals,
        'home_assists': home_assists,
        'away_goals': away_goals,
        'away_assists': away_assists,
        'home_passes': home_team_passes,
        'away_passes': away_team_passes,
        'home_passes_complete': home_passes_complete,
        'away_passes_complete': away_passes_complete,
        'home_shots': home_team_shots,
        'away_shots': away_team_shots
    })

    return extracted_data


def match_stats_extractor(match_overview, match_data):
    home_team_name = match_overview['home_team'].iloc[0]
    away_team_name = match_overview['away_team'].iloc[0]
    home_team_data = match_data[match_data['team'] == home_team_name]
    away_team_data = match_data[match_data['team'] == away_team_name]

    home_team_passes = (home_team_data['type'] == 'Pass').sum()
    away_team_passes = (away_team_data['type'] == 'Pass').sum()
    home_passes_complete = home_team_passes - home_team_data[
        (home_team_data['type'] == 'Pass') & (home_team_data['pass_outcome'] == 'Incomplete')].shape[0]
    away_passes_complete = away_team_passes - away_team_data[
        (away_team_data['type'] == 'Pass') & (away_team_data['pass_outcome'] == 'Incomplete')].shape[0]
    home_team_shots = home_team_data[home_team_data['type'] == 'Shot'].shape[0]
    away_team_shots = away_team_data[away_team_data['type'] == 'Shot'].shape[0]

    return home_team_passes, away_team_passes, home_passes_complete, away_passes_complete, home_team_shots, away_team_shots
