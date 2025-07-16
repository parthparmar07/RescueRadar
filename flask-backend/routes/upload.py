from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload-image', methods=['POST'])
def upload_image():
    """Handle image upload"""
    try:
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Only PNG, JPG, JPEG, GIF, and WebP are allowed.'
            }), 400
        
        # Create upload directory if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(filepath)
        
        # Generate URL (adjust based on your deployment)
        base_url = request.host_url.rstrip('/')
        image_url = f"{base_url}/uploads/{unique_filename}"
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'filename': unique_filename,
            'message': 'Image uploaded successfully'
        })
        
    except Exception as e:
        print(f"Upload Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to upload image',
            'error': str(e)
        }), 500

@upload_bp.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    from flask import send_from_directory
    return send_from_directory(UPLOAD_FOLDER, filename)
