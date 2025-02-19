from flask import request, jsonify
from masterpiecex import Masterpiecex
import os
from .api.conversion_handler import handle_conversion

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
        
    try:
        # Save uploaded file temporarily
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)
        
        # Process conversion using the handler
        result, status_code = handle_conversion(file_path)
        
        # Cleanup temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 