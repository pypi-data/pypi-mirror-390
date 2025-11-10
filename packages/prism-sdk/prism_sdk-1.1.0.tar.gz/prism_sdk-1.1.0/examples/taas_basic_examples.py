"""
TaaS Basic Examples - Trust-as-a-Service SDK Usage

This example demonstrates basic usage of the TaaS client for
trust verification, hallucination detection, source verification,
reasoning analysis, and content safety checks.
"""

from prism_sdk import TaaSClient


def verified_search_example():
    """Example: Verified search with trust scoring"""
    print("\n" + "="*60)
    print("VERIFIED SEARCH EXAMPLE")
    print("="*60)
    
    # Initialize TaaS client
    taas = TaaSClient(api_key="your-api-key-here")
    
    # Perform verified search
    query = "Is renewable energy more cost-effective than fossil fuels?"
    result = taas.verified_search(
        query=query,
        max_sources=10,
        include_citations=True,
        trust_threshold=0.7
    )
    
    print(f"\nQuery: {result.query}")
    print(f"\nAnswer:\n{result.answer}")
    print(f"\n📊 Trust Score: {result.trust_score:.2f}")
    print(f"📊 Confidence: {result.confidence_level}")
    
    print(f"\n📚 Sources ({len(result.sources)}):")
    for i, source in enumerate(result.sources[:5], 1):
        print(f"  {i}. {source.title}")
        print(f"     URL: {source.url}")
        print(f"     Trust: {source.trust_score:.2f} | Credibility: {source.credibility_score:.2f}")
    
    if result.citations:
        print(f"\n📖 Citations ({len(result.citations)}):")
        for i, citation in enumerate(result.citations[:3], 1):
            print(f"  {i}. {citation.title}")
            print(f"     Excerpt: {citation.excerpt[:100]}...")
    
    print(f"\n⚡ Processing Time: {result.processing_time_ms}ms")
    print(f"💰 Cost: ${result.cost_usd:.4f}")
    
    taas.close()


def hallucination_check_example():
    """Example: Check content for AI hallucinations"""
    print("\n" + "="*60)
    print("HALLUCINATION DETECTION EXAMPLE")
    print("="*60)
    
    taas = TaaSClient(api_key="your-api-key-here")
    
    # Text to check (contains intentional inaccuracies)
    text = """
    The Eiffel Tower was built in 1887 and stands at 350 meters tall.
    It was designed by Gustave Eiffel for the 1889 World's Fair in Paris.
    The tower is made entirely of copper and weighs approximately 15,000 tons.
    """
    
    report = taas.hallucination_check(
        text=text,
        include_recommendations=True
    )
    
    print(f"\n📝 Text analyzed: {len(text)} characters")
    print(f"\n⚠️  Hallucination Detected: {report.hallucination_detected}")
    print(f"📊 Risk Level: {report.risk_level}")
    print(f"📊 Confidence: {report.confidence:.2f}")
    
    print(f"\n🔍 Factual Claims Analysis ({len(report.factual_claims)}):")
    for i, claim in enumerate(report.factual_claims, 1):
        print(f"  {i}. {claim.claim}")
        print(f"     Verifiable: {claim.verifiable} | Risk: {claim.risk_level} | Confidence: {claim.confidence:.2f}")
    
    if report.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in report.recommendations:
            print(f"  • {rec}")
    
    print(f"\n⚡ Processing Time: {report.processing_time_ms}ms")
    print(f"💰 Cost: ${report.cost_usd:.4f}")
    
    taas.close()


def source_verification_example():
    """Example: Verify reliability of sources"""
    print("\n" + "="*60)
    print("SOURCE VERIFICATION EXAMPLE")
    print("="*60)
    
    taas = TaaSClient(api_key="your-api-key-here")
    
    # Sources to verify
    sources = [
        {
            "url": "https://www.nature.com/articles/example",
            "title": "Renewable Energy Cost Analysis"
        },
        {
            "url": "https://www.sciencedaily.com/example",
            "title": "Climate Change Research"
        },
        {
            "url": "https://randomsite.com/article",
            "title": "Unverified Claims"
        }
    ]
    
    report = taas.verify_sources(
        sources=sources,
        include_details=True
    )
    
    print(f"\n📊 Sources Analyzed: {report.sources_analyzed}")
    print(f"📊 Overall Reliability: {report.overall_reliability:.2f}")
    
    print(f"\n🔍 Individual Source Analysis:")
    for i, analysis in enumerate(report.source_analyses, 1):
        print(f"\n  {i}. {analysis.domain}")
        print(f"     URL: {analysis.url}")
        print(f"     Reliability: {analysis.reliability_score:.2f}")
        print(f"     Credibility: {analysis.credibility_score:.2f}")
        print(f"     Bias: {analysis.bias_assessment}")
        print(f"     Status: {analysis.verification_status}")
        if analysis.risk_factors:
            print(f"     Risk Factors: {', '.join(analysis.risk_factors)}")
    
    print(f"\n📈 Credibility Breakdown:")
    for category, score in report.credibility_breakdown.items():
        print(f"  • {category}: {score:.2f}")
    
    print(f"\n⚠️  Risk Summary:")
    for risk_type, count in report.risk_summary.items():
        print(f"  • {risk_type}: {count}")
    
    print(f"\n⚡ Processing Time: {report.processing_time_ms}ms")
    print(f"💰 Cost: ${report.cost_usd:.4f}")
    
    taas.close()


