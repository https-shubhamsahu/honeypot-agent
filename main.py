from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router as api_router
from app.api.dashboard import router as dashboard_router
from app.api.admin import router as admin_router
import os

app = FastAPI(title="Agentic Honey-Pot API", version="1.0.0")

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
    return {"message": "Agentic Honey-Pot is running"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
