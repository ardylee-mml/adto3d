from flask import Flask, render_template, request, send_file
import os
from datetime import datetime
from scripts.convert_to_3d import create_3d_model

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/convert', methods=['POST'])
def convert():
    # Handle file upload
    if 'file' not in request.files:
        return "No file uploaded", 400
        
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Save uploaded file
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(upload_path)

    # Generate unique output filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"model_{timestamp}.fbx"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    # Convert to 3D
    try:
        create_3d_model({}, upload_path, output_path)
    except Exception as e:
        return f"Conversion failed: {str(e)}", 500

    return render_template('preview.html', 
                         model_file=output_filename,
                         original_image=file.filename)

@app.route('/download/<filename>')
def download(filename):
    return send_file(
        os.path.join(app.config['OUTPUT_FOLDER'], filename),
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 