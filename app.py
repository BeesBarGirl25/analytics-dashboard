from flask import Flask
from routes.api_routes import api_bp
from routes.dropdown import competition_bp
from routes.match_analysis import match_analysis_bp

def create_app():
    app = Flask(__name__)

    # Register Blueprints
    app.register_blueprint(match_analysis_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix="/api")  # Prefix for API routes
    app.register_blueprint(competition_bp, url_prefix="/api")


    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
