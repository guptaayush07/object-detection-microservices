from ultralytics import YOLO

class ObjectDetectionService:
    def __init__(self,model_path):
        # Initialize YOLOv8 model (will download if not present)
        self.model = YOLO(model_path)  # This will auto-download the model

    def detect_objects(self, image_path):
        """
        Perform object detection on the given image
        Returns: detection results with bounding boxes and annotated image
        """
        try:
            # Run inference
            results = self.model(image_path)

            # Process results
            detections = []
            annotated_image = None

            for r in results:
                # Get annotated image
                annotated_image = r.plot()

                # Extract detection data
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                        # Get confidence and class
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.model.names[class_id]

                        detection = {
                            "class_name": class_name,
                            "class_id": class_id,
                            "confidence": float(confidence),
                            "bounding_box": {
                                "x1": float(x1),
                                "y1": float(y1),
                                "x2": float(x2),
                                "y2": float(y2),
                                "width": float(x2 - x1),
                                "height": float(y2 - y1)
                            }
                        }
                        detections.append(detection)

            return {
                "success": True,
                "detections": detections,
                "total_detections": len(detections),
                "annotated_image": annotated_image
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "detections": [],
                "total_detections": 0
            }