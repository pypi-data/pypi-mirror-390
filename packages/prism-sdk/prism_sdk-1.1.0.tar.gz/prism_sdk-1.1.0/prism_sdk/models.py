"""
Pydantic models for Prism SDK responses and data structures
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PrismError(Exception):
    """Custom exception for Prism API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class SourceInfo(BaseModel):
    """Information about a source used in verification"""
    id: str = Field(..., description="Unique source identifier")
    title: str = Field(..., description="Source title")
    url: str = Field(..., description="Source URL")
    domain: str = Field(..., description="Source domain")
    published_date: Optional[str] = Field(None, description="Publication date")
    author: Optional[str] = Field(None, description="Author name")
    trust_score: float = Field(..., ge=0, le=1, description="Source trust score (0-1)")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance to query (0-1)")
    excerpt: Optional[str] = Field(None, description="Relevant excerpt from source")


class ReasoningStep(BaseModel):
    """A step in the reasoning process"""
    step_number: int = Field(..., description="Step number in reasoning chain")
    description: str = Field(..., description="Description of this reasoning step")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in this step")


class ProviderConsensus(BaseModel):
    """Consensus information from multiple providers"""
    total_providers: int = Field(..., description="Total number of providers consulted")
    agreeing_providers: int = Field(..., description="Number of providers in agreement")
    consensus_percentage: float = Field(..., ge=0, le=100, description="Percentage consensus")
    conflicting_views: List[str] = Field(default_factory=list, description="Conflicting viewpoints")


class MetaInfo(BaseModel):
    """Metadata about the verification process"""
    model_config = {"protected_namespaces": ()}
    
    query_id: str = Field(..., description="Unique query identifier")
    verification_id: str = Field(..., description="Unique verification identifier")
    timestamp: datetime = Field(..., description="Verification timestamp")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    api_version: str = Field(..., description="API version used")
    model_version: str = Field(..., description="AI model version used")


class GraphNode(BaseModel):
    """Node in the knowledge graph"""
    id: str = Field(..., description="Node identifier")
    label: str = Field(..., description="Node label")
    type: str = Field(..., description="Node type (concept, entity, fact, etc.)")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in node accuracy")


class GraphEdge(BaseModel):
    """Edge connecting nodes in the knowledge graph"""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship: str = Field(..., description="Relationship type")
    weight: float = Field(..., ge=0, le=1, description="Relationship strength")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")


class KnowledgeGraph(BaseModel):
    """Complete knowledge graph structure"""
    nodes: List[GraphNode] = Field(..., description="Graph nodes")
    edges: List[GraphEdge] = Field(..., description="Graph edges")
    central_concepts: List[str] = Field(..., description="Central concepts in the graph")
    complexity_score: float = Field(..., ge=0, le=1, description="Graph complexity score")


class TrustScore(BaseModel):
    """Trust score information"""
    overall_score: float = Field(..., ge=0, le=1, description="Overall trust score (0-1)")
    source_reliability: float = Field(..., ge=0, le=1, description="Source reliability score")
    content_accuracy: float = Field(..., ge=0, le=1, description="Content accuracy score")
    consensus_strength: float = Field(..., ge=0, le=1, description="Cross-source consensus")
    temporal_consistency: float = Field(..., ge=0, le=1, description="Temporal consistency score")
    reasoning_quality: float = Field(..., ge=0, le=1, description="Reasoning quality score")
    confidence_level: str = Field(..., description="Confidence level (very_high, high, medium, low)")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")


class QueryResult(BaseModel):
    """Result of a verification query"""
    query: str = Field(..., description="Original query")
    summary: str = Field(..., description="Summary of findings")
    detailed_analysis: str = Field(..., description="Detailed analysis")
    trust_score: TrustScore = Field(..., description="Trust score breakdown")
    sources: List[SourceInfo] = Field(..., description="Sources used")
    reasoning_steps: List[ReasoningStep] = Field(..., description="Reasoning process")
    provider_consensus: ProviderConsensus = Field(..., description="Provider consensus")
    meta: MetaInfo = Field(..., description="Metadata")
    knowledge_graph_id: Optional[str] = Field(None, description="Knowledge graph ID if available")


class VerificationResult(BaseModel):
    """Detailed verification result"""
    verification_id: str = Field(..., description="Verification identifier")
    status: str = Field(..., description="Verification status")
    result: QueryResult = Field(..., description="Verification result")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UsageInfo(BaseModel):
    """API usage information"""
    api_key_id: str = Field(..., description="API key identifier")
    current_usage: int = Field(..., description="Current usage count")
    quota_limit: int = Field(..., description="Monthly quota limit")
    usage_percentage: float = Field(..., description="Usage percentage")
    remaining_requests: int = Field(..., description="Remaining requests")
    reset_date: str = Field(..., description="Quota reset date")
    rate_limit: Dict[str, Any] = Field(..., description="Rate limiting information")


class APIHealthStatus(BaseModel):
    """API health status"""
    status: str = Field(..., description="Overall API status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Status check timestamp")
    services: Dict[str, Any] = Field(..., description="Service status details")


# Request models for API calls
class QueryRequest(BaseModel):
    """Request model for verification queries"""
    query: str = Field(..., min_length=1, max_length=2000, description="Query to verify")
    include_reasoning: bool = Field(True, description="Include reasoning steps")
    include_sources: bool = Field(True, description="Include source information")
    max_sources: int = Field(10, ge=1, le=50, description="Maximum number of sources")
    trust_threshold: float = Field(0.0, ge=0, le=1, description="Minimum trust threshold")


class ScoreRequest(BaseModel):
    """Request model for trust scoring"""
    content: str = Field(..., min_length=1, description="Content to score")
    context: Optional[str] = Field(None, description="Additional context")
    source_url: Optional[str] = Field(None, description="Source URL if available")