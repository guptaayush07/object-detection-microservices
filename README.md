# Object Detection Microservices

This project consists of two microservices for object detection:

- **AI Backend Service**: Handles object detection using YOLOv8  
- **UI Backend Service**: Provides web interface for image upload and result display  

---

## Prerequisites
- Python 3.10 or higher  
- Docker and Docker Compose (for containerized setup)  
- Git  

---

## Project Structure
```

object-detection-microservices/
├── ai-backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── models/
│   └── utils/
├── ui-backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── static/
│   ├── templates/
│   └── utils/
├── Dockerfile.ai
├── Dockerfile.ui
└── docker-compose.yml

````
### Configuration for API Communication

To enable the **UI Backend** to communicate with the **AI Backend**, update the `api.py` file inside the `ui-backend` microservice with the correct `AI_BACKEND_URL`.

- **For Docker environment**  
  ```python
  AI_BACKEND_URL = "http://ai-service:5001"
  ```

- **For Local environment**

  ```python
  AI_BACKEND_URL = "http://127.0.0.1:5001"
  ```

👉 Note: When running inside Docker, always use the **service name** (`ai-service`) instead of `localhost` or `127.0.0.1` to call other services.

## Option 1: Running with Docker (Recommended)

**Clone the repository**
```bash
git clone https://github.com/guptaayush07/object-detection-microservices.git
cd object-detection-microservices
````

**Build and run using Docker Compose**

```bash
docker-compose up --build
```

**Access the application**

* Web Interface: [http://localhost:5000](http://localhost:5000)
* AI Service API: [http://localhost:5001](http://localhost:5001)

**Stop the services**

```bash
docker-compose down
```

---

## Option 2: Manual Setup

**Clone the repository**

```bash
git clone https://github.com/guptaayush07/object-detection-microservices.git
cd object-detection-microservices
```

**Set up AI Backend**

```bash
cd ai-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python app.py
```

The AI service will run on [http://localhost:5001](http://localhost:5001)

**Set up UI Backend (in a new terminal)**

```bash
cd ui-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python app.py
```

The UI service will run on [http://localhost:5000](http://localhost:5000)

---

## Usage

1. Open [http://localhost:5000](http://localhost:5000) in your web browser
2. Upload an image using the web interface
3. Click **"Upload & Detect"** to process the image
4. View the detection results displayed on the page

---

## API Endpoints

### AI Service (Port 5001)

* **POST** `/detect`: Process image for object detection

  * **Input**: Image file
  * **Output**: JSON with detection results

### UI Service (Port 8000)

* **GET** `/`: Home page
* **POST** `/upload`: Handle image upload
* **GET** `/results/<filename>`: View detection results


---

## File Storage

* Uploaded images are stored in `uploads`
* Detection results are stored in `results`

---

## Notes

* For Docker setup, volumes are used to persist uploads and results
* The UI service depends on the AI service being available
* Default ports can be modified in `docker-compose.yml` or app configurations
* YOLOv8 model is automatically downloaded on first run

---

## Troubleshooting

**Services not starting:**

* Check if ports `5000` and `5001` are available
* Ensure Docker daemon is running (for Docker setup)

**Upload errors:**

* Check folder permissions for `uploads` and `results` directories

**Detection not working:**

* Ensure AI service is running and accessible
* Check model file existence in `models` directory