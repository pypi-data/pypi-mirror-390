"""
Queue management commands for MCP Proxy Adapter.

This module provides JSON-RPC commands for managing background jobs
using the queuemgr integration.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""


from typing import Dict, Any

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult
from mcp_proxy_adapter.integrations.queuemgr_integration import (
    QueueManagerIntegration,
    QueueJobBase,
    QueueJobResult,
    QueueJobStatus,
    QueueJobError,
    get_global_queue_manager,
)


class QueueAddJobCommand(Command):
    """Command to add a job to the queue."""

    def __init__(self):
        super().__init__()
        self.name = "queue_add_job"
        self.description = "Add a job to the background queue"
        self.version = "1.0.0"

    def get_schema(self) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "job_type": {
                    "type": "string",
                    "description": "Type of job to add",
                    "enum": ["data_processing", "file_operation", "api_call", "custom", "long_running", "batch_processing", "file_download"]
                },
                "job_id": {
                    "type": "string",
                    "description": "Unique job identifier",
                    "minLength": 1
                },
                "params": {
                    "type": "object",
                    "description": "Job-specific parameters",
                    "properties": {
                        "data": {"type": "object", "description": "Data to process"},
                        "operation": {"type": "string", "description": "Operation type"},
                        "file_path": {"type": "string", "description": "File path for file operations"},
                        "url": {"type": "string", "description": "URL for API calls"},
                        "method": {"type": "string", "description": "HTTP method for API calls"},
                        "headers": {"type": "object", "description": "HTTP headers"},
                        "timeout": {"type": "number", "description": "Job timeout in seconds"},
                        "priority": {"type": "integer", "description": "Job priority (1-10)"},
                        "duration": {"type": "integer", "description": "Duration for long-running jobs (seconds)"},
                        "task_type": {"type": "string", "description": "Type of task for long-running jobs"},
                        "batch_size": {"type": "integer", "description": "Batch size for batch processing jobs"},
                        "items": {"type": "array", "description": "Items to process in batch jobs"},
                        "file_size": {"type": "integer", "description": "File size for download jobs (bytes)"}
                    }
                }
            },
            "required": ["job_type", "job_id", "params"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue add job command."""
        try:
            job_type = params.get("job_type")
            job_id = params.get("job_id")
            job_params = params.get("params", {})

            if not job_type or not job_id:
                raise ValidationError("job_type and job_id are required")

            # Get global queue manager
            queue_manager = await get_global_queue_manager()

            # Map job types to classes
            job_classes = {
                "data_processing": DataProcessingJob,
                "file_operation": FileOperationJob,
                "api_call": ApiCallJob,
                "custom": CustomJob,
                "long_running": LongRunningJob,
                "batch_processing": BatchProcessingJob,
                "file_download": FileDownloadJob,
            }

            if job_type not in job_classes:
                raise ValidationError(f"Unknown job type: {job_type}")

            # Add job to queue
            result = await queue_manager.add_job(
                job_classes[job_type], 
                job_id, 
                job_params
            )

            return SuccessResult(
                data={
                    "message": f"Job {job_id} added successfully",
                    "job_id": job_id,
                    "job_type": job_type,
                    "status": result.status,
                    "description": result.description
                }
            ).to_dict()

        except QueueJobError as e:
            return ErrorResult(
                error_code="QUEUE_JOB_ERROR",
                message=f"Queue job error: {str(e)}",
                details={"job_id": getattr(e, 'job_id', 'unknown')}
            ).to_dict()
        except Exception as e:
            return ErrorResult(
                error_code="INTERNAL_ERROR",
                message=f"Failed to add job: {str(e)}"
            ).to_dict()


