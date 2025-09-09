from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import cv2
from PIL import Image
import base64
import io
from utils.detection import ObjectDetectionService

app = Flask(__name__)
CORS(app)

# Flask App Config
APP_PORT=5001

# Paths
MODEL_PATH="models/yolov8n.pt"
MODELS_DIR="models"
RESULTS_DIR="results"


# Initialize the detection service
detection_service = ObjectDetectionService(model_path=MODEL_PATH)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "AI Backend"})


@app.route('/detect', methods=['POST'])
def detect_objects():
    """
    Main endpoint for object detection
    Expects: multipart/form-data with 'image' file
    Returns: JSON with detection results
    """
    try:
        # Check if image file is present
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

        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        file.save(temp_path)
        
        # Perform detection
        results = detection_service.detect_objects(temp_path)
        
        # Convert annotated image to base64 for response
        annotated_image_b64 = None
        if results["success"] and results["annotated_image"] is not None:
            # Convert BGR to RGB for PIL
            rgb_image = cv2.cvtColor(results["annotated_image"], cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Convert to base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')
            buffer.seek(0)
            annotated_image_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Prepare response
        response_data = {
            "success": results["success"],
            "detections": results["detections"],
            "total_detections": results["total_detections"],
            "annotated_image_base64": annotated_image_b64
        }
        
        if not results["success"]:
            response_data["error"] = results.get("error", "Unknown error")
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}",
            "detections": [],
            "total_detections": 0
        }), 500


    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}",
            "detections": [],
            "total_detections": 0
        }), 500


@app.route('/model_info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    try:
        return jsonify({
            "model_name": MODEL_NAME,
            "classes": list(detection_service.model.names.values()),
            "total_classes": len(detection_service.model.names)
        })
    except Exception as e:
        return jsonify({
            "error": f"Could not get model info: {str(e)}"
        }), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(MODELS_DIR, exist_ok=True)

    # Run the Flask app
    app.run(host='0.0.0.0', port=APP_PORT, debug=True)
