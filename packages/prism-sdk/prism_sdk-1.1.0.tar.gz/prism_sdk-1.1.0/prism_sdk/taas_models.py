"""
Trust-as-a-Service (TaaS) models for Prism SDK
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ========== REQUEST MODELS ==========

class VerifiedSearchRequest(BaseModel):
    """Request for verified search with trust scoring"""
    query: str = Field(..., min_length=1, max_length=2000, description="Search query")
    max_sources: int = Field(10, ge=1, le=50, description="Maximum sources to return")
    include_citations: bool = Field(True, description="Include source citations")
    trust_threshold: float = Field(0.7, ge=0, le=1, description="Minimum trust threshold")


class HallucinationCheckRequest(BaseModel):
    """Request for hallucination detection"""
    text: str = Field(..., min_length=1, max_length=10000, description="Text to check")
    include_recommendations: bool = Field(True, description="Include recommendations")


class SourceVerificationRequest(BaseModel):
    """Request for source verification"""
    sources: List[Dict[str, str]] = Field(..., min_items=1, max_items=50, description="Sources to verify")
    include_details: bool = Field(True, description="Include detailed analysis")


class ReasoningAnalysisRequest(BaseModel):
    """Request for reasoning quality analysis"""
    query: str = Field(..., min_length=1, max_length=1000, description="Original query")
    response: str = Field(..., min_length=1, max_length=10000, description="Response to analyze")
    sources: Optional[List[Dict[str, str]]] = Field(default=None, description="Sources used")


class ContentSafetyRequest(BaseModel):
    """Request for content safety check"""
    content: str = Field(..., min_length=1, max_length=10000, description="Content to check")
    check_bias: bool = Field(True, description="Check for bias")
    check_pii: bool = Field(True, description="Check for PII")


# ========== RESPONSE MODELS ==========

class Citation(BaseModel):
    """Citation information for verified content"""
    source_id: str = Field(..., description="Source identifier")
    title: str = Field(..., description="Source title")
    url: str = Field(..., description="Source URL")
    excerpt: str = Field(..., description="Relevant excerpt")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score")


class VerifiedSource(BaseModel):
    """Verified source with trust information"""
    id: str = Field(..., description="Source identifier")
    title: str = Field(..., description="Source title")
    url: str = Field(..., description="Source URL")
    domain: str = Field(..., description="Domain name")
    trust_score: float = Field(..., ge=0, le=1, description="Trust score")
    credibility_score: float = Field(..., ge=0, le=1, description="Credibility score")
    bias_assessment: Optional[str] = Field(None, description="Bias assessment")
    published_date: Optional[str] = Field(None, description="Publication date")


class ProvenanceInfo(BaseModel):
    """Cryptographic provenance information"""
    signature: str = Field(..., description="Cryptographic signature")
    timestamp: str = Field(..., description="ISO timestamp")
    request_id: str = Field(..., description="Unique request identifier")
    verification_note: Optional[str] = Field(None, description="Verification notes")


class VerifiedSearchResult(BaseModel):
    """Result from verified search with trust scoring"""
    success: bool = Field(..., description="Request success status")
    request_id: str = Field(..., description="Unique request identifier")
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Verified answer")
    trust_score: float = Field(..., ge=0, le=1, description="Overall trust score")
    confidence_level: str = Field(..., description="Confidence level")
    sources: List[VerifiedSource] = Field(..., description="Verified sources")
    citations: List[Citation] = Field(..., description="Citations used")
    provenance: ProvenanceInfo = Field(..., description="Cryptographic provenance")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    tokens_estimated: int = Field(..., description="Estimated tokens used")
    cost_usd: float = Field(..., description="Cost in USD")


class FactualClaim(BaseModel):
    """Individual factual claim extracted from text"""
    claim: str = Field(..., description="The factual claim")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in claim")
    verifiable: bool = Field(..., description="Whether claim is verifiable")
    risk_level: str = Field(..., description="Risk level (low, medium, high)")


class HallucinationReport(BaseModel):
    """Report from hallucination detection"""
    success: bool = Field(..., description="Request success status")
    request_id: str = Field(..., description="Unique request identifier")
    hallucination_detected: bool = Field(..., description="Whether hallucination detected")
    risk_level: str = Field(..., description="Overall risk level")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")
    factual_claims: List[FactualClaim] = Field(..., description="Extracted factual claims")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations")
    provenance: ProvenanceInfo = Field(..., description="Cryptographic provenance")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    tokens_estimated: int = Field(..., description="Estimated tokens used")
    cost_usd: float = Field(..., description="Cost in USD")


class SourceAnalysis(BaseModel):
    """Analysis of a single source"""
    source_id: str = Field(..., description="Source identifier")
    url: str = Field(..., description="Source URL")
    domain: str = Field(..., description="Domain name")
    reliability_score: float = Field(..., ge=0, le=1, description="Reliability score")
    credibility_score: float = Field(..., ge=0, le=1, description="Credibility score")
    bias_assessment: str = Field(..., description="Bias assessment")
    risk_factors: List[str] = Field(..., description="Identified risk factors")
    verification_status: str = Field(..., description="Verification status")


class SourceVerificationReport(BaseModel):
    """Report from source verification"""
    success: bool = Field(..., description="Request success status")
    request_id: str = Field(..., description="Unique request identifier")
    sources_analyzed: int = Field(..., description="Number of sources analyzed")
    overall_reliability: float = Field(..., ge=0, le=1, description="Overall reliability")
    source_analyses: List[SourceAnalysis] = Field(..., description="Individual source analyses")
    credibility_breakdown: Dict[str, float] = Field(..., description="Credibility breakdown")
    risk_summary: Dict[str, int] = Field(..., description="Risk summary")
    provenance: ProvenanceInfo = Field(..., description="Cryptographic provenance")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    cost_usd: float = Field(..., description="Cost in USD")


class ReasoningStep(BaseModel):
    """Individual step in reasoning chain"""
    step_number: int = Field(..., description="Step number")
    description: str = Field(..., description="Step description")
    logic_score: float = Field(..., ge=0, le=1, description="Logic quality score")
    evidence_quality: float = Field(..., ge=0, le=1, description="Evidence quality")


class LogicalFallacy(BaseModel):
    """Detected logical fallacy"""
    fallacy_type: str = Field(..., description="Type of fallacy")
    description: str = Field(..., description="Fallacy description")
    location: str = Field(..., description="Where fallacy appears")
    severity: str = Field(..., description="Severity level")


class ReasoningAnalysis(BaseModel):
    """Analysis of reasoning quality"""
    success: bool = Field(..., description="Request success status")
    request_id: str = Field(..., description="Unique request identifier")
    logical_consistency: float = Field(..., ge=0, le=1, description="Logical consistency score")
    evidence_quality: float = Field(..., ge=0, le=1, description="Evidence quality score")
    coherence_score: float = Field(..., ge=0, le=1, description="Coherence score")
    reasoning_steps: List[ReasoningStep] = Field(..., description="Reasoning steps analyzed")
    fallacies_detected: List[LogicalFallacy] = Field(..., description="Logical fallacies detected")
    recommendations: List[str] = Field(..., description="Improvement recommendations")
    provenance: ProvenanceInfo = Field(..., description="Cryptographic provenance")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    cost_usd: float = Field(..., description="Cost in USD")


class SafetyIssue(BaseModel):
    """Individual safety issue detected"""
    issue_type: str = Field(..., description="Type of issue")
    severity: str = Field(..., description="Severity level")
    description: str = Field(..., description="Issue description")
    location: str = Field(..., description="Where issue appears")


class BiasAnalysis(BaseModel):
    """Bias analysis results"""
    bias_detected: bool = Field(..., description="Whether bias detected")
    bias_types: List[str] = Field(..., description="Types of bias found")
    bias_score: float = Field(..., ge=0, le=1, description="Overall bias score")
    examples: List[str] = Field(..., description="Example biased statements")


class PIIAnalysis(BaseModel):
    """PII detection results"""
    pii_detected: bool = Field(..., description="Whether PII detected")
    pii_types: List[str] = Field(..., description="Types of PII found")
    locations: List[str] = Field(..., description="PII locations")
    redaction_suggestions: List[str] = Field(..., description="Redaction suggestions")


class ContentSafetyReport(BaseModel):
    """Report from content safety check"""
    success: bool = Field(..., description="Request success status")
    request_id: str = Field(..., description="Unique request identifier")
    is_safe: bool = Field(..., description="Whether content is safe")
    safety_score: float = Field(..., ge=0, le=1, description="Overall safety score")
    policy_violations: List[str] = Field(..., description="Policy violations detected")
    safety_issues: List[SafetyIssue] = Field(..., description="Detailed safety issues")
    bias_analysis: Optional[BiasAnalysis] = Field(None, description="Bias analysis")
    pii_analysis: Optional[PIIAnalysis] = Field(None, description="PII analysis")
    risk_categories: Dict[str, float] = Field(..., description="Risk by category")
    recommendations: List[str] = Field(..., description="Safety recommendations")
    provenance: ProvenanceInfo = Field(..., description="Cryptographic provenance")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    cost_usd: float = Field(..., description="Cost in USD")


# ========== BATCH OPERATION MODELS ==========

class BatchHallucinationResult(BaseModel):
    """Result from batch hallucination check"""
    text: str = Field(..., description="Original text")
    result: HallucinationReport = Field(..., description="Hallucination report")
    error: Optional[str] = Field(None, description="Error if failed")


class BatchSourceVerificationResult(BaseModel):
    """Result from batch source verification"""
    sources: List[Dict[str, str]] = Field(..., description="Original sources")
    result: SourceVerificationReport = Field(..., description="Verification report")
    error: Optional[str] = Field(None, description="Error if failed")
