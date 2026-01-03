"""
VNCSSDetector Web Service - Recording Service
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.recording import Recording, RecordingStatus, AnalysisStatus
from app.models.analysis import AnalysisResult, EventType
from app.schemas.recording import RecordingCreate, RecordingUpdate

settings = get_settings()


class RecordingService:
    """Service for recording management operations."""
    
    @staticmethod
    def get_recording_path(node_uuid: str, recording_name: str) -> str:
        """Generate the file path for a recording."""
        base_path = Path(settings.recordings_path)
        node_path = base_path / node_uuid
        return str(node_path / f"{recording_name}.qmdl")
    
    @staticmethod
    async def ensure_recording_directory(node_uuid: str) -> Path:
        """Ensure the recording directory exists for a node."""
        base_path = Path(settings.recordings_path)
        node_path = base_path / node_uuid
        node_path.mkdir(parents=True, exist_ok=True)
        return node_path
    
    @staticmethod
    async def create_recording(
        db: AsyncSession,
        node_id: int,
        node_uuid: str,
        recording_name: str
    ) -> Recording:
        """Create a new recording entry."""
        # Ensure directory exists
        await RecordingService.ensure_recording_directory(node_uuid)
        
        file_path = RecordingService.get_recording_path(node_uuid, recording_name)
        
        recording = Recording(
            node_id=node_id,
            name=recording_name,
            file_path=file_path,
            status=RecordingStatus.RECORDING,
            started_at=datetime.utcnow()
        )
        db.add(recording)
        await db.flush()
        await db.refresh(recording)
        
        return recording
    
    @staticmethod
    async def get_recording_by_id(
        db: AsyncSession, 
        recording_id: int
    ) -> Optional[Recording]:
        """Get a recording by ID."""
        result = await db.execute(
            select(Recording).where(Recording.id == recording_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_recordings(
        db: AsyncSession,
        node_id: Optional[int] = None,
        status: Optional[RecordingStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Recording]:
        """Get recordings with optional filtering."""
        query = select(Recording)
        
        if node_id:
            query = query.where(Recording.node_id == node_id)
        if status:
            query = query.where(Recording.status == status)
            
        query = query.offset(skip).limit(limit).order_by(Recording.started_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_recording(
        db: AsyncSession,
        recording: Recording,
        update_data: RecordingUpdate
    ) -> Recording:
        """Update a recording."""
        data = update_data.model_dump(exclude_unset=True)
        
        for field, value in data.items():
            setattr(recording, field, value)
        
        await db.flush()
        await db.refresh(recording)
        return recording
    
    @staticmethod
    async def stop_recording(db: AsyncSession, recording: Recording) -> Recording:
        """Stop a recording."""
        recording.status = RecordingStatus.STOPPED
        recording.stopped_at = datetime.utcnow()
        
        # Update file size if file exists
        if os.path.exists(recording.file_path):
            recording.file_size_bytes = os.path.getsize(recording.file_path)
        
        await db.flush()
        await db.refresh(recording)
        return recording
    
    @staticmethod
    async def delete_recording(db: AsyncSession, recording: Recording) -> None:
        """Delete a recording and its file."""
        # Delete the file if it exists
        if os.path.exists(recording.file_path):
            os.remove(recording.file_path)
        
        await db.delete(recording)
        await db.flush()
    
    @staticmethod
    async def get_active_recording(
        db: AsyncSession, 
        node_id: int
    ) -> Optional[Recording]:
        """Get the active recording for a node."""
        result = await db.execute(
            select(Recording)
            .where(Recording.node_id == node_id)
            .where(Recording.status == RecordingStatus.RECORDING)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def add_analysis_result(
        db: AsyncSession,
        recording_id: int,
        event_type: EventType,
        analyzer_name: str,
        message: str,
        details: Optional[dict] = None,
        timestamp: Optional[datetime] = None
    ) -> AnalysisResult:
        """Add an analysis result to a recording."""
        result = AnalysisResult(
            recording_id=recording_id,
            timestamp=timestamp or datetime.utcnow(),
            event_type=event_type,
            analyzer_name=analyzer_name,
            message=message,
            details=details
        )
        db.add(result)
        await db.flush()
        await db.refresh(result)
        
        # Update warning count if applicable
        if event_type in [EventType.WARNING, EventType.CRITICAL]:
            recording = await RecordingService.get_recording_by_id(db, recording_id)
            if recording:
                recording.warning_count += 1
                await db.flush()
        
        return result
    
    @staticmethod
    async def get_analysis_results(
        db: AsyncSession,
        recording_id: int,
        event_type: Optional[EventType] = None
    ) -> List[AnalysisResult]:
        """Get analysis results for a recording."""
        query = select(AnalysisResult).where(
            AnalysisResult.recording_id == recording_id
        )
        
        if event_type:
            query = query.where(AnalysisResult.event_type == event_type)
            
        query = query.order_by(AnalysisResult.timestamp)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_recording_stats(db: AsyncSession) -> dict:
        """Get recording statistics."""
        # Total recordings
        total_result = await db.execute(select(func.count(Recording.id)))
        total = total_result.scalar() or 0
        
        # Active recordings
        active_result = await db.execute(
            select(func.count(Recording.id))
            .where(Recording.status == RecordingStatus.RECORDING)
        )
        active = active_result.scalar() or 0
        
        # Total size
        size_result = await db.execute(
            select(func.sum(Recording.file_size_bytes))
        )
        total_size = size_result.scalar() or 0
        
        # Total warnings
        warnings_result = await db.execute(
            select(func.sum(Recording.warning_count))
        )
        total_warnings = warnings_result.scalar() or 0
        
        return {
            "total": total,
            "active": active,
            "total_size_bytes": total_size,
            "total_warnings": total_warnings
        }
