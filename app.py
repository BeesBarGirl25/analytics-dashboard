from flask import Flask, render_template, request, jsonify
from utils.data_loader import load_and_normalize_json
from utils.preprocess import prepare_plot_data, extend_data_without_merge
from utils.plotly_viz import plot_metrics_plotly
from utils.analytics_by_team import calculate_team_metrics
from utils.wider_utils import time_adjustment
import os
import logging
import pandas as pd
import json

app = Flask(__name__)

# Logging Configuration
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
app.logger.setLevel(logging.DEBUG)

# Configurations
DATA_PATH = "C:/Users/enmat/OneDrive/Documents/Development/Statsbomb/Data/open-data/data/events/"
COMPETITION_ID_FILTER = 55
COMPETITION_TO_MATCH_MAPPING = "./data/competition_to_match_mapping.json"
GAME_MAPPING_FILE = "./data/game_mapping.json"

# Load JSONs once for efficiency
with open(COMPETITION_TO_MATCH_MAPPING, 'r') as f:
    competition_to_match_mapping = json.load(f)
with open(GAME_MAPPING_FILE, 'r') as f:
    game_mapping = json.load(f)


@app.route("/")
def index():
    """Serve the main page with default data."""
    matches_with_teams = get_matches_for_competition(COMPETITION_ID_FILTER)
    default_match = matches_with_teams[0] if matches_with_teams else None

    # Prepare default graph
    logging.info(f"Default Match: {default_match}")
    file_path = os.path.join(DATA_PATH, f"{default_match['match_id']}.json")
    logging.info(f"File Path: {file_path}")
    default_graph_html = generate_graph_html(file_path) if default_match else None

    return render_template("index.html", matches_with_teams=matches_with_teams, default_graph_html=default_graph_html)


@app.route("/fetch-data", methods=["POST"])
def fetch_data():
    try:
        data = request.json
        match_id = data.get("match_id")
        if not match_id:
            return jsonify({"error": "No match ID provided"}), 400

        file_path = os.path.join(DATA_PATH, f"{match_id}.json")
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return jsonify({"error": f"File not found: {file_path}"}), 404

        # Generate raw graph data and layout data
        raw_graph_data, raw_layout_data = generate_graph(file_path)
        if raw_graph_data is None or raw_layout_data is None:
            logging.error("Failed to generate graph data or layout.")
            return jsonify({"error": "Failed to generate graph data"}), 500

        xg_data = decode_dataframe(raw_graph_data)
        goal_data = decode_dataframe(raw_layout_data)
        
        # Verify the data is decoded properly
        logging.debug(f"Decoded xg_data: {xg_data}")
        logging.debug(f"Decoded goal_data: {goal_data}")
        
        fig = plot_metrics_plotly(xg_data, goal_data)


        # Return the figure as JSON for frontend rendering
        return jsonify(fig=fig.to_plotly_json())
    except Exception as e:
        logging.error(f"Unexpected error in fetch_data: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500



def process_graph_data(graph_data, layout_data):
    # Prepare traces for Total Goals
    traces = []
    for team in set(row["Team"] for row in graph_data):
        team_data = [row for row in layout_data if row["Team"] == team]
        trace = {
            "x": [row["minutes"] for row in team_data],
            "y": [row["Total Goals"] for row in team_data],
            "type": "scatter",
            "mode": "lines",
            "name": f"{team} - Total Goals",
            "line":"dict(width=2)"
        }
        traces.append(trace)

    # Prepare traces for cumulative xG
    for team in set(row["Team"] for row in layout_data):
        team_data = [row for row in graph_data if row["Team"] == team]
        trace = {
            "x": [row["minutes"] for row in team_data],
            "y": [row["Cumulative xG"] for row in team_data],
            "type": "scatter",
            "mode": "lines",
            "name": f"{team} - Cumulative xG",
            "line":"dict(width=2, dash='dot')"
        }
        traces.append(trace)

    # Define Plotly layout
    plotly_layout = {
        "title": "Cumulative xG and Total Goals Over Time",
        "xaxis": {"title": "Minutes"},
        "yaxis": {"title": "Metrics"}
    }

    return traces, plotly_layout








def get_matches_for_competition(competition_id):
    """Retrieve all matches and teams for a specific competition."""
    matches = competition_to_match_mapping.get(str(competition_id), [])
    return [
        {"match_id": match_id, "teams": f"{teams[0]} vs {teams[1]}"}
        for match_id in matches
        if (teams := game_mapping.get(f"{match_id}.json"))
    ]


def generate_graph_html(file_path):
    """Generate the HTML representation of the graph."""
    try:
        graph_data, layout = generate_graph(file_path)

        if graph_data is None or graph_data.empty or layout is None:
            raise ValueError("Invalid graph data or layout.")

        fig = plot_metrics_plotly(graph_data, layout)
        return fig.to_html(full_html=False)
    except Exception as e:
        logging.error(f"Error in generate_graph_html: {e}")
        return "<p>Error generating graph HTML.</p>"




def generate_graph(file_path):
    """Generate graph data and layout from match data."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        dfEvent = load_and_normalize_json(file_path)
        if dfEvent is None or dfEvent.empty:
            raise ValueError("DataFrame is empty after loading JSON.")

        normalized_time_periods = time_adjustment(dfEvent)
        teams = normalized_time_periods["team.name"].unique()
        if len(teams) == 0:
            raise ValueError("No teams found in the dataset.")

        combined_xg_melted = pd.DataFrame()
        combined_goal_melted = pd.DataFrame()

        for team in teams:
            team_data = normalized_time_periods[normalized_time_periods["team.name"] == team]
            if team_data.empty:
                continue  # Skip empty team data

            team_metrics = calculate_team_metrics(team_data)
            xg_melted = extend_data_without_merge(
                prepare_plot_data(team_metrics, "cum_xg", "Cumulative xG"),
                "Cumulative xG",
            )
            goal_melted = extend_data_without_merge(
                prepare_plot_data(team_metrics, "goal_total", "Total Goals"),
                "Total Goals",
            )

            xg_melted["Team"] = team
            goal_melted["Team"] = team

            combined_xg_melted = pd.concat([combined_xg_melted, xg_melted], ignore_index=True)
            combined_goal_melted = pd.concat([combined_goal_melted, goal_melted], ignore_index=True)

        if combined_xg_melted.empty or combined_goal_melted.empty:
            raise ValueError("Combined data is empty after processing.")

        return combined_xg_melted, combined_goal_melted
    except Exception as e:
        logging.error(f"Error in generate_graph: {e}")
        return None, None

def decode_dataframe(df):
    """Ensure all columns in the DataFrame are converted to Python-native types."""
    return df.applymap(lambda x: x.tolist() if hasattr(x, 'tolist') else x)



if __name__ == "__main__":
    app.run(debug=True)
