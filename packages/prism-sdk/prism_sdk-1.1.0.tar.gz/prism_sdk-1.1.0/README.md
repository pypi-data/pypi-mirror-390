# Prism SDK for Python 🐍

[![PyPI version](https://badge.fury.io/py/prism-sdk.svg)](https://badge.fury.io/py/prism-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/prism-sdk.svg)](https://pypi.org/project/prism-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for **Prism Meta** - AI-Powered Trust Verification API

## 🚀 Features

### Core Verification
- **Trust Verification**: Verify claims and statements with AI-powered analysis
- **Source Analysis**: Get detailed source reliability and credibility scores  
- **Knowledge Graphs**: Generate and explore knowledge graphs for complex topics

### 🆕 Trust-as-a-Service (TaaS) - New in v1.1.0
- **Verified Search**: Get AI responses with trust verification and citations
- **Hallucination Detection**: Detect AI hallucinations with confidence scoring
- **Source Verification**: Verify reliability and credibility of information sources
- **Reasoning Analysis**: Analyze reasoning quality and detect logical fallacies
- **Content Safety**: Check content for safety, bias, and PII

### Technical Features
- **Async Support**: Full async/await support for modern Python applications
- **Batch Operations**: Process multiple requests concurrently
- **Type Safety**: Complete type hints with Pydantic models
- **Retry Logic**: Built-in retry mechanisms with exponential backoff
- **Error Handling**: Comprehensive error handling with detailed error information

## 📦 Installation

```bash
pip install prism-sdk
```

For development with extra dependencies:
```bash
pip install prism-sdk[dev]
```

## 🔑 Getting Started

### 1. Get Your API Key

Sign up at [Prism Labs](https://prismmeta.com) to get your API key.

### 2. Basic Usage

```python
from prism_sdk import PrismClient

# Initialize the client
client = PrismClient(api_key="your-api-key-here")

# Verify a claim
result = client.query("Is renewable energy more cost-effective than fossil fuels?")

print(f"Summary: {result.summary}")
print(f"Trust Score: {result.trust_score.overall_score}")
print(f"Confidence: {result.trust_score.confidence_level}")

# Get detailed sources
for source in result.sources:
    print(f"- {source.title} (Trust: {source.trust_score:.2f})")
```

### 3. Async Usage

```python
import asyncio
from prism_sdk import PrismClient

async def main():
    async with PrismClient(api_key="your-api-key") as client:
        result = await client.query_async("What is quantum computing?")
        print(f"Trust Score: {result.trust_score.overall_score}")

asyncio.run(main())
```

### 4. Trust-as-a-Service (TaaS) - New in v1.1.0

```python
from prism_sdk import TaaSClient

# Initialize TaaS client
taas = TaaSClient(api_key="your-api-key")

# Verified search with trust scoring
result = taas.verified_search("Is renewable energy cost-effective?")
print(f"Answer: {result.answer}")
print(f"Trust Score: {result.trust_score}")
print(f"Sources: {len(result.sources)}")

# Hallucination detection
report = taas.hallucination_check("The Eiffel Tower is 350 meters tall.")
if report.hallucination_detected:
    print(f"Risk: {report.risk_level}")
    for claim in report.factual_claims:
        print(f"- {claim.claim} (Risk: {claim.risk_level})")

# Source verification
sources = [
    {"url": "https://nature.com/article", "title": "Research Article"}
]
report = taas.verify_sources(sources)
print(f"Reliability: {report.overall_reliability}")

# Reasoning analysis
analysis = taas.analyze_reasoning(
    query="Why is the sky blue?",
    response="The sky is blue due to Rayleigh scattering..."
)
print(f"Logic Score: {analysis.logical_consistency}")

# Content safety check
safety = taas.check_content_safety("Content to analyze...")
print(f"Safe: {safety.is_safe}")
print(f"Safety Score: {safety.safety_score}")

taas.close()
```

### 5. Batch Operations (Async)

```python
import asyncio
from prism_sdk import TaaSClient

async def batch_example():
    async with TaaSClient(api_key="your-api-key") as taas:
        # Batch hallucination check
        texts = ["Text 1", "Text 2", "Text 3"]
        results = await taas.batch_hallucination_check(texts, max_workers=5)
        
        for result in results:
            if result.error:
                print(f"Error: {result.error}")
            else:
                print(f"Risk: {result.result.risk_level}")

asyncio.run(batch_example())
```

## 📖 API Reference

### Core Verification Client

### Query Verification

```python
# Basic query
result = client.query("Your question here")

# Advanced query with options
result = client.query(
    query="Is artificial intelligence safe?",
    include_reasoning=True,      # Include reasoning steps
    include_sources=True,        # Include source information
    max_sources=15,             # Maximum sources to return
    trust_threshold=0.7         # Minimum trust threshold
)
```

### Trust Scoring

```python
# Score specific content
score = client.score_content(
    content="AI will replace all human jobs by 2030",
    context="Discussion about AI impact on employment",
    source_url="https://example.com/article"
)

print(f"Overall Score: {score.overall_score}")
print(f"Source Reliability: {score.source_reliability}")
print(f"Content Accuracy: {score.content_accuracy}")
```

### Knowledge Graphs

```python
# Get verification result
result = client.query("Explain climate change")

# Get knowledge graph
if result.knowledge_graph_id:
    graph = client.get_knowledge_graph(result.knowledge_graph_id)
    
    print(f"Nodes: {len(graph.nodes)}")
    print(f"Edges: {len(graph.edges)}")
    print(f"Central Concepts: {graph.central_concepts}")
```

### Usage Monitoring

```python
# Check API usage
usage = client.get_usage()

print(f"Current Usage: {usage.current_usage}/{usage.quota_limit}")
print(f"Remaining: {usage.remaining_requests}")
print(f"Usage: {usage.usage_percentage}%")
```

### Retrieve Past Verifications

```python
# Get specific verification by ID
verification = client.get_verification("ver_abc123")

print(f"Status: {verification.status}")
print(f"Query: {verification.result.query}")
print(f"Summary: {verification.result.summary}")
```

## 🔧 Configuration

### Environment Variables

You can set your API key as an environment variable:

```bash
export PRISM_API_KEY="your-api-key-here"
```

```python
import os
from prism_sdk import PrismClient

# Will automatically use PRISM_API_KEY environment variable
client = PrismClient(api_key=os.getenv("PRISM_API_KEY"))
```

### Custom Configuration

```python
client = PrismClient(
    api_key="your-api-key",
    base_url="https://api.prismmeta.com",  # Production URL
    timeout=60.0,                         # Request timeout
    max_retries=3,                        # Max retry attempts  
    retry_delay=1.0                       # Delay between retries
)
```

## 🛡️ Error Handling

```python
from prism_sdk import PrismClient, PrismError

client = PrismClient(api_key="your-api-key")

try:
    result = client.query("Your question")
except PrismError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Response Data: {e.response_data}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 📊 Response Models

All API responses are returned as typed Pydantic models:

- `QueryResult` - Complete verification result
- `TrustScore` - Trust score breakdown  
- `VerificationResult` - Stored verification
- `KnowledgeGraph` - Knowledge graph structure
- `UsageInfo` - API usage statistics
- `SourceInfo` - Source information
- `ReasoningStep` - Reasoning process step

## 🧪 Testing

```bash
# Install development dependencies
pip install prism-sdk[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=prism_sdk

# Type checking
mypy prism_sdk/

# Code formatting
black prism_sdk/
isort prism_sdk/
```

## 📚 Examples

Check out our [examples directory](examples/) for more usage examples:

- [Basic Verification](examples/basic_verification.py)
- [Async Batch Processing](examples/async_batch.py) 
- [Trust Score Analysis](examples/trust_analysis.py)
- [Knowledge Graph Exploration](examples/knowledge_graphs.py)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](https://docs.prismlabs.ai)
- 🐛 [Issue Tracker](https://github.com/prismlabs/prism-sdk-python/issues)
- 💬 [Discord Community](https://discord.gg/prismlabs)
- 📧 [Email Support](mailto:support@prismlabs.ai)

## 🗺️ Roadmap

- [ ] Streaming responses for real-time verification
- [ ] Webhook support for async processing
- [ ] Bulk verification APIs
- [ ] Enhanced knowledge graph visualization
- [ ] Custom model fine-tuning support

---

Made with ❤️ by Ronald Kigen Komen of  Prism Meta team