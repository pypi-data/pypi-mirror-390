"""
Queue Manager Integration for MCP Proxy Adapter.

This module provides integration between mcp_proxy_adapter and queuemgr
for managing background jobs and task queues.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, Type, List

try:
    from queuemgr.jobs.base import QueueJobBase as QueuemgrJobBase
    from queuemgr.core.types import JobStatus as QueuemgrJobStatus
    from queuemgr.exceptions import (
        QueueManagerError,
        JobNotFoundError,
        JobAlreadyExistsError,
        InvalidJobStateError,
        JobExecutionError,
        ProcessControlError,
        ValidationError as QueuemgrValidationError,
        TimeoutError as QueuemgrTimeoutError,
    )
    QUEUEMGR_AVAILABLE = True
except ImportError as e:
    # Fallback for when queuemgr is not available
    QUEUEMGR_AVAILABLE = False
    QueuemgrJobBase = object
    QueuemgrJobStatus = str
    QueueManagerError = Exception
    JobNotFoundError = Exception
    JobAlreadyExistsError = Exception
    InvalidJobStateError = Exception
    JobExecutionError = Exception
    ProcessControlError = Exception
    QueuemgrValidationError = Exception
    QueuemgrTimeoutError = Exception

from mcp_proxy_adapter.core.logging import get_global_logger
from mcp_proxy_adapter.core.errors import MicroserviceError, ValidationError


class QueueJobStatus:
    """Job status constants for queue integration."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
    DELETED = "deleted"


class QueueJobResult:
    """Result of a queue job execution."""
    
    def __init__(
        self,
        job_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        progress: int = 0,
        description: str = "",
    ):
        """
        Initialize queue job result.
        
        Args:
            job_id: Unique job identifier
            status: Job status
            result: Job result data
            error: Error message if failed
            progress: Progress percentage (0-100)
            description: Job description
        """
        self.job_id = job_id
        self.status = status
        self.result = result or {}
        self.error = error
        self.progress = max(0, min(100, progress))
        self.description = description


class QueueJobError(Exception):
    """Exception raised for queue job errors."""
    
    def __init__(self, job_id: str, message: str, original_error: Optional[Exception] = None):
        """
        Initialize queue job error.
        
        Args:
            job_id: Job identifier that failed
            message: Error message
            original_error: Original exception that caused the error
        """
        super().__init__(f"Job {job_id}: {message}")
        self.job_id = job_id
        self.original_error = original_error


class QueueJobBase(QueuemgrJobBase):
    """
    Base class for MCP Proxy Adapter queue jobs.
    
    This class extends the queuemgr QueueJobBase to provide
    MCP-specific functionality and error handling.
    """
    
    def __init__(self, job_id: str, params: Dict[str, Any]):
        """
        Initialize MCP queue job.
        
        Args:
            job_id: Unique job identifier
            params: Job parameters
        """
        if not QUEUEMGR_AVAILABLE:
            raise MicroserviceError(
                "queuemgr is not available. Install it with: pip install queuemgr>=1.0.5"
            )
        
        super().__init__(job_id, params)
        self.logger = get_global_logger()
        self.mcp_params = params
        
        


