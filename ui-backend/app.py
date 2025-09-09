from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
from utils.ui_service import UIService
from api import AI_BACKEND_URL

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
# Allowed extensions
ALLOWED_EXTENSIONS = {'bmp', 'dng', 'jpeg', 'jpg', 'mpo', 'png', 'tif', 'tiff', 'webp', 'pfm'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Initialize UI service
ui_service = UIService(AI_BACKEND_URL)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    ai_backend_healthy = ui_service.check_ai_backend_health()
    return jsonify({
        "status": "healthy",
        "service": "UI Backend",
        "ai_backend_healthy": ai_backend_healthy
    })

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload and processing"""
    try:
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "error": "No image file provided"
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No image file selected"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "Invalid file type. Allowed: " + ", ".join(ALLOWED_EXTENSIONS)
            }), 400
        
        # Check if AI backend is healthy
        if not ui_service.check_ai_backend_health():
            return jsonify({
                "success": False,
                "error": "AI Backend is not available"
            }), 503
        
        # Process the image
        results = ui_service.process_image(file,UPLOAD_FOLDER,RESULTS_FOLDER)
        
        if results["success"]:
            return jsonify({
                "success": True,
                "message": "Image processed successfully",
                "total_detections": results["result_data"]["total_detections"],
                "detections": results["result_data"]["detections"],
                "json_file": os.path.basename(results["json_path"]),
                "annotated_image_file": os.path.basename(results["annotated_image_path"]) if results["annotated_image_path"] else None
            })
        else:
            return jsonify(results), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download result files"""
    try:
        file_path = os.path.join(RESULTS_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/results')
def list_results():
    """List all result files"""
    try:
        files = []
        for filename in os.listdir(RESULTS_FOLDER):
            file_path = os.path.join(RESULTS_FOLDER, filename)
            files.append({
                "filename": filename,
                "size": os.path.getsize(file_path),
                "modified": os.path.getmtime(file_path)
            })
        
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/model_info')
def get_model_info():
    """Get information about the AI model"""
    try:
        response = requests.get(f"{ui_service.ai_backend_url}/model_info", timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Could not fetch model info"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)