class QueueStartJobCommand(Command):
    """Command to start a job in the queue."""

    def __init__(self):
        super().__init__()
        self.name = "queue_start_job"
        self.description = "Start a job in the background queue"
        self.version = "1.0.0"

    def get_schema(self) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "Job identifier to start",
                    "minLength": 1
                }
            },
            "required": ["job_id"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue start job command."""
        try:
            job_id = params.get("job_id")

            if not job_id:
                raise ValidationError("job_id is required")

            # Get global queue manager
            queue_manager = await get_global_queue_manager()

            # Start job
            result = await queue_manager.start_job(job_id)

            return SuccessResult(
                data={
                    "message": f"Job {job_id} started successfully",
                    "job_id": job_id,
                    "status": result.status,
                    "description": result.description
                }
            ).to_dict()

        except QueueJobError as e:
            return ErrorResult(
                error_code="QUEUE_JOB_ERROR",
                message=f"Queue job error: {str(e)}",
                details={"job_id": getattr(e, 'job_id', 'unknown')}
            ).to_dict()
        except Exception as e:
            return ErrorResult(
                error_code="INTERNAL_ERROR",
                message=f"Failed to start job: {str(e)}"
            ).to_dict()


class QueueStopJobCommand(Command):
    """Command to stop a job in the queue."""

    def __init__(self):
        super().__init__()
        self.name = "queue_stop_job"
        self.description = "Stop a running job in the background queue"
        self.version = "1.0.0"

    def get_schema(self) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "Job identifier to stop",
                    "minLength": 1
                }
            },
            "required": ["job_id"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue stop job command."""
        try:
            job_id = params.get("job_id")

            if not job_id:
                raise ValidationError("job_id is required")

            # Get global queue manager
            queue_manager = await get_global_queue_manager()

            # Stop job
            result = await queue_manager.stop_job(job_id)

            return SuccessResult(
                data={
                    "message": f"Job {job_id} stopped successfully",
                    "job_id": job_id,
                    "status": result.status,
                    "description": result.description
                }
            ).to_dict()

        except QueueJobError as e:
            return ErrorResult(
                error_code="QUEUE_JOB_ERROR",
                message=f"Queue job error: {str(e)}",
                details={"job_id": getattr(e, 'job_id', 'unknown')}
            ).to_dict()
        except Exception as e:
            return ErrorResult(
                error_code="INTERNAL_ERROR",
                message=f"Failed to stop job: {str(e)}"
            ).to_dict()


class QueueDeleteJobCommand(Command):
    """Command to delete a job from the queue."""

    def __init__(self):
        super().__init__()
        self.name = "queue_delete_job"
        self.description = "Delete a job from the background queue"
        self.version = "1.0.0"

    def get_schema(self) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "Job identifier to delete",
                    "minLength": 1
                }
            },
            "required": ["job_id"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue delete job command."""
        try:
            job_id = params.get("job_id")

            if not job_id:
                raise ValidationError("job_id is required")

            # Get global queue manager
            queue_manager = await get_global_queue_manager()

            # Delete job
            result = await queue_manager.delete_job(job_id)

            return SuccessResult(
                data={
                    "message": f"Job {job_id} deleted successfully",
                    "job_id": job_id,
                    "status": result.status,
                    "description": result.description
                }
            ).to_dict()

        except QueueJobError as e:
            return ErrorResult(
                error_code="QUEUE_JOB_ERROR",
                message=f"Queue job error: {str(e)}",
                details={"job_id": getattr(e, 'job_id', 'unknown')}
            ).to_dict()
        except Exception as e:
            return ErrorResult(
                error_code="INTERNAL_ERROR",
                message=f"Failed to delete job: {str(e)}"
            ).to_dict()


class QueueGetJobStatusCommand(Command):
    """Command to get the status of a job."""

    def __init__(self):
        super().__init__()
        self.name = "queue_get_job_status"
        self.description = "Get the status and details of a job"
        self.version = "1.0.0"

    def get_schema(self) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "Job identifier to get status for",
                    "minLength": 1
                }
            },
            "required": ["job_id"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue get job status command."""
        try:
            job_id = params.get("job_id")

            if not job_id:
                raise ValidationError("job_id is required")

            # Get global queue manager
            queue_manager = await get_global_queue_manager()

            # Get job status
            result = await queue_manager.get_job_status(job_id)

            return SuccessResult(
                data={
                    "job_id": result.job_id,
                    "status": result.status,
                    "progress": result.progress,
                    "description": result.description,
                    "result": result.result,
                    "error": result.error
                }
            ).to_dict()

        except QueueJobError as e:
            return ErrorResult(
                error_code="QUEUE_JOB_ERROR",
                message=f"Queue job error: {str(e)}",
                details={"job_id": getattr(e, 'job_id', 'unknown')}
            ).to_dict()
        except Exception as e:
            return ErrorResult(
                error_code="INTERNAL_ERROR",
                message=f"Failed to get job status: {str(e)}"
            ).to_dict()


class QueueListJobsCommand(Command):
    """Command to list all jobs in the queue."""

    def __init__(self):
        super().__init__()
        self.name = "queue_list_jobs"
        self.description = "List all jobs in the background queue"
        self.version = "1.0.0"

    def get_schema(self) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "status_filter": {
                    "type": "string",
                    "description": "Filter jobs by status",
                    "enum": ["pending", "running", "completed", "failed", "stopped", "deleted"]
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of jobs to return",
                    "minimum": 1,
                    "maximum": 1000
                }
            }
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue list jobs command."""
        try:
            status_filter = params.get("status_filter")
            limit = params.get("limit", 100)

            # Get global queue manager
            queue_manager = await get_global_queue_manager()

            # List jobs
            jobs = await queue_manager.list_jobs()

            # Apply filters
            if status_filter:
                jobs = [job for job in jobs if job.status == status_filter]

            # Apply limit
            if limit and len(jobs) > limit:
                jobs = jobs[:limit]

            # Convert to dict format
            jobs_data = []
            for job in jobs:
                jobs_data.append({
                    "job_id": job.job_id,
                    "status": job.status,
                    "progress": job.progress,
                    "description": job.description,
                    "has_result": bool(job.result),
                    "has_error": bool(job.error)
                })

            return SuccessResult(
                data={
                    "jobs": jobs_data,
                    "total_count": len(jobs_data),
                    "status_filter": status_filter,
                    "limit": limit
                }
            ).to_dict()

        except QueueJobError as e:
            return ErrorResult(
                error_code="QUEUE_JOB_ERROR",
                message=f"Queue job error: {str(e)}",
                details={"job_id": getattr(e, 'job_id', 'unknown')}
            ).to_dict()
        except Exception as e:
            return ErrorResult(
                error_code="INTERNAL_ERROR",
                message=f"Failed to list jobs: {str(e)}"
            ).to_dict()


class QueueHealthCommand(Command):
    """Command to check queue system health."""

    def __init__(self):
        super().__init__()
        self.name = "queue_health"
        self.description = "Check the health status of the queue system"
        self.version = "1.0.0"

    def get_schema(self) -> Dict[str, Any]:
        """Get command schema."""
        return {"type": "object", "properties": {}}

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute queue health command."""
        try:
            # Get global queue manager
            queue_manager = await get_global_queue_manager()

            # Get health information
            health = await queue_manager.get_queue_health()

            return SuccessResult(data=health).to_dict()

        except Exception as e:
            return ErrorResult(
                error_code="INTERNAL_ERROR",
                message=f"Failed to check queue health: {str(e)}"
            ).to_dict()