class QueueManagerIntegration:
    """
    Queue Manager Integration for MCP Proxy Adapter.
    
    This class provides a high-level interface for managing
    background jobs using the queuemgr system.
    """
    
    def __init__(
        self,
        registry_path: str = "mcp_queue_registry.jsonl",
        shutdown_timeout: float = 30.0,
        max_concurrent_jobs: int = 10,
    ):
        """
        Initialize queue manager integration.
        
        Args:
            registry_path: Path to the queue registry file
            shutdown_timeout: Timeout for graceful shutdown
            max_concurrent_jobs: Maximum number of concurrent jobs
        """
        if not QUEUEMGR_AVAILABLE:
            raise MicroserviceError(
                "queuemgr is not available. Install it with: pip install queuemgr>=1.0.5"
            )
        
        self.registry_path = registry_path
        self.shutdown_timeout = shutdown_timeout
        self.max_concurrent_jobs = max_concurrent_jobs
        self.logger = get_global_logger()
        self._queue_system: Optional[AsyncQueueSystem] = None
        self._is_running = False
        
    async def start(self) -> None:
        """Start the queue manager integration."""
        if self._is_running:
            self.logger.warning("Queue manager integration is already running")
            return
            
        try:
            self._queue_system = AsyncQueueSystem(
                registry_path=self.registry_path,
                shutdown_timeout=self.shutdown_timeout,
            )
            await self._queue_system.start()
            self._is_running = True
            self.logger.info("✅ Queue manager integration started")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start queue manager integration: {e}")
            raise MicroserviceError(f"Failed to start queue manager: {str(e)}")
    
    async def stop(self) -> None:
        """Stop the queue manager integration."""
        if not self._is_running:
            self.logger.warning("Queue manager integration is not running")
            return
            
        try:
            if self._queue_system:
                await self._queue_system.stop()
            self._is_running = False
            self.logger.info("✅ Queue manager integration stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop queue manager integration: {e}")
            raise MicroserviceError(f"Failed to stop queue manager: {str(e)}")
    
    def is_running(self) -> bool:
        """Check if the queue manager integration is running."""
        return self._is_running and self._queue_system is not None
    
    async def add_job(
        self,
        job_class: Type[QueueJobBase],
        job_id: str,
        params: Dict[str, Any],
    ) -> QueueJobResult:
        """
        Add a job to the queue.
        
        Args:
            job_class: Job class to instantiate
            job_id: Unique job identifier
            params: Job parameters
            
        Returns:
            QueueJobResult with job information
            
        Raises:
            QueueJobError: If job cannot be added
        """
        if not self.is_running():
            raise QueueJobError(job_id, "Queue manager is not running")
        
        try:
            await self._queue_system.add_job(job_class, job_id, params)
            return QueueJobResult(
                job_id=job_id,
                status=QueueJobStatus.PENDING,
                description="Job added to queue"
            )
            
        except JobAlreadyExistsError as e:
            raise QueueJobError(job_id, f"Job already exists: {str(e)}", e)
        except QueuemgrValidationError as e:
            raise QueueJobError(job_id, f"Invalid job parameters: {str(e)}", e)
        except Exception as e:
            raise QueueJobError(job_id, f"Failed to add job: {str(e)}", e)
    
    async def start_job(self, job_id: str) -> QueueJobResult:
        """
        Start a job in the queue.
        
        Args:
            job_id: Job identifier to start
            
        Returns:
            QueueJobResult with job status
            
        Raises:
            QueueJobError: If job cannot be started
        """
        if not self.is_running():
            raise QueueJobError(job_id, "Queue manager is not running")
        
        try:
            await self._queue_system.start_job(job_id)
            return QueueJobResult(
                job_id=job_id,
                status=QueueJobStatus.RUNNING,
                description="Job started"
            )
            
        except JobNotFoundError as e:
            raise QueueJobError(job_id, f"Job not found: {str(e)}", e)
        except InvalidJobStateError as e:
            raise QueueJobError(job_id, f"Invalid job state: {str(e)}", e)
        except Exception as e:
            raise QueueJobError(job_id, f"Failed to start job: {str(e)}", e)
    
    async def stop_job(self, job_id: str) -> QueueJobResult:
        """
        Stop a job in the queue.
        
        Args:
            job_id: Job identifier to stop
            
        Returns:
            QueueJobResult with job status
            
        Raises:
            QueueJobError: If job cannot be stopped
        """
        if not self.is_running():
            raise QueueJobError(job_id, "Queue manager is not running")
        
        try:
            await self._queue_system.stop_job(job_id)
            return QueueJobResult(
                job_id=job_id,
                status=QueueJobStatus.STOPPED,
                description="Job stopped"
            )
            
        except JobNotFoundError as e:
            raise QueueJobError(job_id, f"Job not found: {str(e)}", e)
        except ProcessControlError as e:
            raise QueueJobError(job_id, f"Process control error: {str(e)}", e)
        except Exception as e:
            raise QueueJobError(job_id, f"Failed to stop job: {str(e)}", e)
    
    async def delete_job(self, job_id: str) -> QueueJobResult:
        """
        Delete a job from the queue.
        
        Args:
            job_id: Job identifier to delete
            
        Returns:
            QueueJobResult with job status
            
        Raises:
            QueueJobError: If job cannot be deleted
        """
        if not self.is_running():
            raise QueueJobError(job_id, "Queue manager is not running")
        
        try:
            await self._queue_system.delete_job(job_id)
            return QueueJobResult(
                job_id=job_id,
                status=QueueJobStatus.DELETED,
                description="Job deleted"
            )
            
        except JobNotFoundError as e:
            raise QueueJobError(job_id, f"Job not found: {str(e)}", e)
        except Exception as e:
            raise QueueJobError(job_id, f"Failed to delete job: {str(e)}", e)
    
    async def get_job_status(self, job_id: str) -> QueueJobResult:
        """
        Get the status of a job.
        
        Args:
            job_id: Job identifier to get status for
            
        Returns:
            QueueJobResult with job status and information
            
        Raises:
            QueueJobError: If job status cannot be retrieved
        """
        if not self.is_running():
            raise QueueJobError(job_id, "Queue manager is not running")
        
        try:
            status_data = await self._queue_system.get_job_status(job_id)
            
            # Convert queuemgr status to MCP status
            mcp_status = self._convert_status(status_data.get("status", "unknown"))
            
            return QueueJobResult(
                job_id=job_id,
                status=mcp_status,
                result=status_data.get("result", {}),
                error=status_data.get("error"),
                progress=status_data.get("progress", 0),
                description=status_data.get("description", ""),
            )
            
        except JobNotFoundError as e:
            raise QueueJobError(job_id, f"Job not found: {str(e)}", e)
        except Exception as e:
            raise QueueJobError(job_id, f"Failed to get job status: {str(e)}", e)
    
    async def list_jobs(self) -> List[QueueJobResult]:
        """
        List all jobs in the queue.
        
        Returns:
            List of QueueJobResult objects
            
        Raises:
            QueueJobError: If jobs cannot be listed
        """
        if not self.is_running():
            raise QueueJobError("", "Queue manager is not running")
        
        try:
            jobs_data = await self._queue_system.list_jobs()
            
            results = []
            for job_data in jobs_data:
                mcp_status = self._convert_status(job_data.get("status", "unknown"))
                results.append(QueueJobResult(
                    job_id=job_data.get("job_id", "unknown"),
                    status=mcp_status,
                    result=job_data.get("result", {}),
                    error=job_data.get("error"),
                    progress=job_data.get("progress", 0),
                    description=job_data.get("description", ""),
                ))
            
            return results
            
        except Exception as e:
            raise QueueJobError("", f"Failed to list jobs: {str(e)}", e)
    
    
    def _convert_status(self, queuemgr_status: str) -> str:
        """
        Convert queuemgr status to MCP status.
        
        Args:
            queuemgr_status: Status from queuemgr
            
        Returns:
            MCP-compatible status
        """
        status_mapping = {
            "pending": QueueJobStatus.PENDING,
            "running": QueueJobStatus.RUNNING,
            "completed": QueueJobStatus.COMPLETED,
            "failed": QueueJobStatus.FAILED,
            "stopped": QueueJobStatus.STOPPED,
            "deleted": QueueJobStatus.DELETED,
        }
        
        return status_mapping.get(queuemgr_status.lower(), QueueJobStatus.PENDING)


# Global queue manager instance
_global_queue_manager: Optional[QueueManagerIntegration] = None


async def get_global_queue_manager() -> QueueManagerIntegration:
    """
    Get global queue manager instance, initializing it if necessary.

    Returns:
        QueueManagerIntegration instance

    Raises:
        QueueJobError: If queue manager cannot be initialized
    """
    global _global_queue_manager
    
    if _global_queue_manager is None:
        # Initialize with default configuration
        config = {
            "queue_manager": {
                "backend": "memory",  # Default to in-memory for simplicity
                "max_workers": 4,
            }
        }
        _global_queue_manager = QueueManagerIntegration(config)
        await _global_queue_manager.initialize()
    
    return _global_queue_manager






