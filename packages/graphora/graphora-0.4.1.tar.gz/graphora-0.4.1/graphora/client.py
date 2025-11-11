"""
Graphora Client

Main client class for interacting with the Graphora API.
"""

import json
import os
import time
import warnings
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

import requests

from graphora.models import (
    OntologyResponse,
    TransformResponse,
    TransformStatus,
    TransformRunStatus,
    MergeInitResponse,
    MergeState,
    GraphResponse,
    DocumentMetadata,
    ChangeLog,
    ResolutionStrategy,
    SaveGraphRequest,
    SaveGraphResponse,
    QualityResults,
    QualityRuleType,
    QualitySeverity,
    ApprovalRequest,
    RejectQualityRequest,
    QualityApprovalResponse,
    QualityRejectionResponse,
    QualityViolationsResponse,
    QualitySummaryResponse,
    QualityDeleteResponse,
    QualityHealthResponse,
    RecentRunsResponse,
    DashboardSummaryResponse,
    DashboardPerformanceResponse,
    DashboardQualityResponse,
)
from graphora.exceptions import GraphoraAPIError, GraphoraClientError
from graphora.utils import get_api_url


class GraphoraClient:
    """
    Client for interacting with the Graphora API.
    
    This client provides methods for all major Graphora API endpoints, including:
    - Ontology management
    - Document transformation
    - Graph merging
    - Graph querying and manipulation
    - Quality validation and approval workflows
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        user_id: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        Initialize a new Graphora client.
        
        Args:
            base_url: Base URL of the Graphora API. If omitted, the client uses the
                `GRAPHORA_API_URL` environment variable or the value derived from
                `graphora.utils.get_api_url()`.
            auth_token: Clerk-issued bearer token for authentication. If not provided,
                the client will read GRAPHORA_AUTH_TOKEN from the environment.
            user_id: Optional user identifier for client-side bookkeeping (not sent automatically)
            timeout: Request timeout in seconds
        """
        resolved_base_url = base_url or os.environ.get("GRAPHORA_API_URL") or get_api_url()
        self.base_url = resolved_base_url.rstrip('/')
        env_token = os.environ.get("GRAPHORA_AUTH_TOKEN")
        self.auth_token = auth_token or env_token
        if not self.auth_token:
            raise ValueError(
                "A Clerk bearer token is required. Provide it via auth_token="
                " or the GRAPHORA_AUTH_TOKEN environment variable."
            )
        if os.environ.get("GRAPHORA_API_KEY") and not auth_token:
            warnings.warn(
                "GRAPHORA_API_KEY is deprecated; use GRAPHORA_AUTH_TOKEN instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.user_id = user_id
        self.timeout = timeout
        self.api_version = "v1"

    @property
    def headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Accept": "application/json",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def _build_url(self, endpoint: str) -> str:
        """Build a full URL for the given endpoint."""
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return f"{self.base_url}/api/{self.api_version}/{endpoint}"

    def _build_system_url(self, path: str) -> str:
        """Build URL for system-level endpoints that are not versioned."""
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_msg = error_data["detail"]
            except (ValueError, json.JSONDecodeError):
                pass
            raise GraphoraAPIError(f"API error: {error_msg}", response.status_code)
        except (ValueError, json.JSONDecodeError):
            raise GraphoraClientError("Invalid JSON response from API")
        except requests.exceptions.RequestException as e:
            raise GraphoraClientError(f"Request failed: {str(e)}")
    
    # Ontology Endpoints
    
    def register_ontology(self, ontology_yaml: str) -> OntologyResponse:
        """
        Register, validate and upload an ontology definition.
        
        Args:
            ontology_yaml: Ontology definition in YAML format
            
        Returns:
            OntologyResponse with the ID of the validated ontology
        """
        url = self._build_url("ontology")
        data = {"text": ontology_yaml}
        response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return OntologyResponse(**result)
    
    def get_ontology(self, ontology_id: str) -> str:
        """
        Retrieve an ontology by ID.
        
        Args:
            ontology_id: ID of the ontology to retrieve
            
        Returns:
            Ontology YAML text
        """
        url = self._build_url(f"ontology/{ontology_id}")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return result.get("text", "")
    
    # Transform Endpoints
    
    def transform(
        self,
        ontology_id: str,
        files: List[Union[str, Path, BinaryIO]],
        metadata: Optional[List[DocumentMetadata]] = None
    ) -> TransformResponse:
        """
        Upload documents for processing.
        
        Args:
            ontology_id: ID of the ontology to use for transformation
            files: List of files to process (paths or file-like objects)
            metadata: Optional metadata for each document
            
        Returns:
            TransformResponse with the ID for tracking progress
        """
        url = self._build_url(f"transform/{ontology_id}/upload")
        
        multipart_files: List[Any] = []
        opened_files: List[BinaryIO] = []
        for i, file in enumerate(files):
            if isinstance(file, (str, Path)):
                path = Path(file)
                filename = path.name
                file_obj = open(path, "rb")
                opened_files.append(file_obj)
            else:
                filename = getattr(file, "name", f"file_{i}")
                file_obj = file

            multipart_files.append(("files", (filename, file_obj)))

        try:
            response = requests.post(
                url,
                files=multipart_files,
                headers=self.headers,
                timeout=self.timeout,
            )
        finally:
            for fh in opened_files:
                try:
                    fh.close()
                except Exception:  # pragma: no cover - best effort cleanup
                    pass

        result = self._handle_response(response)
        return TransformResponse(**result)
    
    def get_transform_status(
        self,
        transform_id: str,
        include_metrics: bool = True
    ) -> TransformStatus:
        """
        Get the status of a transformation.
        
        Args:
            transform_id: ID of the transformation to check
            include_metrics: Whether to include resource metrics
            
        Returns:
            TransformStatus with current progress
        """
        url = self._build_url(f"transform/status/{transform_id}")
        params = {"include_metrics": include_metrics}
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return TransformStatus(**result)
    
    def wait_for_transform(
        self,
        transform_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> TransformStatus:
        """
        Wait for a transformation to complete.
        
        Args:
            transform_id: ID of the transformation to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
            
        Returns:
            Final TransformStatus
            
        Raises:
            GraphoraClientError: If the transformation fails or times out
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_transform_status(transform_id)
            if status.overall_status in (
                TransformRunStatus.COMPLETED,
                TransformRunStatus.FAILED,
            ):
                return status
            time.sleep(poll_interval)
        
        raise GraphoraClientError(f"Transform {transform_id} timed out after {timeout} seconds")
    
    def cleanup_transform(self, transform_id: str) -> bool:
        """
        Clean up transformation data.
        
        Args:
            transform_id: ID of the transformation to clean up
            
        Returns:
            True if cleanup was successful
        """
        url = self._build_url(f"transform/status/{transform_id}/cleanup")
        response = requests.post(url, headers=self.headers, timeout=self.timeout)
        self._handle_response(response)
        return True
    
    def get_transformed_graph(
        self,
        transform_id: str,
        limit: int = 1000,
        skip: int = 0
    ) -> GraphResponse:
        """
        Retrieve graph data by transform ID.
        
        Args:
            transform_id: ID of the transformation
            limit: Maximum number of nodes to return
            skip: Number of nodes to skip for pagination
            
        Returns:
            GraphResponse with nodes and edges
        """
        url = self._build_url(f"graph/{transform_id}")
        params = {"limit": limit, "skip": skip}
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return GraphResponse(**result)
    
    def update_transform_graph(
        self,
        transform_id: str,
        changes: SaveGraphRequest
    ) -> SaveGraphResponse:
        """
        Save bulk modifications to the graph.
        
        Args:
            transform_id: ID of the transformation
            changes: Batch of modifications to apply
            
        Returns:
            SaveGraphResponse with updated graph data
        """
        url = self._build_url(f"graph/{transform_id}")
        payload = changes.model_dump(exclude_none=True)
        response = requests.put(
            url, json=payload, headers=self.headers, timeout=self.timeout
        )
        result = self._handle_response(response)
        return SaveGraphResponse(**result)
    
    # Merge Endpoints
    
    def start_merge(
        self,
        session_id: str,
        transform_id: str,
        merge_id: Optional[str] = None,
    ) -> MergeInitResponse:
        """
        Start a new merge process.
        
        Args:
            session_id: Session ID (ontology ID)
            transform_id: ID of the transformation to merge
            merge_id: Optional custom merge ID
            
        Returns:
            MergeInitResponse with the ID for tracking progress
        """
        url = self._build_url(f"merge/{session_id}/{transform_id}/start")
        params = {}
        if merge_id:
            params["merge_id"] = merge_id
            
        response = requests.post(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return MergeInitResponse(**result)
    
    def get_merge_status(self, merge_id: str) -> MergeState:
        """
        Get the status of a merge process.
        
        Args:
            merge_id: ID of the merge to check
            
        Returns:
            MergeStatus with current progress
        """
        url = self._build_url(f"merge/{merge_id}/status")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        if isinstance(result, str):
            return MergeState(result)
        raise GraphoraClientError(
            f"Unexpected merge status payload for {merge_id}: {result}"
        )
    
    def get_conflicts(self, merge_id: str) -> List[ChangeLog]:
        """
        Get conflicts for a merge process.
        
        Args:
            merge_id: ID of the merge process
            
        Returns:
            List of conflicts requiring resolution
        """
        url = self._build_url(f"merge/{merge_id}/conflicts")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return [ChangeLog(**item) for item in result]
    
    def resolve_conflict(
        self,
        merge_id: str,
        conflict_id: str,
        changed_props: Dict[str, Any],
        resolution: ResolutionStrategy,
        learning_comment: str = ""
    ) -> bool:
        """
        Apply a resolution to a specific conflict.
        
        Args:
            merge_id: ID of the merge process
            conflict_id: ID of the conflict to resolve
            changed_props: Properties that were changed
            resolution: The resolution decision
            learning_comment: Comment on the resolution
            
        Returns:
            True if the resolution was applied successfully
        """
        url = self._build_url(f"merge/{merge_id}/conflicts/{conflict_id}/resolve")
        resolution_value = resolution.value if isinstance(resolution, ResolutionStrategy) else resolution
        data = {
            "changed_props": changed_props,
            "resolution": resolution_value,
            "learning_comment": learning_comment,
        }
        response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return result
    
    def get_merge_statistics(self, merge_id: str) -> Dict[str, Any]:
        """
        Get detailed statistics of a merge operation.
        
        Args:
            merge_id: ID of the merge process
            
        Returns:
            Dictionary of merge statistics
        """
        url = self._build_url(f"merge/statistics/{merge_id}")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        return self._handle_response(response)
    
    def get_merged_graph(self, merge_id: str, transform_id: str) -> GraphResponse:
        """
        Retrieve graph data for a merge process.
        
        Args:
            merge_id: ID of the merge process
            transform_id: ID of the transformation
            
        Returns:
            GraphResponse with nodes and edges
        """
        url = self._build_url(f"merge/graph/{merge_id}/{transform_id}")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return GraphResponse(**result)
    
    # Quality Validation Endpoints
    
    def get_quality_results(self, transform_id: str) -> QualityResults:
        """
        Get quality validation results for a transform.
        
        Args:
            transform_id: ID of the transformation to get quality results for
            
        Returns:
            QualityResults with validation metrics, violations, and scores
        """
        url = self._build_url(f"quality/results/{transform_id}")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return QualityResults(**result)
    
    def approve_quality_results(
        self, 
        transform_id: str, 
        approval_comment: Optional[str] = None
    ) -> QualityApprovalResponse:
        """
        Approve quality validation results and proceed to merge.
        
        Args:
            transform_id: ID of the transformation to approve
            approval_comment: Optional comment about the approval
            
        Returns:
            QualityApprovalResponse confirming the approval
        """
        url = self._build_url(f"quality/approve/{transform_id}")
        data = ApprovalRequest(approval_comment=approval_comment).dict()
        response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return QualityApprovalResponse(**result)
    
    def reject_quality_results(
        self, 
        transform_id: str, 
        rejection_reason: str
    ) -> QualityRejectionResponse:
        """
        Reject quality validation results and stop the process.
        
        Args:
            transform_id: ID of the transformation to reject
            rejection_reason: Required reason for rejecting the results
            
        Returns:
            QualityRejectionResponse confirming the rejection
        """
        url = self._build_url(f"quality/reject/{transform_id}")
        data = RejectQualityRequest(rejection_reason=rejection_reason).dict()
        response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return QualityRejectionResponse(**result)
    
    def get_quality_violations(
        self,
        transform_id: str,
        violation_type: Optional[QualityRuleType] = None,
        severity: Optional[QualitySeverity] = None,
        entity_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> QualityViolationsResponse:
        """
        Get detailed quality violations with filtering and pagination.
        
        Args:
            transform_id: ID of the transformation
            violation_type: Filter by rule type (format, business, etc.)
            severity: Filter by severity level (error, warning, info)
            entity_type: Filter by entity type
            limit: Maximum number of violations to return (1-1000)
            offset: Number of violations to skip for pagination
            
        Returns:
            QualityViolationsResponse with filtered violations
        """
        url = self._build_url(f"quality/violations/{transform_id}")
        params = {
            "limit": min(max(limit, 1), 1000),  # Ensure within bounds
            "offset": max(offset, 0)  # Ensure non-negative
        }
        
        if violation_type:
            params["violation_type"] = violation_type
        if severity:
            params["severity"] = severity
        if entity_type:
            params["entity_type"] = entity_type
            
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return QualityViolationsResponse(**result)
    
    def get_quality_summary(self, limit: int = 10) -> QualitySummaryResponse:
        """
        Get summary of recent quality results for the user.
        
        Args:
            limit: Number of recent results to return (1-50)
            
        Returns:
            QualitySummaryResponse with recent quality result summaries
        """
        url = self._build_url("quality/summary")
        params = {"limit": min(max(limit, 1), 50)}  # Ensure within bounds
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return QualitySummaryResponse(**result)
    
    def delete_quality_results(self, transform_id: str) -> QualityDeleteResponse:
        """
        Delete quality validation results for a transform.
        
        Args:
            transform_id: ID of the transformation to delete results for
            
        Returns:
            QualityDeleteResponse confirming the deletion
        """
        url = self._build_url(f"quality/results/{transform_id}")
        response = requests.delete(url, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return QualityDeleteResponse(**result)
    
    def get_quality_health(self) -> QualityHealthResponse:
        """
        Check the health and availability of the quality validation API.
        
        Returns:
            QualityHealthResponse with health status information
        """
        url = self._build_url("quality/health")
        response = requests.get(url, timeout=self.timeout)  # No auth headers needed for health check
        result = self._handle_response(response)
        return QualityHealthResponse(**result)

    # Dashboard Endpoints

    def get_dashboard_runs(
        self,
        limit: int = 20,
        days: int = 14
    ) -> RecentRunsResponse:
        """Fetch the most recent transform runs with quality and usage context."""

        url = self._build_url("dashboard/runs")
        params = {
            "limit": min(max(limit, 1), 50),
            "days": min(max(days, 1), 90)
        }
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return RecentRunsResponse(**result)

    def get_dashboard_summary(
        self,
        days: int = 14,
        max_runs: int = 200
    ) -> DashboardSummaryResponse:
        """Retrieve aggregated KPI metrics for the dashboard summary header."""

        url = self._build_url("dashboard/summary")
        params = {
            "days": min(max(days, 1), 90),
            "max_runs": min(max(max_runs, 1), 1000)
        }
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return DashboardSummaryResponse(**result)

    def get_dashboard_performance(
        self,
        days: int = 14,
        max_runs: int = 200
    ) -> DashboardPerformanceResponse:
        """Retrieve performance time-series metrics for dashboard charts."""

        url = self._build_url("dashboard/performance")
        params = {
            "days": min(max(days, 1), 90),
            "max_runs": min(max(max_runs, 1), 1000)
        }
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return DashboardPerformanceResponse(**result)

    def get_dashboard_quality(
        self,
        days: int = 14,
        max_runs: int = 200
    ) -> DashboardQualityResponse:
        """Retrieve quality aggregates for the dashboard quality section."""

        url = self._build_url("dashboard/quality")
        params = {
            "days": min(max(days, 1), 90),
            "max_runs": min(max(max_runs, 1), 1000)
        }
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return DashboardQualityResponse(**result)
