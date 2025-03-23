from flask import Flask
from routes.home_routes import home_bp
from routes.api_routes import api_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(home_bp)
    app.register_blueprint(api_bp, url_prefix="/api")  # Prefix for API routes

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
