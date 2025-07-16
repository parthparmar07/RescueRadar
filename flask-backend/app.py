from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Import route modules
from routes.ai_analysis import ai_bp
from routes.reports import reports_bp
from routes.notifications import notifications_bp
from routes.upload import upload_bp
from routes.email_management import email_bp

# Register blueprints
app.register_blueprint(ai_bp, url_prefix='/api')
app.register_blueprint(reports_bp, url_prefix='/api')
app.register_blueprint(notifications_bp, url_prefix='/api')
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(email_bp, url_prefix='/api/email')

@app.route('/api/health', methods=['GET'])
def health_check():
    """API Health Check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'services': {
            'ai_analysis': 'healthy' if os.getenv('GROQ_API_KEY') else 'misconfigured',
            'email': 'healthy' if os.getenv('BREVO_API_KEY') else 'misconfigured',
            'whatsapp': 'healthy' if os.getenv('TWILIO_ACCOUNT_SID') else 'misconfigured',
            'google_maps': 'healthy' if os.getenv('GOOGLE_MAPS_API_KEY') else 'misconfigured',
            'database': 'healthy' if os.getenv('SUPABASE_URL') else 'misconfigured'
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
