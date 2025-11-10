# Prism SDK for Python
"""
Official Python SDK for Prism Labs - AI-Powered Trust Verification API

The Prism SDK provides a simple interface to interact with the Prism Labs API
for trust verification, fact-checking, and knowledge graph generation.

Example:
    from prism_sdk import PrismClient, TaaSClient
    
    # Traditional verification
    client = PrismClient(api_key="your-api-key")
    result = client.query("What is quantum computing?")
    print(result.summary)
    
    # Trust-as-a-Service
    taas = TaaSClient(api_key="your-api-key")
    verified = taas.verified_search("Is renewable energy cost-effective?")
    print(f"Trust Score: {verified.trust_score}")
"""

__version__ = "1.1.0"
__author__ = "Prism Meta"
__email__ = "noreply@prismmeta.com"

from .client import PrismClient
from .taas_client import TaaSClient
from .models import (
    QueryResult,
    TrustScore,
    VerificationResult,
    KnowledgeGraph,
    UsageInfo,
    SourceInfo,
    ReasoningStep,
    PrismError
)
from .taas_models import (
    VerifiedSearchResult,
    HallucinationReport,
    SourceVerificationReport,
    ReasoningAnalysis,
    ContentSafetyReport,
    VerifiedSource,
    Citation,
    FactualClaim,
    SourceAnalysis,
    LogicalFallacy,
    BiasAnalysis,
    PIIAnalysis
)

__all__ = [
    # Core client
    "PrismClient",
    "TaaSClient",
    
    # Core models
    "QueryResult", 
    "TrustScore",
    "VerificationResult",
    "KnowledgeGraph",
    "UsageInfo",
    "SourceInfo",
    "ReasoningStep",
    "PrismError",
    
    # TaaS models
    "VerifiedSearchResult",
    "HallucinationReport",
    "SourceVerificationReport",
    "ReasoningAnalysis",
    "ContentSafetyReport",
    "VerifiedSource",
    "Citation",
    "FactualClaim",
    "SourceAnalysis",
    "LogicalFallacy",
    "BiasAnalysis",
    "PIIAnalysis"
]