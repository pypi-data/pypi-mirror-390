"""
Basic verification example using the Prism SDK

This example demonstrates how to:
1. Initialize the Prism client
2. Submit a verification query
3. Analyze the results
4. Handle errors properly
"""

import os
from prism_sdk import PrismClient, PrismError


def main():
    """Basic verification example"""
    
    # Initialize client (use environment variable or replace with your API key)
    api_key = os.getenv("PRISM_API_KEY", "your-api-key-here")
    
    # For development, use localhost. For production, use the actual API URL
    client = PrismClient(
        api_key=api_key,
        base_url="http://localhost:8001"  # Change to production URL when ready
    )
    
    try:
        print("🔍 Starting Prism verification...")
        
        # Submit a verification query
        query = "Is renewable energy more cost-effective than fossil fuels in 2024?"
        print(f"Query: {query}")
        
        result = client.query(
            query=query,
            include_reasoning=True,
            include_sources=True,
            max_sources=10
        )
        
        print("\n📊 Verification Results:")
        print("=" * 50)
        
        # Display basic information
        print(f"Summary: {result.summary}")
        print(f"Trust Score: {result.trust_score.overall_score:.2f}")
        print(f"Confidence: {result.trust_score.confidence_level}")
        
        # Display trust score breakdown
        print(f"\n🎯 Trust Score Breakdown:")
        print(f"  Source Reliability: {result.trust_score.source_reliability:.2f}")
        print(f"  Content Accuracy: {result.trust_score.content_accuracy:.2f}")
        print(f"  Consensus Strength: {result.trust_score.consensus_strength:.2f}")
        print(f"  Reasoning Quality: {result.trust_score.reasoning_quality:.2f}")
        
        # Display sources
        print(f"\n📚 Sources ({len(result.sources)}):")
        for i, source in enumerate(result.sources[:5], 1):  # Show top 5 sources
            print(f"  {i}. {source.title}")
            print(f"     URL: {source.url}")
            print(f"     Trust: {source.trust_score:.2f}, Relevance: {source.relevance_score:.2f}")
            if source.excerpt:
                excerpt = source.excerpt[:100] + "..." if len(source.excerpt) > 100 else source.excerpt
                print(f"     Excerpt: {excerpt}")
            print()
        
        # Display reasoning steps
        if result.reasoning_steps:
            print(f"🧠 Reasoning Steps ({len(result.reasoning_steps)}):")
            for step in result.reasoning_steps[:3]:  # Show first 3 steps
                print(f"  Step {step.step_number}: {step.description}")
                print(f"    Confidence: {step.confidence:.2f}")
                if step.evidence:
                    print(f"    Evidence: {', '.join(step.evidence[:2])}")
                print()
        
        # Display provider consensus
        consensus = result.provider_consensus
        print(f"🤝 Provider Consensus:")
        print(f"  Agreement: {consensus.agreeing_providers}/{consensus.total_providers} providers")
        print(f"  Consensus: {consensus.consensus_percentage:.1f}%")
        
        # Display metadata
        meta = result.meta
        print(f"\n⚙️ Metadata:")
        print(f"  Query ID: {meta.query_id}")
        print(f"  Processing Time: {meta.processing_time_ms:.1f}ms")
        print(f"  API Version: {meta.api_version}")
        
        # Check if knowledge graph is available
        if result.knowledge_graph_id:
            print(f"\n🕸️ Knowledge Graph Available: {result.knowledge_graph_id}")
            try:
                graph = client.get_knowledge_graph(result.knowledge_graph_id)
                print(f"  Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")
                print(f"  Central Concepts: {', '.join(graph.central_concepts[:3])}")
            except Exception as e:
                print(f"  Error loading graph: {e}")
        
    except PrismError as e:
        print(f"❌ Prism API Error: {e.message}")
        print(f"Status Code: {e.status_code}")
        if e.response_data:
            print(f"Response: {e.response_data}")
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
    
    finally:
        # Always close the client
        client.close()


if __name__ == "__main__":
    main()