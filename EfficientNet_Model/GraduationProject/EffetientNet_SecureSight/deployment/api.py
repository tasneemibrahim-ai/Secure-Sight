from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from inference import SecureSightInference

app = FastAPI(title="SecureSight API", description="AI Video Anomaly Detection Deployment")

# Enable CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import HTMLResponse

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    with open("dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

# Initialize Inference Engine
# Point to the best model checkpoint if available
MODEL_PATH = "outputs/checkpoints/best_model.pth"
inference_engine = SecureSightInference(MODEL_PATH if os.path.exists(MODEL_PATH) else None)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    mode = "Simulation" if inference_engine.demo_mode else "Production"
    return {
        "status": "online", 
        "mode": mode,
        "model": "EfficientNet-B0", 
        "task": "Video Anomaly Detection"
    }

@app.post("/analyze-frame")
async def analyze_frame(file: UploadFile = File(...)):
    """Analyze a single uploaded image frame."""
    try:
        temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # If in demo mode, we don't even need cv2 to work
        if inference_engine.demo_mode:
            prob = inference_engine.predict_frame(None)
        else:
            import cv2
            frame = cv2.imread(temp_path)
            if frame is None:
                raise HTTPException(status_code=400, detail="Invalid image file")
            prob = inference_engine.predict_frame(frame)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return {
            "anomaly_probability": prob,
            "is_anomaly": prob > 0.5,
            "alert_level": "CRITICAL" if prob > 0.8 else ("WARNING" if prob > 0.5 else "NORMAL")
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/health")
async def health():
    return {"status": "healthy", "mode": "Simulation" if inference_engine.demo_mode else "Production"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
