"""
Main Prism SDK client for interacting with the Prism Labs API
"""
import asyncio
import json
import time
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
import httpx
from .models import (
    QueryResult, TrustScore, VerificationResult, KnowledgeGraph, 
    UsageInfo, APIHealthStatus, PrismError, QueryRequest, ScoreRequest
)


class PrismClient:
    """
    Official Python client for the Prism Labs API
    
    This client provides access to all Prism API endpoints including:
    - Query verification
    - Trust scoring  
    - Knowledge graph generation
    - Usage monitoring
    
    Example:
        client = PrismClient(api_key="your-api-key")
        result = client.query("What is artificial intelligence?")
        print(f"Trust Score: {result.trust_score.overall_score}")
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8001",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the Prism client
        
        Args:
            api_key: Your Prism Labs API key
            base_url: Base URL for the Prism API (default: localhost for development)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # HTTP client with default headers
        self.client = httpx.Client(
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
                "User-Agent": "prism-sdk-python/1.0.0"
            }
        )
        
        # Async client for async operations
        self.async_client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
                "User-Agent": "prism-sdk-python/1.0.0"
            }
        )
    
    def _make_url(self, endpoint: str) -> str:
        """Construct full URL for an endpoint"""
        return urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate errors"""
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise PrismError(
                f"Invalid JSON response: {response.text}",
                status_code=response.status_code
            )
        
        if response.status_code >= 400:
            error_message = data.get('detail', f'API error: {response.status_code}')
            raise PrismError(
                error_message,
                status_code=response.status_code,
                response_data=data
            )
        
        return data
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = self._make_url(endpoint)
        
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = await self.async_client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await self.async_client.post(url, json=data, params=params)
                elif method.upper() == "PUT":
                    response = await self.async_client.put(url, json=data, params=params)
                elif method.upper() == "DELETE":
                    response = await self.async_client.delete(url, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                return self._handle_response(response)
                
            except httpx.RequestError as e:
                if attempt == self.max_retries:
                    raise PrismError(f"Request failed after {self.max_retries + 1} attempts: {str(e)}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
            except PrismError:
                # Don't retry on API errors (4xx, 5xx)
                raise
    
    def _make_sync_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make sync HTTP request with retry logic"""
        url = self._make_url(endpoint)
        
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = self.client.get(url, params=params)
                elif method.upper() == "POST":
                    response = self.client.post(url, json=data, params=params)
                elif method.upper() == "PUT":
                    response = self.client.put(url, json=data, params=params)
                elif method.upper() == "DELETE":
                    response = self.client.delete(url, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                return self._handle_response(response)
                
            except httpx.RequestError as e:
                if attempt == self.max_retries:
                    raise PrismError(f"Request failed after {self.max_retries + 1} attempts: {str(e)}")
                time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
            except PrismError:
                # Don't retry on API errors (4xx, 5xx)
                raise
    
    async def _make_async_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make async HTTP request with retry logic"""
        url = self._make_url(endpoint)
        
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = await self.async_client.get(url, params=params)
                elif method.upper() == "POST":
                    response = await self.async_client.post(url, json=data, params=params)
                elif method.upper() == "PUT":
                    response = await self.async_client.put(url, json=data, params=params)
                elif method.upper() == "DELETE":
                    response = await self.async_client.delete(url, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                return self._handle_response(response)
                
            except httpx.RequestError as e:
                if attempt == self.max_retries:
                    raise PrismError(f"Request failed after {self.max_retries + 1} attempts: {str(e)}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
            except PrismError:
                raise
    
    def health(self) -> APIHealthStatus:
        """
        Check API health status
        
        Returns:
            APIHealthStatus: Current API health information
        """
        data = self._make_sync_request("GET", "/")
        return APIHealthStatus(**data)
    
    def query(
        self,
        query: str,
        include_reasoning: bool = True,
        include_sources: bool = True,
        max_sources: int = 10,
        trust_threshold: float = 0.0
    ) -> QueryResult:
        """
        Submit a verification query to Prism
        
        Args:
            query: The question or statement to verify
            include_reasoning: Include reasoning steps in response
            include_sources: Include source information in response  
            max_sources: Maximum number of sources to return (1-50)
            trust_threshold: Minimum trust score threshold (0.0-1.0)
            
        Returns:
            QueryResult: Comprehensive verification result
            
        Example:
            result = client.query("Is climate change caused by human activity?")
            print(f"Summary: {result.summary}")
            print(f"Trust Score: {result.trust_score.overall_score}")
        """
        request_data = QueryRequest(
            query=query,
            include_reasoning=include_reasoning,
            include_sources=include_sources,
            max_sources=max_sources,
            trust_threshold=trust_threshold
        )
        
        data = self._make_sync_request("POST", "/v1/query", request_data.dict())
        return QueryResult(**data)
    
    def score_content(
        self,
        content: str,
        context: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> TrustScore:
        """
        Get trust score for specific content
        
        Args:
            content: Content to analyze and score
            context: Additional context for scoring
            source_url: Source URL if available
            
        Returns:
            TrustScore: Detailed trust score breakdown
        """
        request_data = ScoreRequest(
            content=content,
            context=context,
            source_url=source_url
        )
        
        data = self._make_sync_request("POST", "/v1/score", request_data.dict())
        return TrustScore(**data)
    
    def get_verification(self, verification_id: str) -> VerificationResult:
        """
        Retrieve a specific verification result
        
        Args:
            verification_id: Unique verification identifier
            
        Returns:
            VerificationResult: Complete verification details
        """
        data = self._make_sync_request("GET", f"/v1/verify/{verification_id}")
        return VerificationResult(**data)
    
    def get_knowledge_graph(self, verification_id: str) -> KnowledgeGraph:
        """
        Get knowledge graph for a verification
        
        Args:
            verification_id: Unique verification identifier
            
        Returns:
            KnowledgeGraph: Knowledge graph structure
        """
        data = self._make_sync_request("GET", f"/v1/graph/{verification_id}")
        return KnowledgeGraph(**data)
    
    def get_usage(self) -> UsageInfo:
        """
        Get current API usage information
        
        Returns:
            UsageInfo: Usage statistics and quota information
        """
        data = self._make_sync_request("GET", "/v1/me/usage")
        return UsageInfo(**data)
    
    # Async versions of all methods
    async def query_async(
        self,
        query: str,
        include_reasoning: bool = True,
        include_sources: bool = True,
        max_sources: int = 10,
        trust_threshold: float = 0.0
    ) -> QueryResult:
        """Async version of query method"""
        request_data = QueryRequest(
            query=query,
            include_reasoning=include_reasoning,
            include_sources=include_sources,
            max_sources=max_sources,
            trust_threshold=trust_threshold
        )
        
        data = await self._make_async_request("POST", "/v1/query", request_data.dict())
        return QueryResult(**data)
    
    async def score_content_async(
        self,
        content: str,
        context: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> TrustScore:
        """Async version of score_content method"""
        request_data = ScoreRequest(
            content=content,
            context=context,
            source_url=source_url
        )
        
        data = await self._make_async_request("POST", "/v1/score", request_data.dict())
        return TrustScore(**data)
    
    async def get_verification_async(self, verification_id: str) -> VerificationResult:
        """Async version of get_verification method"""
        data = await self._make_async_request("GET", f"/v1/verify/{verification_id}")
        return VerificationResult(**data)
    
    async def get_knowledge_graph_async(self, verification_id: str) -> KnowledgeGraph:
        """Async version of get_knowledge_graph method"""
        data = await self._make_async_request("GET", f"/v1/graph/{verification_id}")
        return KnowledgeGraph(**data)
    
    async def get_usage_async(self) -> UsageInfo:
        """Async version of get_usage method"""
        data = await self._make_async_request("GET", "/v1/me/usage")
        return UsageInfo(**data)
    
    def close(self):
        """Close HTTP clients (sync version)"""
        self.client.close()
    
    async def close_async(self):
        """Close async HTTP client"""
        if self.async_client:
            await self.async_client.aclose()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.client.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_async()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_async()