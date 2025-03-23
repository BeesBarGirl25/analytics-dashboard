from flask import Blueprint, render_template, request, jsonify, current_app
from statsbombpy import sb
from utils.plotting_functions import generate_match_graph
import pandas as pd

# Define blueprint
match_analysis_bp = Blueprint('match_analysis', __name__)

# Global cache to store match data (temporary for the example)
match_data_cache = {}

# Route for main match analysis page
@match_analysis_bp.route('/')
def match_analysis():
    return render_template('match_analysis.html', active_page='match_analysis')

# Route to fetch matches for a competition/season
@match_analysis_bp.route('/fetch_matches', methods=['POST'])
def fetch_matches():
    try:
        data = request.get_json()
        competition_id = data.get('competition_id')
        season_id = data.get('season_id')

        if competition_id is None or season_id is None:
            return jsonify({"error": "Missing competition_id or season_id"}), 400

        competition_id = int(competition_id)
        season_id = int(season_id)

        matches = sb.matches(competition_id, season_id)
        match_data = matches[['match_id', 'home_team', 'away_team', 'competition_stage']]
        options = [
            {
                "competition_stage": row['competition_stage'],
                "value": row['match_id'],
                "text": f"{row['home_team']} vs {row['away_team']}"
            }
            for _, row in match_data.iterrows()
        ]
        return jsonify(options), 200

    except ValueError:
        return jsonify({"error": "Invalid competition_id or season_id"}), 400
    except Exception as e:
        print(f"Error in fetch_matches: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# New endpoint to fetch match data using sb.events
@match_analysis_bp.route('/fetch_match', methods=['POST'])
def fetch_match():
    try:
        data = request.get_json()
        match_id = int(data.get('match_id'))

        # Check if match data is already in cache
        if match_id in match_data_cache:
            print(f"Using cached data for Match ID: {match_id}")
            return jsonify(match_data_cache[match_id]), 200

        # Fetch match data from StatsBomb API
        match = sb.events(match_id)
        # Handle NaN values and convert DataFrame to JSON-serializable format
        match_cleaned = match.fillna(-999)
        match_data = match_cleaned.to_dict(orient='records')

        # Cache the cleaned data
        match_data_cache[match_id] = match_data
        return jsonify(match_data), 200

    except ValueError:
        return jsonify({"error": "Invalid match_id"}), 400
    except Exception as e:
        print(f"Error in fetch_match: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


# Updated fetch_match_graph to use cached match data
@match_analysis_bp.route('/fetch_match_graph', methods=['POST'])
def fetch_match_graph():
    try:
        data = request.get_json()
        match_id = int(data.get('match_id'))
        width = int(data.get('width', 800))  # Default width
        height = int(data.get('height', 600))  # Default height

        # Retrieve cached match data
        if match_id not in match_data_cache:
            return jsonify({"error": "Match data not found. Fetch it first with /fetch_match"}), 400

        match = pd.DataFrame(match_data_cache[match_id])  # Convert cached dict back to DataFrame
        fig = generate_match_graph(match)
        fig.update_layout(
            autosize=False,
            width=width - 40,
            height=height - 40,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        graph_div = fig.to_html(full_html=False)
        return jsonify({"graph_div": graph_div}), 200

    except ValueError:
        return jsonify({"error": "Invalid match_id"}), 400
    except Exception as e:
        print(f"Error in fetch_match_graph: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
