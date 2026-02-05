"""
Admin API endpoints for full system visibility.
"""
from fastapi import APIRouter
from app.services.admin_logger import admin_logger

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/stats")
async def get_admin_stats():
    """Get admin statistics"""
    return admin_logger.get_stats()


@router.get("/logs")
async def get_logs(limit: int = 50):
    """Get global action logs"""
    return {
        "logs": admin_logger.get_global_logs(limit)
    }


@router.get("/sessions")
async def get_sessions():
    """Get all sessions summary"""
    return {
        "sessions": admin_logger.get_all_sessions_summary()
    }


@router.get("/sessions/{session_id}")
async def get_session_detail(session_id: str):
    """Get detailed session info including conversation and all logs"""
    detail = admin_logger.get_session_detail(session_id)
    if detail:
        return detail
    return {"error": "Session not found"}


@router.get("/full")
async def get_full_admin_view():
    """Get all admin data in one call"""
    return {
        "stats": admin_logger.get_stats(),
        "logs": admin_logger.get_global_logs(30),
        "sessions": admin_logger.get_all_sessions_summary()
    }
