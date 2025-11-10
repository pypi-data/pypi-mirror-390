"""
TaaS Async & Batch Examples - Advanced TaaS Usage

This example demonstrates async operations and batch processing
for efficient handling of multiple requests concurrently.
"""

import asyncio
from prism_sdk import TaaSClient


async def async_verified_search_example():
    """Example: Async verified search"""
    print("\n" + "="*60)
    print("ASYNC VERIFIED SEARCH EXAMPLE")
    print("="*60)
    
    async with TaaSClient(api_key="your-api-key-here") as taas:
        queries = [
            "What is quantum computing?",
            "How does renewable energy work?",
            "Explain blockchain technology"
        ]
        
        print(f"\nProcessing {len(queries)} queries concurrently...")
        
        # Process all queries concurrently
        tasks = [taas.verified_search_async(q) for q in queries]
        results = await asyncio.gather(*tasks)
        
        for i, (query, result) in enumerate(zip(queries, results), 1):
            print(f"\n{'─'*60}")
            print(f"Query {i}: {query}")
            print(f"Trust Score: {result.trust_score:.2f}")
            print(f"Answer: {result.answer[:200]}...")
            print(f"Sources: {len(result.sources)}")
            print(f"Processing Time: {result.processing_time_ms}ms")


async def batch_hallucination_check_example():
    """Example: Batch hallucination detection"""
    print("\n" + "="*60)
    print("BATCH HALLUCINATION CHECK EXAMPLE")
    print("="*60)
    
    async with TaaSClient(api_key="your-api-key-here") as taas:
        texts = [
            "The Eiffel Tower is 330 meters tall and was completed in 1889.",
            "Python was created in 1991 by Guido van Rossum at CWI in the Netherlands.",
            "The Great Wall of China is visible from the Moon with the naked eye.",
            "Water boils at 100°C at sea level under standard atmospheric pressure.",
            "Albert Einstein invented the telephone in 1876."
        ]
        
        print(f"\nChecking {len(texts)} texts for hallucinations...")
        print("(Processing up to 5 concurrent requests)\n")
        
        # Batch process with max 5 concurrent requests
        results = await taas.batch_hallucination_check(
            texts=texts,
            include_recommendations=True,
            max_workers=5
        )
        
        for i, batch_result in enumerate(results, 1):
            print(f"\n{'─'*60}")
            print(f"Text {i}: {batch_result.text[:80]}...")
            
            if batch_result.error:
                print(f"❌ Error: {batch_result.error}")
            else:
                report = batch_result.result
                print(f"Hallucination Detected: {report.hallucination_detected}")
                print(f"Risk Level: {report.risk_level}")
                print(f"Confidence: {report.confidence:.2f}")
                print(f"Claims Analyzed: {len(report.factual_claims)}")
                
                # Show suspicious claims
                suspicious = [c for c in report.factual_claims if c.risk_level in ["high", "medium"]]
                if suspicious:
                    print(f"\n⚠️  Suspicious Claims:")
                    for claim in suspicious:
                        print(f"  • {claim.claim} (Risk: {claim.risk_level})")


async def batch_source_verification_example():
    """Example: Batch source verification"""
    print("\n" + "="*60)
    print("BATCH SOURCE VERIFICATION EXAMPLE")
    print("="*60)
    
    async with TaaSClient(api_key="your-api-key-here") as taas:
        # Multiple source lists to verify
        source_lists = [
            # Academic sources
            [
                {"url": "https://www.nature.com/articles/example1", "title": "Nature Article"},
                {"url": "https://science.sciencemag.org/example", "title": "Science Magazine"}
            ],
            # News sources
            [
                {"url": "https://www.bbc.com/news/example", "title": "BBC News"},
                {"url": "https://www.reuters.com/article/example", "title": "Reuters"}
            ],
            # Mixed credibility
            [
                {"url": "https://www.who.int/example", "title": "WHO Report"},
                {"url": "https://randomsite.com/article", "title": "Random Blog"}
            ]
        ]
        
        print(f"\nVerifying {len(source_lists)} source lists...")
        print(f"Total sources: {sum(len(s) for s in source_lists)}\n")
        
        # Batch verify all source lists
        results = await taas.batch_verify_sources(
            source_lists=source_lists,
            include_details=True,
            max_workers=3
        )
        
        for i, batch_result in enumerate(results, 1):
            print(f"\n{'─'*60}")
            print(f"Source List {i}:")
            
            if batch_result.error:
                print(f"❌ Error: {batch_result.error}")
            else:
                report = batch_result.result
                print(f"Sources Analyzed: {report.sources_analyzed}")
                print(f"Overall Reliability: {report.overall_reliability:.2f}")
                
                print(f"\nSources:")
                for analysis in report.source_analyses:
                    print(f"  • {analysis.domain}")
                    print(f"    Reliability: {analysis.reliability_score:.2f}")
                    print(f"    Status: {analysis.verification_status}")


