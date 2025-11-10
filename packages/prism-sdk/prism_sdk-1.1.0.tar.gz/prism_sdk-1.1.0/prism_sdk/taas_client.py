"""
Trust-as-a-Service (TaaS) client for Prism SDK
"""
import asyncio
from typing import Optional, List, Dict, Any
import httpx
from .taas_models import (
    VerifiedSearchRequest, VerifiedSearchResult,
    HallucinationCheckRequest, HallucinationReport,
    SourceVerificationRequest, SourceVerificationReport,
    ReasoningAnalysisRequest, ReasoningAnalysis,
    ContentSafetyRequest, ContentSafetyReport,
    BatchHallucinationResult, BatchSourceVerificationResult
)
from .models import PrismError


class TaaSClient:
    """
    Trust-as-a-Service client for verified AI responses
    
    Provides access to:
    - Verified search with trust scoring
    - Hallucination detection
    - Source verification
    - Reasoning quality analysis
    - Content safety checks
    
    Example:
        client = TaaSClient(api_key="your-api-key")
        result = client.verified_search("What is quantum computing?")
        print(f"Trust Score: {result.trust_score}")
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: float = 60.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize TaaS client
        
        Args:
            api_key: Your Prism Labs API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds (TaaS operations can be slow)
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # HTTP clients
        self.client = httpx.Client(
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
                "User-Agent": "prism-sdk-python/1.1.0"
            }
        )
        
        self.async_client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
                "User-Agent": "prism-sdk-python/1.1.0"
            }
        )
    
    def _make_url(self, endpoint: str) -> str:
        """Construct full URL for an endpoint"""
        from urllib.parse import urljoin
        return urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate errors"""
        try:
            data = response.json()
        except Exception:
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
    
    def _make_sync_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make synchronous HTTP request with retry logic"""
        import time
        url = self._make_url(endpoint)
        
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = self.client.get(url, params=params)
                elif method.upper() == "POST":
                    response = self.client.post(url, json=data, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                return self._handle_response(response)
                
            except httpx.RequestError as e:
                if attempt == self.max_retries:
                    raise PrismError(f"Request failed after {self.max_retries + 1} attempts: {str(e)}")
                time.sleep(self.retry_delay * (2 ** attempt))
            except PrismError:
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
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                return self._handle_response(response)
                
            except httpx.RequestError as e:
                if attempt == self.max_retries:
                    raise PrismError(f"Request failed after {self.max_retries + 1} attempts: {str(e)}")
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
            except PrismError:
                raise
    
    # ========== VERIFIED SEARCH ==========
    
    def verified_search(
        self,
        query: str,
        max_sources: int = 10,
        include_citations: bool = True,
        trust_threshold: float = 0.7
    ) -> VerifiedSearchResult:
        """
        Get AI response with trust verification
        
        Args:
            query: Search query
            max_sources: Maximum sources to return (1-50)
            include_citations: Include source citations
            trust_threshold: Minimum trust threshold (0.0-1.0)
            
        Returns:
            VerifiedSearchResult: Verified search result with trust scores
            
        Example:
            result = client.verified_search("Is renewable energy cost-effective?")
            print(f"Answer: {result.answer}")
            print(f"Trust Score: {result.trust_score}")
            for source in result.sources:
                print(f"- {source.title} (Trust: {source.trust_score})")
        """
        request_data = VerifiedSearchRequest(
            query=query,
            max_sources=max_sources,
            include_citations=include_citations,
            trust_threshold=trust_threshold
        )
        
        data = self._make_sync_request("POST", "/v1/trust/verified-search", request_data.dict())
        return VerifiedSearchResult(**data)
    
    async def verified_search_async(
        self,
        query: str,
        max_sources: int = 10,
        include_citations: bool = True,
        trust_threshold: float = 0.7
    ) -> VerifiedSearchResult:
        """Async version of verified_search"""
        request_data = VerifiedSearchRequest(
            query=query,
            max_sources=max_sources,
            include_citations=include_citations,
            trust_threshold=trust_threshold
        )
        
        data = await self._make_async_request("POST", "/v1/trust/verified-search", request_data.dict())
        return VerifiedSearchResult(**data)
    
    # ========== HALLUCINATION DETECTION ==========
    
    def hallucination_check(
        self,
        text: str,
        include_recommendations: bool = True
    ) -> HallucinationReport:
        """
        Check content for AI hallucinations
        
        Args:
            text: Text to check for hallucinations
            include_recommendations: Include recommendations for improvement
            
        Returns:
            HallucinationReport: Detailed hallucination analysis
            
        Example:
            report = client.hallucination_check(
                "The Eiffel Tower was built in 1887 and is 350 meters tall."
            )
            if report.hallucination_detected:
                print(f"Risk Level: {report.risk_level}")
                print(f"Confidence: {report.confidence}")
                for claim in report.factual_claims:
                    print(f"- {claim.claim} (Risk: {claim.risk_level})")
        """
        request_data = HallucinationCheckRequest(
            text=text,
            include_recommendations=include_recommendations
        )
        
        data = self._make_sync_request("POST", "/v1/trust/hallucination-check-simple", request_data.dict())
        return HallucinationReport(**data)
    
    async def hallucination_check_async(
        self,
        text: str,
        include_recommendations: bool = True
    ) -> HallucinationReport:
        """Async version of hallucination_check"""
        request_data = HallucinationCheckRequest(
            text=text,
            include_recommendations=include_recommendations
        )
        
        data = await self._make_async_request("POST", "/v1/trust/hallucination-check-simple", request_data.dict())
        return HallucinationReport(**data)
    
    # ========== SOURCE VERIFICATION ==========
    
    def verify_sources(
        self,
        sources: List[Dict[str, str]],
        include_details: bool = True
    ) -> SourceVerificationReport:
        """
        Verify reliability of sources
        
        Args:
            sources: List of sources with 'url' and optionally 'title'
            include_details: Include detailed analysis per source
            
        Returns:
            SourceVerificationReport: Source verification results
            
        Example:
            sources = [
                {"url": "https://example.com/article", "title": "Article Title"},
                {"url": "https://another.com/post"}
            ]
            report = client.verify_sources(sources)
            print(f"Overall Reliability: {report.overall_reliability}")
            for analysis in report.source_analyses:
                print(f"- {analysis.url}: {analysis.reliability_score}")
        """
        request_data = SourceVerificationRequest(
            sources=sources,
            include_details=include_details
        )
        
        data = self._make_sync_request("POST", "/v1/trust/source-verification-simple", request_data.dict())
        return SourceVerificationReport(**data)
    
    async def verify_sources_async(
        self,
        sources: List[Dict[str, str]],
        include_details: bool = True
    ) -> SourceVerificationReport:
        """Async version of verify_sources"""
        request_data = SourceVerificationRequest(
            sources=sources,
            include_details=include_details
        )
        
        data = await self._make_async_request("POST", "/v1/trust/source-verification-simple", request_data.dict())
        return SourceVerificationReport(**data)
    
    # ========== REASONING ANALYSIS ==========
    
    def analyze_reasoning(
        self,
        query: str,
        response: str,
        sources: Optional[List[Dict[str, str]]] = None
    ) -> ReasoningAnalysis:
        """
        Analyze reasoning quality of AI response
        
        Args:
            query: Original query
            response: AI response to analyze
            sources: Sources used (optional)
            
        Returns:
            ReasoningAnalysis: Detailed reasoning quality analysis
            
        Example:
            analysis = client.analyze_reasoning(
                query="Why is the sky blue?",
                response="The sky is blue because of Rayleigh scattering..."
            )
            print(f"Logical Consistency: {analysis.logical_consistency}")
            print(f"Evidence Quality: {analysis.evidence_quality}")
            if analysis.fallacies_detected:
                for fallacy in analysis.fallacies_detected:
                    print(f"- {fallacy.fallacy_type}: {fallacy.description}")
        """
        request_data = ReasoningAnalysisRequest(
            query=query,
            response=response,
            sources=sources or []
        )
        
        data = self._make_sync_request("POST", "/v1/trust/reasoning-analysis-simple", request_data.dict())
        return ReasoningAnalysis(**data)
    
    async def analyze_reasoning_async(
        self,
        query: str,
        response: str,
        sources: Optional[List[Dict[str, str]]] = None
    ) -> ReasoningAnalysis:
        """Async version of analyze_reasoning"""
        request_data = ReasoningAnalysisRequest(
            query=query,
            response=response,
            sources=sources or []
        )
        
        data = await self._make_async_request("POST", "/v1/trust/reasoning-analysis-simple", request_data.dict())
        return ReasoningAnalysis(**data)
    
    # ========== CONTENT SAFETY ==========
    
    def check_content_safety(
        self,
        content: str,
        check_bias: bool = True,
        check_pii: bool = True
    ) -> ContentSafetyReport:
        """
        Check content safety and policy compliance
        
        Args:
            content: Content to check
            check_bias: Check for bias
            check_pii: Check for personally identifiable information
            
        Returns:
            ContentSafetyReport: Comprehensive safety analysis
            
        Example:
            report = client.check_content_safety(
                "This is some content to check for safety issues."
            )
            print(f"Is Safe: {report.is_safe}")
            print(f"Safety Score: {report.safety_score}")
            if report.policy_violations:
                print("Policy Violations:", report.policy_violations)
            if report.bias_analysis and report.bias_analysis.bias_detected:
                print("Bias Types:", report.bias_analysis.bias_types)
        """
        request_data = ContentSafetyRequest(
            content=content,
            check_bias=check_bias,
            check_pii=check_pii
        )
        
        data = self._make_sync_request("POST", "/v1/trust/content-safety-simple", request_data.dict())
        return ContentSafetyReport(**data)
    
    async def check_content_safety_async(
        self,
        content: str,
        check_bias: bool = True,
        check_pii: bool = True
    ) -> ContentSafetyReport:
        """Async version of check_content_safety"""
        request_data = ContentSafetyRequest(
            content=content,
            check_bias=check_bias,
            check_pii=check_pii
        )
        
        data = await self._make_async_request("POST", "/v1/trust/content-safety-simple", request_data.dict())
        return ContentSafetyReport(**data)
    
    # ========== BATCH OPERATIONS ==========
    
    async def batch_hallucination_check(
        self,
        texts: List[str],
        include_recommendations: bool = True,
        max_workers: int = 5
    ) -> List[BatchHallucinationResult]:
        """
        Check multiple texts for hallucinations concurrently
        
        Args:
            texts: List of texts to check
            include_recommendations: Include recommendations
            max_workers: Maximum concurrent requests
            
        Returns:
            List[BatchHallucinationResult]: Results for each text
            
        Example:
            texts = [
                "The Eiffel Tower is 330 meters tall.",
                "Python was created in 1991 by Guido van Rossum.",
                "The Earth is flat."
            ]
            results = await client.batch_hallucination_check(texts)
            for i, result in enumerate(results):
                if result.error:
                    print(f"Text {i+1} failed: {result.error}")
                else:
                    print(f"Text {i+1}: Risk={result.result.risk_level}")
        """
        semaphore = asyncio.Semaphore(max_workers)
        
        async def check_one(text: str) -> BatchHallucinationResult:
            async with semaphore:
                try:
                    result = await self.hallucination_check_async(text, include_recommendations)
                    return BatchHallucinationResult(text=text, result=result, error=None)
                except Exception as e:
                    return BatchHallucinationResult(
                        text=text,
                        result=None,  # type: ignore
                        error=str(e)
                    )
        
        tasks = [check_one(text) for text in texts]
        return await asyncio.gather(*tasks)
    
    async def batch_verify_sources(
        self,
        source_lists: List[List[Dict[str, str]]],
        include_details: bool = True,
        max_workers: int = 5
    ) -> List[BatchSourceVerificationResult]:
        """
        Verify multiple source lists concurrently
        
        Args:
            source_lists: List of source lists to verify
            include_details: Include detailed analysis
            max_workers: Maximum concurrent requests
            
        Returns:
            List[BatchSourceVerificationResult]: Results for each source list
        """
        semaphore = asyncio.Semaphore(max_workers)
        
        async def verify_one(sources: List[Dict[str, str]]) -> BatchSourceVerificationResult:
            async with semaphore:
                try:
                    result = await self.verify_sources_async(sources, include_details)
                    return BatchSourceVerificationResult(sources=sources, result=result, error=None)
                except Exception as e:
                    return BatchSourceVerificationResult(
                        sources=sources,
                        result=None,  # type: ignore
                        error=str(e)
                    )
        
        tasks = [verify_one(sources) for sources in source_lists]
        return await asyncio.gather(*tasks)
    
    # ========== CONTEXT MANAGERS ==========
    
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
