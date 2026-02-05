from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router, chat_endpoint, verify_api_key
from app.api.dashboard import router as dashboard_router
from app.api.admin import router as admin_router
from app.models import ChatRequest
from fastapi import Depends
import os

app = FastAPI(title="Agentic Honey-Pot API", version="1.0.0")

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(api_router)
app.include_router(dashboard_router)
app.include_router(admin_router)

@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard UI"""
    return FileResponse(os.path.join(static_dir, "dashboard.html"))

@app.get("/admin")
async def admin_panel():
    """Serve the admin panel UI"""
    return FileResponse(os.path.join(static_dir, "admin.html"))

@app.get("/tester")
async def tester():
    """Serve the endpoint tester UI"""
    return FileResponse(os.path.join(static_dir, "tester.html"))

@app.get("/")
def root():
    return {"message": "Agentic Honey-Pot is running", "status": "ok"}

# Also handle POST at root endpoint (in case GUVI sends to /)
@app.post("/")
async def root_post(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    """Handle POST at root - redirects to chat endpoint"""
    return await chat_endpoint(request, api_key)

# Handle POST at /webhook (common alternative endpoint)
@app.post("/webhook")
async def webhook_post(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    """Handle POST at /webhook - redirects to chat endpoint"""
    return await chat_endpoint(request, api_key)

# Handle POST at /api/chat (another common pattern)
@app.post("/api/chat")
async def api_chat_post(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    """Handle POST at /api/chat - redirects to chat endpoint"""
    return await chat_endpoint(request, api_key)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

