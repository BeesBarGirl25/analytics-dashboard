from flask import Blueprint, render_template, request, jsonify, current_app
from statsbombpy import sb
from utils.plotting_functions import generate_match_graph
import pandas as pd

# Define blueprint
match_analysis_bp = Blueprint('match_analysis', __name__)

# Define route
@match_analysis_bp.route('/')
def match_analysis():
    return render_template('match_analysis.html', active_page='match_analysis')

@match_analysis_bp.route('/fetch_matches', methods=['POST'])
def fetch_matches():
    data = request.get_json()
    competition_id = int(data.get('competition_id'))
    season_id = int(data.get('season_id'))

    matches = sb.matches(competition_id, season_id)
    match_data = matches[['match_id', 'home_team', 'away_team']]
    options = [
        {"value": row['match_id'], "text": f"{row['home_team']} vs {row['away_team']}"}
        for _, row in match_data.iterrows()
    ]

    return jsonify(options)

@match_analysis_bp.route('/fetch_match_graph', methods=['POST'])
def fetch_match_graph():
    data = request.get_json()
    match_id = int(data.get('match_id'))
    width = int(data.get('width'))  # Pass width dynamically
    height = int(data.get('height'))  # Pass height dynamically

    match = sb.events(match_id)

    fig = generate_match_graph(match)

    fig.update_layout(
        autosize=False,  # Disable autosizing
        width=width - 40,  # Reduce width slightly to respect container padding
        height=height - 40,  # Reduce height slightly to respect container padding
        margin=dict(
            l=20, r=20, t=40, b=20  # Match container padding
        )
    )

    graph_div = fig.to_html(full_html=False)
    return jsonify({"graph_div": graph_div})




