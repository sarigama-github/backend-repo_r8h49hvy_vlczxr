import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="AI Product Photo Generator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


# ---------------------------
# Dummy Image Processing API
# ---------------------------
class UploadResponse(BaseModel):
    imageId: str
    previewUrl: str


@app.post("/api/upload", response_model=UploadResponse)
async def api_upload(file: UploadFile = File(...)):
    # In a real implementation, store file and return persistent url + id
    # Here we return dummy identifiers
    image_id = "demo-image-id"
    preview_url = "/placeholder-preview"  # front-end will use objectURL for preview anyway
    return UploadResponse(imageId=image_id, previewUrl=preview_url)


class RemoveBgRequest(BaseModel):
    imageId: str

class RemoveBgResponse(BaseModel):
    bgRemovedUrl: str


@app.post("/api/remove-background", response_model=RemoveBgResponse)
async def remove_background(req: RemoveBgRequest):
    # Dummy background removal
    return RemoveBgResponse(bgRemovedUrl=f"/bg-removed/{req.imageId}")


class GenerateViewsRequest(BaseModel):
    imageId: str
    presets: List[str]
    customAngles: Optional[List[dict]] = []
    targetSizes: Optional[List[str]] = []

class GenerateViewsResponse(BaseModel):
    jobId: str


@app.post("/api/generate-views", response_model=GenerateViewsResponse)
async def generate_views(req: GenerateViewsRequest):
    # Return a dummy job id
    return GenerateViewsResponse(jobId="job-demo-123")


class JobOutput(BaseModel):
    viewName: str
    url: str
    creditCost: int

class JobStatusResponse(BaseModel):
    status: str
    outputs: List[JobOutput] = []


@app.get("/api/job-status", response_model=JobStatusResponse)
async def job_status(jobId: str):
    # Always done for demo; URLs are placeholders as front-end uses local preview
    outputs = [
        JobOutput(viewName="hero", url="/demo/hero", creditCost=1),
        JobOutput(viewName="front", url="/demo/front", creditCost=1),
        JobOutput(viewName="left", url="/demo/left", creditCost=1),
        JobOutput(viewName="right", url="/demo/right", creditCost=1),
        JobOutput(viewName="detail", url="/demo/detail", creditCost=1),
    ]
    return JobStatusResponse(status="done", outputs=outputs)


class ExportZipResponse(BaseModel):
    zipUrl: str


@app.post("/api/export-zip", response_model=ExportZipResponse)
async def export_zip():
    # Provide a dummy downloadable URL
    return ExportZipResponse(zipUrl="/exports/demo.zip")


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
