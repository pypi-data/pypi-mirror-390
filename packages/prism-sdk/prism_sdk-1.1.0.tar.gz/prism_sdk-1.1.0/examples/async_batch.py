"""
Async batch processing example using the Prism SDK

This example demonstrates how to:
1. Process multiple queries concurrently
2. Use async/await patterns
3. Handle batch results efficiently
4. Monitor progress and performance
"""

import asyncio
import time
from typing import List, Tuple
from prism_sdk import PrismClient, PrismError, QueryResult


async def verify_query_async(client: PrismClient, query: str, query_id: int) -> Tuple[int, QueryResult, str]:
    """Verify a single query asynchronously"""
    try:
        start_time = time.time()
        result = await client.query_async(query, max_sources=5)
        processing_time = time.time() - start_time
        
        return query_id, result, f"✅ Success ({processing_time:.2f}s)"
    
    except PrismError as e:
        return query_id, None, f"❌ API Error: {e.message}"
    
    except Exception as e:
        return query_id, None, f"❌ Error: {str(e)}"


async def process_batch(queries: List[str], max_concurrent: int = 5) -> List[Tuple[int, QueryResult, str]]:
    """Process a batch of queries with concurrency limit"""
    
    # Initialize async client
    async with PrismClient(
        api_key="your-api-key-here",  # Replace with your API key
        base_url="http://localhost:8001"
    ) as client:
        
        print(f"🚀 Processing {len(queries)} queries with max {max_concurrent} concurrent requests...")
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(query: str, query_id: int):
            async with semaphore:
                return await verify_query_async(client, query, query_id)
        
        # Create tasks for all queries
        tasks = [
            process_with_semaphore(query, i) 
            for i, query in enumerate(queries)
        ]
        
        # Process all queries concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        print(f"⏱️ Batch completed in {total_time:.2f} seconds")
        print(f"📊 Average: {total_time/len(queries):.2f}s per query")
        
        return results


async def main():
    """Main async function"""
    
    # Sample queries for batch processing
    queries = [
        "Is artificial intelligence safe for humanity?",
        "Do electric vehicles have lower lifetime emissions than gas cars?",
        "Is renewable energy cheaper than fossil fuels in 2024?",
        "Are vaccines effective against COVID-19?",
        "Does exercise improve mental health?",
        "Is climate change primarily caused by human activities?",
        "Are organic foods more nutritious than conventional foods?",
        "Is remote work more productive than office work?",
        "Do violent video games cause aggressive behavior?",
        "Is nuclear energy safer than coal power?"
    ]
    
    try:
        # Process queries in batches
        results = await process_batch(queries, max_concurrent=3)
        
        print("\n📋 Batch Results Summary:")
        print("=" * 80)
        
        successful_results = []
        failed_results = []
        
        for query_id, result, status in results:
            query = queries[query_id]
            print(f"\n{query_id + 1}. {query}")
            print(f"   Status: {status}")
            
            if result is not None:
                successful_results.append((query_id, result))
                print(f"   Trust Score: {result.trust_score.overall_score:.2f}")
                print(f"   Confidence: {result.trust_score.confidence_level}")
                print(f"   Sources: {len(result.sources)}")
                
                # Show brief summary
                summary = result.summary[:100] + "..." if len(result.summary) > 100 else result.summary
                print(f"   Summary: {summary}")
            else:
                failed_results.append(query_id)
        
        # Print final statistics
        print(f"\n📊 Final Statistics:")
        print(f"   Total Queries: {len(queries)}")
        print(f"   Successful: {len(successful_results)}")
        print(f"   Failed: {len(failed_results)}")
        print(f"   Success Rate: {len(successful_results)/len(queries)*100:.1f}%")
        
        # Analyze successful results
        if successful_results:
            trust_scores = [result.trust_score.overall_score for _, result in successful_results]
            avg_trust = sum(trust_scores) / len(trust_scores)
            
            print(f"\n🎯 Trust Score Analysis:")
            print(f"   Average Trust Score: {avg_trust:.2f}")
            print(f"   Highest Trust Score: {max(trust_scores):.2f}")
            print(f"   Lowest Trust Score: {min(trust_scores):.2f}")
            
            # Show highest and lowest trust queries
            sorted_results = sorted(successful_results, key=lambda x: x[1].trust_score.overall_score, reverse=True)
            
            print(f"\n🏆 Highest Trust Query:")
            best_id, best_result = sorted_results[0]
            print(f"   {queries[best_id]} (Score: {best_result.trust_score.overall_score:.2f})")
            
            print(f"\n⚠️ Lowest Trust Query:")
            worst_id, worst_result = sorted_results[-1]
            print(f"   {queries[worst_id]} (Score: {worst_result.trust_score.overall_score:.2f})")
    
    except Exception as e:
        print(f"❌ Batch processing failed: {e}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())