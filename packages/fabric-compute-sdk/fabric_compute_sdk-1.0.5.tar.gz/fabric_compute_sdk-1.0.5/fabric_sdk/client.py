"""
Fabric SDK Client - Main interface for interacting with Fabric API
"""

import requests
import time
from typing import Dict, Any, Optional, List
from .exceptions import (
    AuthenticationError,
    JobSubmissionError,
    InsufficientCreditsError,
    JobTimeoutError,
    NetworkError
)
from .types import Job, Node, CreditBalance, JobResult


class FabricClient:
    """
    Fabric SDK Client for programmatic job submission
    
    Example:
        >>> client = FabricClient(
        ...     api_url="https://api.fabric.carmel.so",
        ...     email="user@example.com",
        ...     password="password"
        ... )
        >>> job = client.submit_job("pytorch_cnn", params={...})
        >>> result = client.wait_for_job(job['id'])
    """
    
    def __init__(
        self,
        api_url: str,
        email: str,
        password: str,
        auto_login: bool = True,
        timeout: int = 30
    ):
        """
        Initialize Fabric client
        
        Args:
            api_url: Fabric API base URL (e.g., "https://api.fabric.carmel.so")
            email: User email
            password: User password
            auto_login: Automatically login on initialization
            timeout: Default request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.email = email
        self.password = password
        self.timeout = timeout
        self.token: Optional[str] = None
        
        if auto_login:
            self.login()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        auth_required: bool = True
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling and retry logic"""
        url = f"{self.api_url}{endpoint}"
        headers = {}
        
        if auth_required:
            if not self.token:
                raise AuthenticationError("Not authenticated. Call login() first.")
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed or token expired")
            elif response.status_code == 403:
                raise AuthenticationError("Access forbidden")
            elif response.status_code == 400:
                error_data = response.json()
                if "insufficient credits" in str(error_data).lower():
                    raise InsufficientCreditsError(f"Insufficient credits: {error_data}")
                raise JobSubmissionError(f"Bad request: {error_data}")
            elif response.status_code >= 400:
                raise NetworkError(f"HTTP {response.status_code}: {response.text}")
            
            return response.json()
        
        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {e}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {e}")
    
    def login(self) -> str:
        """
        Authenticate and obtain access token
        
        Returns:
            Access token
            
        Raises:
            AuthenticationError: If login fails
        """
        try:
            response = self._make_request(
                'POST',
                '/api/auth/login',
                data={'email': self.email, 'password': self.password},
                auth_required=False
            )
            self.token = response.get('access_token')
            return self.token
        except Exception as e:
            raise AuthenticationError(f"Login failed: {e}")
    
    def get_credit_balance(self) -> CreditBalance:
        """
        Get current credit balance
        
        Returns:
            Credit balance object
        """
        return self._make_request('GET', '/api/payment/balance')
    
    def list_nodes(self, status: Optional[str] = None) -> List[Node]:
        """
        List available compute nodes
        
        Args:
            status: Filter by node status (active, inactive, busy)
            
        Returns:
            List of nodes
        """
        params = {'status': status} if status else None
        return self._make_request('GET', '/api/nodes', params=params)
    
    def submit_job(
        self,
        workload_type: str,
        params: Dict[str, Any],
        input_file_url: Optional[str] = None,
        requirements: Optional[Dict[str, Any]] = None,
        job_name: Optional[str] = None,
        max_runtime_minutes: Optional[int] = None,
        budget_cap_usd: Optional[float] = None
    ) -> Job:
        """
        Submit a job to the Fabric network
        
        Args:
            workload_type: Type of workload (e.g., "llm_inference", "video_transcode")
            params: Workload-specific parameters
            input_file_url: URL to input file for media processing jobs (optional)
            requirements: Hardware requirements (optional)
                - min_cpu_cores: Minimum CPU cores
                - min_ram_gb: Minimum RAM in GB
                - gpu_required: Whether GPU is required
                - min_gpu_memory_gb: Minimum GPU memory in GB
            job_name: User-friendly identifier for the job (optional)
            max_runtime_minutes: Maximum runtime in minutes (optional, default: 30)
            budget_cap_usd: Maximum budget in USD (optional, job rejected if cost exceeds)
        
        Returns:
            Created job object
            
        Raises:
            JobSubmissionError: If submission fails
            InsufficientCreditsError: If insufficient credits
        """
        # Prepare job parameters
        job_params = params.copy()
        if requirements:
            job_params['requirements'] = requirements
        
        payload = {
            'job_type': workload_type,
            'params': job_params
        }
        
        # Add optional fields if provided
        if input_file_url:
            payload['input_file_url'] = input_file_url
        if job_name:
            payload['job_name'] = job_name
        if max_runtime_minutes:
            payload['max_runtime_minutes'] = max_runtime_minutes
        if budget_cap_usd is not None:
            payload['budget_cap_usd'] = budget_cap_usd
        
        try:
            job_data = self._make_request('POST', '/api/jobs/submit', data=payload)
            
            # Check for capacity warning
            if job_data.get('warning'):
                print(f"⚠️  Warning: {job_data['warning'].get('message')}")
                if job_data['warning'].get('suggestions'):
                    print("Suggestions:")
                    for suggestion in job_data['warning']['suggestions']:
                        print(f"  - {suggestion}")
            
            return job_data
        except Exception as e:
            raise JobSubmissionError(f"Job submission failed: {e}")
    
    def get_job(self, job_id: str) -> Job:
        """
        Get job details
        
        Args:
            job_id: Job ID
            
        Returns:
            Job object
        """
        # Use /optimized endpoint to get all jobs, then filter for the specific job
        jobs = self._make_request('GET', '/api/jobs/optimized', params={'limit': 100})
        
        for job in jobs:
            if job['id'] == job_id:
                return job
        
        # Job not found in user's jobs
        raise JobSubmissionError(f"Job {job_id} not found in your jobs")
    
    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        """
        Get job results after completion
        
        Args:
            job_id: Job ID
            
        Returns:
            Dictionary with:
            - success: Whether job completed successfully
            - result: The actual computation result (if success=True)
            - error_message: Error message (if success=False)
            - execution_time: Job execution time in seconds
            - node_id: ID of node that executed the job
            - cost: Actual cost of the job
            
        Raises:
            JobSubmissionError: If job not found or still running
            
        Example:
            >>> result = client.get_job_result(job['id'])
            >>> if result['success']:
            ...     print("Result:", result['result'])
            ...     print("Cost: $", result['cost'])
        """
        # First check if job exists and is completed
        job = self.get_job(job_id)
        
        if job['status'] in ['queued', 'executing']:
            raise JobSubmissionError(
                f"Job is still {job['status']}. Wait for completion before fetching results."
            )
        
        if job['status'] == 'failed':
            return {
                'success': False,
                'result': None,
                'error_message': job.get('error_message', 'Job failed with unknown error'),
                'execution_time': job.get('duration_seconds', 0),
                'node_id': job.get('assigned_node_id'),
                'cost': job.get('actual_cost', 0)
            }
        
        # Fetch results from results endpoint
        try:
            response = self._make_request('GET', f'/api/jobs/{job_id}/results')
            
            return {
                'success': True,
                'result': response.get('result'),
                'error_message': None,
                'execution_time': response.get('execution_time', job.get('duration_seconds', 0)),
                'node_id': response.get('node_id', job.get('assigned_node_id')),
                'cost': job.get('actual_cost', 0)
            }
        except Exception as e:
            # If results endpoint fails, return job data
            return {
                'success': job['status'] == 'completed',
                'result': None,
                'error_message': str(e),
                'execution_time': job.get('duration_seconds', 0),
                'node_id': job.get('assigned_node_id'),
                'cost': job.get('actual_cost', 0)
            }
    
    def wait_for_job(
        self,
        job_id: str,
        timeout: int = 600,
        poll_interval: int = 5
    ) -> JobResult:
        """
        Wait for job to complete
        
        Args:
            job_id: Job ID
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            Job result with metadata
            
        Raises:
            JobTimeoutError: If job doesn't complete within timeout
        """
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > timeout:
                raise JobTimeoutError(
                    f"Job {job_id} did not complete within {timeout}s"
                )
            
            job = self.get_job(job_id)
            status = job['status']
            
            if status == 'completed':
                # Get result from /results endpoint
                try:
                    result_response = self._make_request('GET', f'/api/jobs/{job_id}/results')
                    result_data = result_response.get('result')
                    error_msg = result_response.get('error_message')
                except:
                    result_data = None
                    error_msg = None
                
                return JobResult(
                    job_id=job_id,
                    status='completed',
                    result=result_data,
                    actual_cost=job.get('actual_cost', 0.0),
                    duration_seconds=job.get('duration_seconds'),
                    error_message=error_msg
                )
            
            elif status == 'failed':
                # Get error from /results endpoint
                try:
                    result_response = self._make_request('GET', f'/api/jobs/{job_id}/results')
                    error_msg = result_response.get('error_message', 'Job failed')
                except:
                    error_msg = 'Job failed'
                
                return JobResult(
                    job_id=job_id,
                    status='failed',
                    result=None,
                    actual_cost=job.get('actual_cost', 0.0),
                    duration_seconds=job.get('duration_seconds'),
                    error_message=error_msg
                )
            
            # Job still in progress
            time.sleep(poll_interval)
    
    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a running job (if supported by backend)
        
        Args:
            job_id: Job ID
            
        Returns:
            Response from backend
        """
        return self._make_request('POST', f'/api/jobs/{job_id}/cancel')
    
    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Job]:
        """
        List user's jobs
        
        Args:
            status: Filter by status (queued, executing, completed, failed)
            limit: Maximum number of jobs to return
            
        Returns:
            List of jobs
        """
        # Use the /optimized endpoint which filters by current user
        params = {'limit': limit}
        if status:
            params['status_filter'] = status
        
        return self._make_request('GET', '/api/jobs/optimized', params=params)
    
    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a file for media processing jobs
        
        Args:
            file_path: Path to local file to upload
            
        Returns:
            Dict containing:
                - file_id: Unique file ID
                - file_url: Public URL to access file
                - storage_path: Storage path in Supabase
                - file_size: Size in bytes
                
        Raises:
            FileNotFoundError: If file doesn't exist
            JobSubmissionError: If upload fails
            
        Example:
            >>> upload = client.upload_file("recording.m4a")
            >>> job = client.submit_job("audio_to_text", params={
            ...     "input_file_url": upload['file_url'],
            ...     "language": "en"
            ... })
        """
        import os
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Open file
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                
                # Upload via direct upload endpoint
                response = requests.post(
                    f"{self.api_url}/api/files/upload-direct",
                    headers={'Authorization': f'Bearer {self.token}'},
                    files=files,
                    timeout=300  # 5 minute timeout for large files
                )
                
                if response.status_code == 401:
                    raise AuthenticationError("Authentication failed - token may be expired")
                
                response.raise_for_status()
                result = response.json()
                
                if not result.get('success'):
                    raise JobSubmissionError(f"File upload failed: {result.get('error', 'Unknown error')}")
                
                return {
                    'file_id': result['file_id'],
                    'file_url': result['download_url'],
                    'storage_path': result['storage_path'],
                    'file_size': result['file_size']
                }
                
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"File upload failed: {str(e)}")
        except Exception as e:
            raise JobSubmissionError(f"File upload error: {str(e)}")

