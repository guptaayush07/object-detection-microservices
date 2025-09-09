import json
import base64
import requests
import os
from datetime import datetime

class UIService:
    def __init__(self,ai_backend_url):
        self.ai_backend_url = ai_backend_url
        
    def check_ai_backend_health(self):
        """Check if AI backend is healthy"""
        try:
            response = requests.get(f"{self.ai_backend_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def process_image(self, image_file,upload_folder,results_folder):
        """Send image to AI backend for processing"""
        try:
            # Save uploaded image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_filename = f"original_{timestamp}_{image_file.filename}"
            image_path = os.path.join(upload_folder, original_filename)
            image_file.save(image_path)
            
            # Send to AI backend
            with open(image_path, 'rb') as f:
                files = {'image': (image_file.filename, f, 'image/jpeg')}
                response = requests.post(
                    f"{self.ai_backend_url}/detect",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                result_data = response.json()
                
                # Save results
                results = self.save_results(result_data, timestamp, original_filename,results_folder)
                results['original_image_path'] = image_path
                return results
            else:
                return {
                    "success": False,
                    "error": f"AI Backend error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing error: {str(e)}"
            }
    
    def save_results(self, result_data, timestamp, original_filename,results_folder):
        """Save detection results and annotated image"""
        try:
            # Save JSON results
            json_filename = f"detections_{timestamp}.json"
            json_path = os.path.join(results_folder, json_filename)
            
            # Prepare JSON data (without base64 image for cleaner file)
            json_data = {
                "timestamp": timestamp,
                "original_filename": original_filename,
                "success": result_data["success"],
                "total_detections": result_data["total_detections"],
                "detections": result_data["detections"]
            }
            
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            # Save annotated image if available
            annotated_image_path = None
            if result_data.get("annotated_image_base64"):
                annotated_filename = f"annotated_{timestamp}.png"
                annotated_image_path = os.path.join(results_folder, annotated_filename)
                
                # Decode and save base64 image
                image_data = base64.b64decode(result_data["annotated_image_base64"])
                with open(annotated_image_path, 'wb') as f:
                    f.write(image_data)
            
            return {
                "success": True,
                "json_path": json_path,
                "annotated_image_path": annotated_image_path,
                "result_data": result_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Save error: {str(e)}"
            }