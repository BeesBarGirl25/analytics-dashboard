from flask import Blueprint, jsonify

# Create the Blueprint
api_bp = Blueprint("api", __name__)

@api_bp.route("/data")
def get_data():
    # Example JSON response
    return jsonify({"message": "This is an API response!"})