# Example job classes for demonstration
class DataProcessingJob(QueueJobBase):
    """Example data processing job."""

    def run(self) -> None:
        """Execute data processing job."""
        import time
        import json

        self.logger.info(f"DataProcessingJob {self.job_id}: Starting data processing")
        
        # Simulate processing
        data = self.mcp_params.get("data", {})
        operation = self.mcp_params.get("operation", "process")
        
        time.sleep(2)  # Simulate work
        
        result = {
            "job_id": self.job_id,
            "operation": operation,
            "processed_at": time.time(),
            "data_size": len(json.dumps(data)),
            "status": "completed"
        }
        
        self.set_mcp_result(result)


class FileOperationJob(QueueJobBase):
    """Example file operation job."""

    def run(self) -> None:
        """Execute file operation job."""
        import os
        import time

        self.logger.info(f"FileOperationJob {self.job_id}: Starting file operation")
        
        file_path = self.mcp_params.get("file_path", "")
        operation = self.mcp_params.get("operation", "read")
        
        try:
            if operation == "read" and os.path.exists(file_path):
                with open(file_path, "r") as f:
                    content = f.read()
                
                result = {
                    "job_id": self.job_id,
                    "operation": operation,
                    "file_path": file_path,
                    "file_size": len(content),
                    "status": "completed"
                }
            else:
                result = {
                    "job_id": self.job_id,
                    "operation": operation,
                    "file_path": file_path,
                    "error": f"File not found or invalid operation: {operation}",
                    "status": "failed"
                }
            
            self.set_mcp_result(result, result["status"])
            
        except Exception as e:
            self.set_mcp_error(f"File operation failed: {str(e)}")


class ApiCallJob(QueueJobBase):
    """Example API call job."""

    def run(self) -> None:
        """Execute API call job."""
        import requests
        import time

        self.logger.info(f"ApiCallJob {self.job_id}: Starting API call")
        
        url = self.mcp_params.get("url", "")
        method = self.mcp_params.get("method", "GET")
        headers = self.mcp_params.get("headers", {})
        timeout = self.mcp_params.get("timeout", 30)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout
            )
            
            result = {
                "job_id": self.job_id,
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "response_size": len(response.content),
                "status": "completed"
            }
            
            self.set_mcp_result(result)
            
        except Exception as e:
            self.set_mcp_error(f"API call failed: {str(e)}")


