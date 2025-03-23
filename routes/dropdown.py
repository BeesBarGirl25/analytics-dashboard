from flask import jsonify, Blueprint
from statsbombpy import sb

competition_bp = Blueprint("competition", __name__)


@competition_bp.route('/get_competitions')
def get_competitions():
    all_competitions = sb.competitions()
    relevant_data = all_competitions[['competition_name', 'competition_id', 'season_id', 'season_name']]
    relevant_data['display_key'] = relevant_data['competition_name'] + " (" + relevant_data['season_name'] + ")"
    options = relevant_data.to_dict(orient="records")
    return jsonify(options)