def reasoning_analysis_example():
    """Example: Analyze reasoning quality"""
    print("\n" + "="*60)
    print("REASONING ANALYSIS EXAMPLE")
    print("="*60)
    
    taas = TaaSClient(api_key="your-api-key-here")
    
    query = "Why is the sky blue?"
    response = """
    The sky appears blue because of a phenomenon called Rayleigh scattering.
    When sunlight enters Earth's atmosphere, it collides with gas molecules.
    Blue light has a shorter wavelength than other colors, so it scatters more.
    This scattered blue light reaches our eyes from all directions, making the sky appear blue.
    During sunset, the sky turns orange because the light travels through more atmosphere.
    """
    
    analysis = taas.analyze_reasoning(
        query=query,
        response=response,
        sources=[
            {"url": "https://physics.edu/rayleigh", "title": "Rayleigh Scattering Explained"}
        ]
    )
    
    print(f"\n📊 Reasoning Quality Scores:")
    print(f"  • Logical Consistency: {analysis.logical_consistency:.2f}")
    print(f"  • Evidence Quality: {analysis.evidence_quality:.2f}")
    print(f"  • Coherence: {analysis.coherence_score:.2f}")
    
    print(f"\n🔗 Reasoning Steps ({len(analysis.reasoning_steps)}):")
    for step in analysis.reasoning_steps:
        print(f"\n  Step {step.step_number}: {step.description}")
        print(f"    Logic: {step.logic_score:.2f} | Evidence: {step.evidence_quality:.2f}")
    
    if analysis.fallacies_detected:
        print(f"\n⚠️  Logical Fallacies Detected ({len(analysis.fallacies_detected)}):")
        for fallacy in analysis.fallacies_detected:
            print(f"\n  • {fallacy.fallacy_type}")
            print(f"    Description: {fallacy.description}")
            print(f"    Location: {fallacy.location}")
            print(f"    Severity: {fallacy.severity}")
    else:
        print(f"\n✅ No logical fallacies detected")
    
    if analysis.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in analysis.recommendations:
            print(f"  • {rec}")
    
    print(f"\n⚡ Processing Time: {analysis.processing_time_ms}ms")
    print(f"💰 Cost: ${analysis.cost_usd:.4f}")
    
    taas.close()


def content_safety_example():
    """Example: Check content safety"""
    print("\n" + "="*60)
    print("CONTENT SAFETY CHECK EXAMPLE")
    print("="*60)
    
    taas = TaaSClient(api_key="your-api-key-here")
    
    content = """
    This is a sample text that discusses various topics including technology,
    science, and social issues. It's important to analyze content for safety,
    bias, and personally identifiable information before publication.
    """
    
    report = taas.check_content_safety(
        content=content,
        check_bias=True,
        check_pii=True
    )
    
    print(f"\n📊 Safety Assessment:")
    print(f"  • Is Safe: {report.is_safe}")
    print(f"  • Safety Score: {report.safety_score:.2f}")
    
    if report.policy_violations:
        print(f"\n⚠️  Policy Violations:")
        for violation in report.policy_violations:
            print(f"  • {violation}")
    else:
        print(f"\n✅ No policy violations detected")
    
    if report.safety_issues:
        print(f"\n⚠️  Safety Issues ({len(report.safety_issues)}):")
        for issue in report.safety_issues:
            print(f"\n  • {issue.issue_type} ({issue.severity})")
            print(f"    {issue.description}")
            print(f"    Location: {issue.location}")
    else:
        print(f"\n✅ No safety issues detected")
    
    if report.bias_analysis:
        bias = report.bias_analysis
        print(f"\n🎭 Bias Analysis:")
        print(f"  • Bias Detected: {bias.bias_detected}")
        print(f"  • Bias Score: {bias.bias_score:.2f}")
        if bias.bias_types:
            print(f"  • Types: {', '.join(bias.bias_types)}")
    
    if report.pii_analysis:
        pii = report.pii_analysis
        print(f"\n🔒 PII Analysis:")
        print(f"  • PII Detected: {pii.pii_detected}")
        if pii.pii_types:
            print(f"  • Types: {', '.join(pii.pii_types)}")
    
    print(f"\n📊 Risk Categories:")
    for category, score in report.risk_categories.items():
        print(f"  • {category}: {score:.2f}")
    
    if report.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in report.recommendations:
            print(f"  • {rec}")
    
    print(f"\n⚡ Processing Time: {report.processing_time_ms}ms")
    print(f"💰 Cost: ${report.cost_usd:.4f}")
    
    taas.close()


if __name__ == "__main__":
    print("\n🔐 Prism SDK - TaaS Examples")
    print("Trust-as-a-Service demonstrations\n")
    
    # Run all examples
    # Note: Replace "your-api-key-here" with your actual API key
    
    try:
        verified_search_example()
        hallucination_check_example()
        source_verification_example()
        reasoning_analysis_example()
        content_safety_example()
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to:")
        print("1. Replace 'your-api-key-here' with your actual API key")
        print("2. Ensure the API server is running")
        print("3. Check your network connection")
