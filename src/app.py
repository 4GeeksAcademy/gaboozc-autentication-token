"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from api.utils import APIException, generate_sitemap
from api.models import db
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands
from flask_cors import CORS

# Environment configuration
ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests
app.url_map.strict_slashes = False

# Database configuration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

# Add the admin and commands
setup_admin(app)
setup_commands(app)

# Register the API blueprint
app.register_blueprint(api, url_prefix='/api')

# Handle errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generate sitemap with all your endpoints
@app.route('/sitemap')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return jsonify({"error": "Not available in production"}), 404

# Serve only API routes with Flask, React handles everything else
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_routes(path):
    """
    Serve only API routes with Flask.
    """
    return api(path)

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
