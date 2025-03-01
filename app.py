from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
import os
import logging
import shutil
from datetime import datetime
from scripts.convert_to_3d import create_3d_model
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Log the paths
logger.info(f"Base directory: {BASE_DIR}")
logger.info(f"Upload folder: {UPLOAD_FOLDER}")
logger.info(f"Output folder: {OUTPUT_FOLDER}")

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Configure allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Add routes to serve files
@app.route('/uploads/<filename>')
def serve_upload(filename):
    logger.debug(f"Received request for file: {filename}")
    full_path = os.path.join(UPLOAD_FOLDER, filename)
    logger.debug(f"Full path: {full_path}")
    
    if os.path.exists(full_path):
        logger.debug(f"File exists at {full_path}")
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except Exception as e:
            logger.error(f"Error serving file: {str(e)}")
            return str(e), 500
    else:
        logger.error(f"File not found at {full_path}")
        return "File not found", 404

@app.route('/output/<filename>')
def serve_output(filename):
    logger.debug(f"Serving output file: {filename}")
    return send_from_directory(OUTPUT_FOLDER, filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/api/convert', methods=['POST'])
def convert():
    try:
        # Handle file upload
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file uploaded'
            }), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No selected file'
            }), 400

        # Get additional parameters
        is_outfit = request.form.get('isOutfit', 'false').lower() == 'true'
        outfit_type = request.form.get('outfitType', None)

        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Save uploaded file
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)
        
        # Set correct permissions for the uploaded file
        os.chmod(upload_path, 0o644)

        # Generate output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_{timestamp}.glb")

        # Convert to 3D
        params = {
            'isOutfit': is_outfit,
            'outfitType': outfit_type
        }
        result = create_3d_model(params, upload_path, output_path)

        if not result['success']:
            return jsonify({
                'success': False,
                'message': f"Conversion failed: {result.get('error', 'Unknown error')}"
            }), 500

        # Generate URLs for all output files
        base_url = f"http://{request.host}"
        output_urls = {}
        
        for file_type, file_path in result['files'].items():
            relative_path = os.path.relpath(file_path, start=os.path.dirname(OUTPUT_FOLDER))
            output_urls[file_type] = f"{base_url}/outputs/{os.path.basename(file_path)}"

        return jsonify({
            'success': True,
            'message': 'Conversion completed successfully',
            'outputs': output_urls,
            'requestId': result.get('requestId')
        })

    except Exception as e:
        app.logger.error(f"Error in /api/convert: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/download/<filename>')
def download(filename):
    return send_file(
        os.path.join(OUTPUT_FOLDER, filename),
        as_attachment=True
    )

@app.route('/api/validate-image', methods=['POST'])
def validate_image():
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'message': 'No file provided'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'message': 'No file selected'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'message': 'Invalid file type. Please upload a PNG or JPG image.'
        }), 400
    
    # If validation passes
    return jsonify({
        'success': True,
        'message': 'File is valid'
    })

@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    logger.debug('Body: %s', request.get_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 