class CustomJob(QueueJobBase):
    """Example custom job."""

    def run(self) -> None:
        """Execute custom job."""
        import time

        self.logger.info(f"CustomJob {self.job_id}: Starting custom job")
        
        # Custom job logic here
        time.sleep(1)  # Simulate work
        
        result = {
            "job_id": self.job_id,
            "custom_data": self.mcp_params.get("custom_data", {}),
            "status": "completed"
        }
        
        self.set_mcp_result(result)


class LongRunningJob(QueueJobBase):
    """Example long-running job with progress updates."""
    
    def run(self) -> None:
        """Execute long-running job with progress updates."""
        import time
        import random
        
        self.logger.info(f"LongRunningJob {self.job_id}: Starting long-running job")
        
        duration = self.mcp_params.get("duration", 10)  # Default 10 seconds
        task_type = self.mcp_params.get("task_type", "data_processing")
        
        self.set_status("running")
        self.set_description(f"Processing {task_type} task...")
        
        # Simulate long-running work with progress updates
        for i in range(duration):
            # Update progress
            progress = int((i + 1) / duration * 100)
            self.set_progress(progress)
            self.set_description(f"Processing {task_type} task... {progress}% complete")
            
            # Simulate work
            time.sleep(1)
            
            # Simulate occasional errors (5% chance)
            if random.random() < 0.05:
                self.set_mcp_error(f"Simulated error at {progress}%", "failed")
                return
        
        # Complete successfully
        result = {
            "job_id": self.job_id,
            "task_type": task_type,
            "duration": duration,
            "completed_at": time.time(),
            "status": "completed"
        }
        
        self.set_mcp_result(result)


class BatchProcessingJob(QueueJobBase):
    """Example batch processing job."""
    
    def run(self) -> None:
        """Execute batch processing job."""
        import time
        import random
        
        self.logger.info(f"BatchProcessingJob {self.job_id}: Starting batch processing")
        
        batch_size = self.mcp_params.get("batch_size", 100)
        items = self.mcp_params.get("items", [])
        
        self.set_status("running")
        self.set_description(f"Processing batch of {len(items)} items...")
        
        processed_items = []
        
        for i, item in enumerate(items):
            # Update progress
            progress = int((i + 1) / len(items) * 100)
            self.set_progress(progress)
            self.set_description(f"Processing item {i+1}/{len(items)}... {progress}% complete")
            
            # Simulate processing each item
            time.sleep(0.1)  # 100ms per item
            
            # Simulate processing result
            processed_item = {
                "original": item,
                "processed": f"processed_{item}",
                "timestamp": time.time()
            }
            processed_items.append(processed_item)
            
            # Simulate occasional processing errors (2% chance)
            if random.random() < 0.02:
                self.set_mcp_error(f"Processing failed at item {i+1}: {item}", "failed")
                return
        
        # Complete successfully
        result = {
            "job_id": self.job_id,
            "batch_size": batch_size,
            "processed_count": len(processed_items),
            "processed_items": processed_items,
            "completed_at": time.time(),
            "status": "completed"
        }
        
        self.set_mcp_result(result)


class FileDownloadJob(QueueJobBase):
    """Example file download job with progress tracking."""
    
    def run(self) -> None:
        """Execute file download job."""
        import time
        import random
        
        self.logger.info(f"FileDownloadJob {self.job_id}: Starting file download")
        
        url = self.mcp_params.get("url", "https://example.com/file.zip")
        file_size = self.mcp_params.get("file_size", 1024 * 1024)  # Default 1MB
        
        self.set_status("running")
        self.set_description(f"Downloading {url}...")
        
        # Simulate download with progress updates
        downloaded = 0
        chunk_size = 64 * 1024  # 64KB chunks
        
        while downloaded < file_size:
            # Simulate download chunk
            chunk = min(chunk_size, file_size - downloaded)
            time.sleep(0.1)  # Simulate network delay
            
            downloaded += chunk
            progress = int(downloaded / file_size * 100)
            
            self.set_progress(progress)
            self.set_description(f"Downloading {url}... {progress}% complete ({downloaded}/{file_size} bytes)")
            
            # Simulate occasional network errors (3% chance)
            if random.random() < 0.03:
                self.set_mcp_error(f"Network error during download at {progress}%", "failed")
                return
        
        # Complete successfully
        result = {
            "job_id": self.job_id,
            "url": url,
            "file_size": file_size,
            "downloaded_bytes": downloaded,
            "completed_at": time.time(),
            "status": "completed"
        }
        
        self.set_mcp_result(result)