async def concurrent_mixed_operations_example():
    """Example: Mix different TaaS operations concurrently"""
    print("\n" + "="*60)
    print("CONCURRENT MIXED OPERATIONS EXAMPLE")
    print("="*60)
    
    async with TaaSClient(api_key="your-api-key-here") as taas:
        print("\nRunning different TaaS operations concurrently...")
        
        # Create different types of tasks
        tasks = {
            "verified_search": taas.verified_search_async("What is AI?"),
            "hallucination": taas.hallucination_check_async("The Moon is made of cheese."),
            "sources": taas.verify_sources_async([
                {"url": "https://www.nature.com/article", "title": "Article"}
            ]),
            "reasoning": taas.analyze_reasoning_async(
                query="Why is water wet?",
                response="Water is wet because it has high surface tension."
            ),
            "safety": taas.check_content_safety_async("This is a test content.")
        }
        
        # Execute all operations concurrently
        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await task
                print(f"✅ {name}: Completed")
            except Exception as e:
                print(f"❌ {name}: Failed - {e}")
        
        # Display summary
        print(f"\n{'─'*60}")
        print("Results Summary:")
        
        if "verified_search" in results:
            print(f"  • Verified Search: Trust Score = {results['verified_search'].trust_score:.2f}")
        
        if "hallucination" in results:
            print(f"  • Hallucination Check: Risk = {results['hallucination'].risk_level}")
        
        if "sources" in results:
            print(f"  • Source Verification: Reliability = {results['sources'].overall_reliability:.2f}")
        
        if "reasoning" in results:
            print(f"  • Reasoning Analysis: Logic = {results['reasoning'].logical_consistency:.2f}")
        
        if "safety" in results:
            print(f"  • Content Safety: Safe = {results['safety'].is_safe}")


async def parallel_hallucination_analysis_example():
    """Example: Parallel analysis with detailed reporting"""
    print("\n" + "="*60)
    print("PARALLEL HALLUCINATION ANALYSIS")
    print("="*60)
    
    async with TaaSClient(api_key="your-api-key-here") as taas:
        # Different content types to analyze
        contents = {
            "scientific": """
                Water molecules consist of two hydrogen atoms and one oxygen atom.
                The chemical formula is H2O. Water has a boiling point of 100°C
                at standard atmospheric pressure.
            """,
            "historical": """
                The Declaration of Independence was signed on July 4, 1776.
                George Washington was the first President of the United States,
                serving from 1789 to 1797.
            """,
            "mixed_accuracy": """
                The speed of light is approximately 300,000 km/s.
                Albert Einstein developed the theory of relativity in 1905.
                The human brain has 100 trillion neurons.
            """,
            "fiction": """
                Dragons can breathe fire due to a special organ in their throat.
                Wizards use wands made from magical wood to cast spells.
                Time travel is possible using a flux capacitor.
            """
        }
        
        print(f"\nAnalyzing {len(contents)} different content types...\n")
        
        # Analyze all content types in parallel
        tasks = [
            taas.hallucination_check_async(text, include_recommendations=True)
            for text in contents.values()
        ]
        results = await asyncio.gather(*tasks)
        
        # Display detailed comparison
        print(f"\n{'═'*60}")
        print("COMPARATIVE ANALYSIS")
        print(f"{'═'*60}")
        
        for (content_type, text), result in zip(contents.items(), results):
            print(f"\n{content_type.upper()}")
            print(f"{'─'*60}")
            print(f"Hallucination Detected: {result.hallucination_detected}")
            print(f"Risk Level: {result.risk_level}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Claims: {len(result.factual_claims)}")
            
            # Categorize claims by risk
            high_risk = [c for c in result.factual_claims if c.risk_level == "high"]
            medium_risk = [c for c in result.factual_claims if c.risk_level == "medium"]
            low_risk = [c for c in result.factual_claims if c.risk_level == "low"]
            
            print(f"\nRisk Distribution:")
            print(f"  🔴 High Risk: {len(high_risk)}")
            print(f"  🟡 Medium Risk: {len(medium_risk)}")
            print(f"  🟢 Low Risk: {len(low_risk)}")
            
            if high_risk:
                print(f"\n  High Risk Claims:")
                for claim in high_risk[:2]:  # Show first 2
                    print(f"    • {claim.claim}")


async def rate_limiting_example():
    """Example: Handling rate limits with retries"""
    print("\n" + "="*60)
    print("RATE LIMITING & RETRY EXAMPLE")
    print("="*60)
    
    async with TaaSClient(
        api_key="your-api-key-here",
        timeout=60.0,
        max_retries=3,
        retry_delay=2.0
    ) as taas:
        # Simulate many requests
        queries = [f"Query {i+1}: What is AI?" for i in range(20)]
        
        print(f"\nSending {len(queries)} requests...")
        print("(SDK will automatically handle rate limits)\n")
        
        successful = 0
        failed = 0
        
        # Process in batches of 5
        batch_size = 5
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}...")
            
            tasks = [taas.verified_search_async(q) for q in batch]
            
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        failed += 1
                        print(f"  ❌ Failed: {type(result).__name__}")
                    else:
                        successful += 1
                        print(f"  ✅ Success")
                
                # Small delay between batches
                if i + batch_size < len(queries):
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"  ❌ Batch failed: {e}")
                failed += len(batch)
        
        print(f"\n{'─'*60}")
        print(f"Results: {successful} successful, {failed} failed")
        print(f"Success Rate: {successful/len(queries)*100:.1f}%")


async def main():
    """Run all async examples"""
    print("\n🔐 Prism SDK - Async & Batch TaaS Examples")
    print("Advanced concurrent operations\n")
    
    try:
        await async_verified_search_example()
        await batch_hallucination_check_example()
        await batch_source_verification_example()
        await concurrent_mixed_operations_example()
        await parallel_hallucination_analysis_example()
        await rate_limiting_example()
        
        print("\n" + "="*60)
        print("✅ All async examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to:")
        print("1. Replace 'your-api-key-here' with your actual API key")
        print("2. Ensure the API server is running")
        print("3. Check your network connection")


if __name__ == "__main__":
    # Run async examples
    asyncio.run(main())
