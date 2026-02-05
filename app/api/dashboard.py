"""
Dashboard API endpoints for real-time data.
"""
from fastapi import APIRouter
from app.services.data_store import data_store

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_stats():
    """Get dashboard statistics"""
    return data_store.get_dashboard_stats()


@router.get("/activities")
async def get_activities(limit: int = 10):
    """Get recent activities"""
    return {
        "activities": data_store.get_recent_activities(limit)
    }


@router.get("/sessions")
async def get_sessions(limit: int = 10):
    """Get recent sessions"""
    return {
        "sessions": data_store.get_recent_sessions(limit)
    }


@router.get("/intelligence")
async def get_intelligence():
    """Get intelligence summary"""
    return data_store.get_intelligence_summary()


@router.get("/full")
async def get_full_dashboard():
    """Get all dashboard data in one call"""
    return {
        "stats": data_store.get_dashboard_stats(),
        "activities": data_store.get_recent_activities(10),
        "sessions": data_store.get_recent_sessions(5),
        "intelligence": data_store.get_intelligence_summary()
    }
