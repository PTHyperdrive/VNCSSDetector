"""
VNCSSDetector Web Service - Recordings Router
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.recording import RecordingStatus
from app.models.user import User
from app.schemas.recording import (
    RecordingResponse, RecordingWithNode, AnalysisResultResponse
)
from app.services.node_service import NodeService
from app.services.recording_service import RecordingService
from app.routers.deps import get_current_user, require_operator

router = APIRouter()


@router.get("", response_model=List[RecordingResponse])
async def list_recordings(
    node_id: Optional[int] = None,
    status: Optional[RecordingStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all recordings with optional filtering.
    """
    recordings = await RecordingService.get_recordings(
        db,
        node_id=node_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return recordings


@router.get("/{recording_id}", response_model=RecordingWithNode)
async def get_recording(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific recording by ID with node information.
    """
    recording = await RecordingService.get_recording_by_id(db, recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    node = await NodeService.get_node_by_id(db, recording.node_id)
    
    return RecordingWithNode(
        **recording.__dict__,
        node_name=node.name if node else "Unknown",
        node_uuid=node.uuid if node else "Unknown"
    )


@router.get("/{recording_id}/download")
async def download_recording(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download a recording's QMDL file.
    """
    import os
    
    recording = await RecordingService.get_recording_by_id(db, recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    if not os.path.exists(recording.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording file not found on disk"
        )
    
    return FileResponse(
        path=recording.file_path,
        filename=f"{recording.name}.qmdl",
        media_type="application/octet-stream"
    )


@router.post("/{recording_id}/stop", response_model=RecordingResponse)
async def stop_recording(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator)
):
    """
    Stop an active recording.
    """
    recording = await RecordingService.get_recording_by_id(db, recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    if recording.status != RecordingStatus.RECORDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recording is not active"
        )
    
    updated_recording = await RecordingService.stop_recording(db, recording)
    return updated_recording


@router.post("/{recording_id}/analyze", response_model=RecordingResponse)
async def trigger_analysis(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator)
):
    """
    Trigger analysis on a recording.
    """
    from app.models.recording import AnalysisStatus
    
    recording = await RecordingService.get_recording_by_id(db, recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    if recording.status == RecordingStatus.RECORDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot analyze while recording is active"
        )
    
    # Mark as running analysis
    from app.schemas.recording import RecordingUpdate
    update_data = RecordingUpdate(
        status=RecordingStatus.ANALYZING,
        analysis_status=AnalysisStatus.RUNNING
    )
    updated_recording = await RecordingService.update_recording(db, recording, update_data)
    
    # TODO: Queue actual analysis job
    # In production, this would send a message to a worker queue
    
    return updated_recording


@router.get("/{recording_id}/analysis", response_model=List[AnalysisResultResponse])
async def get_analysis_results(
    recording_id: int,
    event_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get analysis results for a recording.
    """
    from app.models.analysis import EventType
    
    recording = await RecordingService.get_recording_by_id(db, recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    filter_event_type = None
    if event_type:
        try:
            filter_event_type = EventType(event_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type: {event_type}"
            )
    
    results = await RecordingService.get_analysis_results(
        db,
        recording_id=recording_id,
        event_type=filter_event_type
    )
    return results


@router.delete("/{recording_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recording(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator)
):
    """
    Delete a recording and its file.
    """
    recording = await RecordingService.get_recording_by_id(db, recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    if recording.status == RecordingStatus.RECORDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete active recording"
        )
    
    await RecordingService.delete_recording(db, recording)


@router.get("/stats/overview")
async def get_recording_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recording statistics.
    """
    stats = await RecordingService.get_recording_stats(db)
    return stats
