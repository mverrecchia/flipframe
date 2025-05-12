import os
import time
import json
import logging
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

current_drawings = {}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://chaelchia.com"]}})
TOKEN_FOLDER = "/home/mverrecchia/Documents/flipdisc2/tokens"

os.makedirs(TOKEN_FOLDER, exist_ok=True)

@app.route('/api/validate_token', methods=['GET'])
def validate_token():

    token = request.args.get('t')
    
    if not token:
        return jsonify({"valid": False, "error": "No token provided"}), 400
    
    token_file = os.path.join(TOKEN_FOLDER, f"{token}.json")
    if not os.path.exists(token_file):
        return jsonify({"valid": False, "error": "Invalid token"}), 404
    
    try:
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        if time.time() > token_data.get('expires', 0):
            return jsonify({"valid": False, "error": "Token expired"}), 400
        
        # if token_data.get('used', False):
        #     return jsonify({"valid": False, "error": "Token already used"}), 400
        
        # token_data['used'] = True
        # with open(token_file, 'w') as f:
        #     json.dump(token_data, f)
        
        return jsonify({"valid": True})
    
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        return jsonify({"valid": False, "error": "Server error"}), 500


@app.route('/api/current_drawing/<token>', methods=['GET'])
def get_current_drawing(token):
    try:
        token_file = os.path.join(TOKEN_FOLDER, f"{token}.json")
        if not os.path.exists(token_file):
            return jsonify({"error": "Invalid token"}), 404
        
        if token in current_drawings:
            return jsonify(current_drawings[token])
        
        return jsonify({"error": "No drawing found"}), 404
        
    except Exception as e:
        logger.error(f"Error retrieving drawing: {e}")
        return jsonify({"error": "Server error"}), 500

@app.route('/api/submit_drawing', methods=['POST'])
def submit_drawing():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        token = data.get('token')
        
        token_file = os.path.join(TOKEN_FOLDER, f"{token}.json")
        if not os.path.exists(token_file):
            return jsonify({"success": False, "error": "Invalid token"}), 404
        
        current_drawings[token] = data
        
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"Error saving drawing: {e}")
        return jsonify({"success": False, "error": "Server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
