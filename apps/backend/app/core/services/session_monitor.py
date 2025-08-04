"""
Background tasks for training session management.
Handles auto-pause, cleanup, and session monitoring.
"""

import asyncio
import logging
from typing import List
from datetime import datetime, timezone, timedelta

from db.session import get_db
from db.crud.training_session import (
    get_long_running_sessions,
    abandon_session
)
from db.models.training_session import SessionStatus
from config.app_settings import settings

logger = logging.getLogger(__name__)

class SessionMonitorService:
    """Service for monitoring and managing training sessions."""
    
    def __init__(self):
        self.is_running = False
        self.task = None
        
        # Configuration - Only for long-running session abandonment
        self.abandon_hours = 24       # Abandon after 24 hours
        self.check_interval = 300     # Check every 5 minutes (300 seconds)
    
    async def start(self):
        """Start the session monitoring background task."""
        if self.is_running:
            logger.warning("Session monitor is already running")
            return
        
        if not settings.ENABLE_AUTO_FINISH_JOB:
            logger.info("Auto-finish job is disabled, skipping session monitor")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._monitor_loop())
        logger.info("Session monitor started")
    
    async def stop(self):
        """Stop the session monitoring background task."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Session monitor stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop - only checks for long-running sessions to abandon."""
        while self.is_running:
            try:
                await self._check_long_running_sessions()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session monitor: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _check_long_running_sessions(self):
        """Check for and abandon very long-running sessions."""
        try:
            async for db in get_db():
                long_sessions = await get_long_running_sessions(
                    db, 
                    hours_limit=self.abandon_hours
                )
                
                for session in long_sessions:
                    try:
                        await abandon_session(
                            db, 
                            session.id, 
                            session.user_id
                        )
                        logger.info(f"Auto-abandoned session {session.id} for user {session.user_id}")
                        
                        # TODO: Send notification to user about abandoned session
                        # await self._send_abandon_notification(session)
                        
                    except Exception as e:
                        logger.error(f"Error abandoning session {session.id}: {e}")
                
                if long_sessions:
                    logger.info(f"Auto-abandoned {len(long_sessions)} long-running sessions")
                
        except Exception as e:
            logger.error(f"Error checking long-running sessions: {e}")

# Global instance
session_monitor = SessionMonitorService()

async def get_session_monitor() -> SessionMonitorService:
    """Get the global session monitor instance."""
    return session_monitor

# Functions to start/stop the monitor (can be called from main.py)
async def start_session_monitor():
    """Start the session monitoring service."""
    monitor = await get_session_monitor()
    await monitor.start()

async def stop_session_monitor():
    """Stop the session monitoring service."""
    monitor = await get_session_monitor()
    await monitor.stop()
