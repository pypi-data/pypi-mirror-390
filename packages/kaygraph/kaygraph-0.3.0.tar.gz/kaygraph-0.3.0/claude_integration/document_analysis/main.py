"""
Enterprise Document Analysis System - Main Entry Point.

This module demonstrates the complete document analysis system workflow
with real-world scenarios and comprehensive testing.
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from .nodes import DocumentMetadata, DocumentContent, DocumentType
from .graphs import create_workflow, get_available_workflows
from .utils import (
    TextExtractor,
    ComplianceRules,
    RiskAssessmentFramework,
    ReportTemplate,
    calculate_document_statistics,
    extract_document_structure
)


def setup_logging():
    """Setup logging for the document analysis system."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('document_analysis.log')
        ]
    )


async def demo_single_document_analysis():
    """Demonstrate processing a single document through the analysis pipeline."""
    print("\n" + "="*70)
    print("DEMO 1: Single Document Analysis")
    print("="*70)

    # Create the main workflow
    workflow = create_workflow("document_analysis")

    # Create sample document (simulating a business contract)
    sample_document = {
        "id": "doc_demo_001",
        "filename": "service_agreement_2024.pdf",
        "file_type": "pdf",
        "author": "Legal Department",
        "department": "Legal",
        "classification": "confidential",
        "content": """
SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of January 1, 2024,
between Acme Corporation ("Client") located at 123 Business Ave, Tech City, CA 94000,
and CloudTech Solutions ("Provider") located at 456 Innovation Dr, San Francisco, CA 94105.

1. SERVICES
Provider agrees to provide cloud infrastructure services including:
- 24/7 system monitoring and support
- 99.99% uptime SLA guarantee
- Data backup and disaster recovery
- Security compliance (SOC 2, ISO 27001)

2. PAYMENT TERMS
Client agrees to pay $50,000 monthly for services rendered. Payment is due within
30 days of invoice date. Late payments will incur 1.5% monthly interest.

3. DATA PROTECTION
Provider will comply with GDPR, CCPA, and HIPAA regulations. All customer data
will be encrypted at rest and in transit using AES-256 encryption.

4. CONFIDENTIALITY
Both parties agree to maintain confidentiality of proprietary information.
This includes but not limited to: API keys, passwords, customer lists, and trade secrets.

5. TERMINATION
Either party may terminate with 90 days written notice. Upon termination, Provider
will assist with data migration for up to 30 days.

Contact: legal@acmecorp.com | Phone: 555-123-4567

Signed:
John Doe, CEO, Acme Corporation
Jane Smith, VP Sales, CloudTech Solutions
        """,
        "tags": ["contract", "legal", "saas", "cloud"],
        "created_at": "2024-01-01T00:00:00Z"
    }

    print(f"📄 Processing document: {sample_document['filename']}")
    print(f"   Type: {sample_document['file_type']}")
    print(f"   Classification: {sample_document['classification']}")
    print(f"   Department: {sample_document['department']}")

    # Initialize shared context
    shared_context = {
        "incoming_document": sample_document,
        "start_time": time.time(),
        "processing_stage": "starting"
    }

    try:
        # Run the workflow
        print("\n⚙️  Processing document through analysis pipeline...")
        result = await workflow.run(
            start_node_name="document_ingestion",
            shared=shared_context
        )

        # Display results
        print("\n" + "-"*50)
        print("📊 ANALYSIS RESULTS")
        print("-"*50)

        # Document metadata
        metadata = shared_context.get("document_metadata")
        if metadata:
            print(f"\n✅ Document Metadata:")
            print(f"   ID: {metadata.id}")
            print(f"   File Type: {metadata.file_type.value}")
            print(f"   Size: {metadata.file_size:,} bytes")
            print(f"   Language: {metadata.language}")

        # Content analysis
        content_analysis = shared_context.get("content_analysis")
        if content_analysis:
            print(f"\n✅ Content Analysis:")
            print(f"   Summary: {content_analysis.get('summary', 'N/A')[:200]}...")
            print(f"   Document Type: {content_analysis.get('document_type', 'N/A')}")
            print(f"   Topics: {', '.join(content_analysis.get('topics', []))}")
            print(f"   Sentiment: {content_analysis.get('sentiment', 'N/A')}")
            print(f"   Complexity: {content_analysis.get('complexity', 'N/A')}")
            print(f"   Target Audience: {content_analysis.get('target_audience', 'N/A')}")

        # Key insights
        insights = shared_context.get("extracted_insights")
        if insights:
            print(f"\n✅ Key Insights:")
            key_insights = insights.get("key_insights", [])
            for i, insight in enumerate(key_insights[:3], 1):
                print(f"   {i}. {insight.get('insight', 'N/A')}")
                print(f"      Confidence: {insight.get('confidence', 0):.2f}")

        # Compliance results
        compliance = shared_context.get("compliance_results")
        if compliance:
            print(f"\n✅ Compliance Assessment:")
            print(f"   Overall Score: {compliance.get('overall_compliance_score', 0):.1%}")
            violations = compliance.get("violations", [])
            print(f"   Violations Found: {len(violations)}")
            if violations:
                for violation in violations[:3]:
                    print(f"   - [{violation.get('severity', 'N/A')}] {violation.get('type', 'N/A')}")

        # Final report
        report = shared_context.get("analysis_report")
        if report:
            print(f"\n✅ Report Generated:")
            print(f"   Report ID: {report.get('report_id', 'N/A')}")
            print(f"   Processing Time: {report['processing_metrics']['processing_time']:.2f}s")
            print(f"   Word Count: {report['processing_metrics']['word_count']:,}")
            print(f"   Reading Time: {report['processing_metrics']['reading_time']} minutes")

        processing_time = time.time() - shared_context["start_time"]
        print(f"\n⏱️  Total Processing Time: {processing_time:.2f}s")
        print("✅ Document analysis completed successfully!")

    except Exception as e:
        print(f"❌ Error processing document: {e}")
        import traceback
        traceback.print_exc()


async def demo_batch_document_processing():
    """Demonstrate batch processing of multiple documents."""
    print("\n" + "="*70)
    print("DEMO 2: Batch Document Processing")
    print("="*70)

    # Create batch workflow
    workflow = create_workflow("batch_processing")

    # Create sample batch of documents
    batch_documents = [
        {
            "id": "batch_001",
            "filename": "quarterly_report_Q1_2024.pdf",
            "file_type": "pdf",
            "content": "Q1 2024 Financial Report: Revenue increased by 15% compared to Q4 2023..."
        },
        {
            "id": "batch_002",
            "filename": "product_roadmap_2024.docx",
            "file_type": "docx",
            "content": "Product Development Roadmap: New features planned for 2024 include AI integration..."
        },
        {
            "id": "batch_003",
            "filename": "customer_feedback_analysis.txt",
            "file_type": "txt",
            "content": "Customer Satisfaction Survey Results: 87% of customers rated our service as excellent..."
        },
        {
            "id": "batch_004",
            "filename": "security_audit_report.pdf",
            "file_type": "pdf",
            "content": "Security Audit Findings: All systems passed security compliance checks..."
        },
        {
            "id": "batch_005",
            "filename": "market_analysis_2024.html",
            "file_type": "html",
            "content": "Market Analysis: Industry growth projected at 12% annually through 2025..."
        }
    ]

    print(f"📚 Processing batch of {len(batch_documents)} documents")
    for doc in batch_documents:
        print(f"   • {doc['filename']}")

    shared_context = {
        "batch_documents": batch_documents,
        "start_time": time.time()
    }

    try:
        # Run batch workflow
        print("\n⚙️  Processing documents in parallel...")
        result = await workflow.run(
            start_node_name="batch_document_ingestion",
            shared=shared_context
        )

        # Display batch results
        print("\n" + "-"*50)
        print("📊 BATCH PROCESSING RESULTS")
        print("-"*50)

        # Batch statistics
        batch_stats = shared_context.get("batch_stats", {})
        if batch_stats:
            print(f"\n✅ Batch Statistics:")
            print(f"   Total Documents: {batch_stats.get('total', 0)}")
            print(f"   Valid Documents: {batch_stats.get('valid', 0)}")
            print(f"   Invalid Documents: {batch_stats.get('invalid', 0)}")

        # Cross-document insights
        cross_insights = shared_context.get("cross_document_insights", {})
        if cross_insights:
            print(f"\n✅ Cross-Document Insights:")
            print(f"   Unique Topics: {', '.join(cross_insights.get('unique_topics', []))}")
            print(f"   Sentiment Distribution: {cross_insights.get('sentiment_distribution', {})}")

            # Cross-references
            cross_refs = cross_insights.get("cross_references", [])
            if cross_refs:
                print(f"   Cross-References Found: {len(cross_refs)}")
                for ref in cross_refs[:3]:
                    print(f"   - {ref['doc1']} ↔ {ref['doc2']}: {', '.join(ref['common_topics'])}")

        processing_time = time.time() - shared_context["start_time"]
        print(f"\n⏱️  Total Batch Processing Time: {processing_time:.2f}s")
        print(f"📊 Average Time per Document: {processing_time/len(batch_documents):.2f}s")

    except Exception as e:
        print(f"❌ Error in batch processing: {e}")


async def demo_compliance_assessment():
    """Demonstrate compliance and regulatory assessment workflow."""
    print("\n" + "="*70)
    print("DEMO 3: Compliance Assessment")
    print("="*70)

    # Create compliance workflow
    workflow = create_workflow("compliance_assessment")

    # Create sample document with compliance concerns
    compliance_document = {
        "id": "compliance_demo_001",
        "filename": "data_processing_agreement.pdf",
        "file_type": "pdf",
        "department": "Legal",
        "classification": "confidential",
        "content": """
DATA PROCESSING AGREEMENT

This agreement covers the processing of personal data including:
- Customer names and email addresses (john.doe@example.com, jane.smith@company.com)
- Phone numbers (555-123-4567, 555-987-6543)
- Credit card information for payment processing
- Social Security Numbers: 123-45-6789 (example)
- Medical records and health information
- API Keys: sk-proj-abc123xyz789
- Database passwords: MyS3cur3P@ssw0rd!

All data must be handled in compliance with:
- GDPR (General Data Protection Regulation)
- CCPA (California Consumer Privacy Act)
- HIPAA (Health Insurance Portability and Accountability Act)
- PCI DSS (Payment Card Industry Data Security Standard)

Data retention period: 7 years
Data encryption: AES-256
Access control: Role-based with MFA

Contact DPO: privacy@company.com
        """,
        "tags": ["compliance", "gdpr", "data-protection", "legal"]
    }

    print(f"🔒 Processing compliance-sensitive document: {compliance_document['filename']}")
    print(f"   Department: {compliance_document['department']}")
    print(f"   Classification: {compliance_document['classification']}")

    # Use compliance utilities
    compliance_rules = ComplianceRules()
    risk_framework = RiskAssessmentFramework()

    shared_context = {
        "incoming_document": compliance_document,
        "document_content": DocumentContent(text=compliance_document["content"]),
        "start_time": time.time()
    }

    try:
        # Run compliance workflow
        print("\n⚙️  Running compliance assessment...")
        result = await workflow.run(
            start_node_name="document_ingestion",
            shared=shared_context
        )

        # Check for compliance violations using utilities
        print("\n🔍 Checking for compliance violations...")
        violations = await compliance_rules.check_document(compliance_document["content"])

        print(f"\n⚠️  Found {len(violations)} compliance violations:")
        # Group violations by severity
        by_severity = {}
        for violation in violations:
            severity = violation.get("severity", "unknown")
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(violation)

        for severity in ["critical", "high", "medium", "low"]:
            if severity in by_severity:
                print(f"\n   {severity.upper()} Severity ({len(by_severity[severity])} issues):")
                for v in by_severity[severity][:2]:  # Show first 2 of each severity
                    print(f"   - {v['rule_name']}: {v['category']}")
                    print(f"     Remediation: {v['remediation']}")

        # Risk assessment
        risk_analysis = await risk_framework.assess_document_risk({
            "classification": compliance_document["classification"],
            "compliance_violations": violations
        })

        print(f"\n📊 Risk Assessment:")
        print(f"   Overall Risk Level: {risk_analysis['overall_risk_level'].upper()}")
        print(f"   Risk Score: {risk_analysis['risk_score']:.1f}/100")
        print(f"   Risk Factors: {len(risk_analysis['risk_factors'])}")

        print(f"\n📋 Recommendations:")
        for i, rec in enumerate(risk_analysis['recommendations'][:3], 1):
            print(f"   {i}. {rec}")

        processing_time = time.time() - shared_context["start_time"]
        print(f"\n⏱️  Compliance Assessment Time: {processing_time:.2f}s")

    except Exception as e:
        print(f"❌ Error in compliance assessment: {e}")


async def demo_executive_reporting():
    """Demonstrate executive-level reporting workflow."""
    print("\n" + "="*70)
    print("DEMO 4: Executive Reporting")
    print("="*70)

    # Create executive reporting workflow
    workflow = create_workflow("executive_reporting")

    # Create sample strategic document
    strategic_document = {
        "id": "exec_demo_001",
        "filename": "strategic_plan_2024_2026.pdf",
        "file_type": "pdf",
        "department": "Executive",
        "classification": "confidential",
        "content": """
STRATEGIC PLAN 2024-2026

Executive Summary:
Our three-year strategic plan focuses on digital transformation, market expansion,
and operational excellence. Key objectives include achieving $500M revenue by 2026,
expanding into 5 new international markets, and reducing operational costs by 20%.

Strategic Pillars:

1. Digital Innovation
   - Implement AI-driven customer service (Q2 2024)
   - Launch mobile-first platform (Q3 2024)
   - Develop predictive analytics capabilities (Q1 2025)
   Investment: $50M | Expected ROI: 35%

2. Market Expansion
   - Enter European markets (Germany, France, UK)
   - Establish Asia-Pacific presence (Japan, Singapore)
   - Strategic acquisitions budget: $100M
   Investment: $150M | Expected ROI: 25%

3. Operational Excellence
   - Automate 60% of manual processes
   - Reduce customer acquisition cost by 30%
   - Improve employee productivity by 25%
   Investment: $30M | Expected ROI: 45%

Financial Projections:
- 2024: Revenue $350M, EBITDA $70M (20%)
- 2025: Revenue $425M, EBITDA $95M (22%)
- 2026: Revenue $500M, EBITDA $125M (25%)

Risk Factors:
- Market competition intensifying
- Regulatory compliance costs increasing
- Technology implementation challenges
- Talent retention in competitive market

Success Metrics:
- Customer satisfaction score > 90%
- Employee engagement score > 85%
- Market share growth > 5% annually
- Digital revenue > 60% of total

Board Approval Required for:
- Acquisitions > $10M
- New market entry
- Major technology investments > $5M
        """,
        "tags": ["strategy", "executive", "financial", "planning"]
    }

    print(f"📈 Processing strategic document: {strategic_document['filename']}")
    print(f"   Department: {strategic_document['department']}")
    print(f"   Classification: {strategic_document['classification']}")

    shared_context = {
        "incoming_document": strategic_document,
        "start_time": time.time()
    }

    try:
        # Run executive reporting workflow
        print("\n⚙️  Generating executive analysis...")
        result = await workflow.run(
            start_node_name="document_ingestion",
            shared=shared_context
        )

        # Display executive summary
        exec_summary = shared_context.get("executive_summary", {})
        if exec_summary:
            print("\n" + "-"*50)
            print("📊 EXECUTIVE SUMMARY")
            print("-"*50)

            print(f"\n{exec_summary.get('executive_summary', 'N/A')}")

            print(f"\n📈 Key Metrics:")
            metrics = exec_summary.get("key_metrics", {})
            for key, value in metrics.items():
                print(f"   • {key.replace('_', ' ').title()}: {value}")

            print(f"\n🎯 Strategic Recommendations:")
            for i, rec in enumerate(exec_summary.get("strategic_recommendations", [])[:3], 1):
                print(f"   {i}. {rec}")

            print(f"\n⚡ Decision Points:")
            for i, decision in enumerate(exec_summary.get("decision_points", [])[:3], 1):
                print(f"   {i}. {decision}")

        # Visual insights
        visual_insights = shared_context.get("visual_insights", {})
        if visual_insights:
            print(f"\n📊 Visual Insights Prepared:")
            charts = visual_insights.get("charts", [])
            print(f"   Charts Generated: {len(charts)}")
            for chart in charts:
                print(f"   • {chart['type'].upper()}: {chart['title']}")

            print(f"\n📈 Key Trends:")
            for trend in visual_insights.get("trends", [])[:3]:
                print(f"   • {trend}")

        # Generate executive report using template
        reporter = ReportTemplate()
        analysis_results = {
            "document_id": strategic_document["id"],
            "document_type": "strategic_plan",
            "classification": strategic_document["classification"],
            "executive_summary": exec_summary.get("executive_summary", ""),
            "key_findings": [
                "Digital transformation initiative on track",
                "Market expansion opportunities identified",
                "Operational efficiency gains achievable"
            ],
            "overall_risk_level": "medium",
            "risk_score": 65,
            "recommendations": exec_summary.get("strategic_recommendations", []),
            "next_steps": exec_summary.get("decision_points", [])
        }

        report_text = reporter.generate_executive_report(analysis_results)
        print(f"\n📄 Executive Report Generated:")
        print("   (First 500 characters)")
        print(report_text[:500] + "...")

        processing_time = time.time() - shared_context["start_time"]
        print(f"\n⏱️  Executive Analysis Time: {processing_time:.2f}s")

    except Exception as e:
        print(f"❌ Error in executive reporting: {e}")


async def demo_document_statistics():
    """Demonstrate document statistics and analysis utilities."""
    print("\n" + "="*70)
    print("DEMO 5: Document Statistics & Utilities")
    print("="*70)

    sample_text = """
    Artificial Intelligence (AI) is transforming the business landscape.
    Companies are leveraging machine learning algorithms to optimize operations,
    enhance customer experiences, and drive innovation. The global AI market
    is expected to reach $390 billion by 2025, with healthcare, finance, and
    retail sectors leading adoption.

    Key benefits include:
    - Automated decision-making
    - Predictive analytics
    - Natural language processing
    - Computer vision applications

    Visit our website at https://example.com for more information.
    Contact us at info@example.com or call 555-123-4567.
    """

    print("📊 Analyzing document statistics and structure...")

    # Calculate statistics
    stats = calculate_document_statistics(sample_text)
    print(f"\n📈 Document Statistics:")
    print(f"   Word Count: {stats['word_count']}")
    print(f"   Character Count: {stats['character_count']}")
    print(f"   Sentence Count: {stats['sentence_count']}")
    print(f"   Average Word Length: {stats['average_word_length']:.1f}")
    print(f"   Average Sentence Length: {stats['average_sentence_length']:.1f}")
    print(f"   Reading Time: {stats['reading_time_minutes']} minute(s)")
    print(f"   Complexity Score: {stats['complexity_score']:.2f} (0-1 scale)")

    # Extract structure
    structure = extract_document_structure(sample_text)
    print(f"\n🏗️ Document Structure:")
    print(f"   URLs Found: {len(structure['urls'])}")
    for url in structure['urls']:
        print(f"   • {url}")
    print(f"   Lists Found: {len(structure['lists'])}")
    for item in structure['lists'][:3]:
        print(f"   • {item}")
    print(f"   Quoted Text: {len(structure['quotes'])}")

    # Test text extraction
    extractor = TextExtractor()
    print(f"\n📄 Text Extraction Capabilities:")
    print(f"   Supported Formats: {', '.join(extractor.config.supported_formats)}")
    print(f"   Max File Size: {extractor.config.max_file_size:,} bytes")
    print(f"   OCR Enabled: {extractor.config.ocr_enabled}")

    print("\n✅ Document utilities demonstration complete!")


async def run_all_demos():
    """Run all demonstration scenarios."""
    print("🚀 Enterprise Document Analysis System - Complete Demo Suite")
    print("=" * 80)

    try:
        # Run all demo scenarios
        await demo_single_document_analysis()
        await demo_batch_document_processing()
        await demo_compliance_assessment()
        await demo_executive_reporting()
        await demo_document_statistics()

        print("\n" + "="*80)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*80)

        print("\n📋 SUMMARY OF CAPABILITIES DEMONSTRATED:")
        print("✅ Single document deep analysis with AI insights")
        print("✅ Batch processing with cross-document analysis")
        print("✅ Compliance checking and risk assessment")
        print("✅ Executive-level reporting and visualization")
        print("✅ Document statistics and structure extraction")
        print("✅ Multiple workflow patterns (linear, parallel, conditional)")
        print("✅ Integration with Claude AI for sophisticated analysis")
        print("✅ Production-ready error handling and logging")

    except Exception as e:
        print(f"\n❌ Demo suite failed: {e}")
        import traceback
        traceback.print_exc()


def print_available_workflows():
    """Print information about available workflows."""
    print("\n📋 AVAILABLE WORKFLOWS:")
    workflows = get_available_workflows()
    for name, creator in workflows.items():
        print(f"   - {name}: {creator.__name__}")


if __name__ == "__main__":
    """Main entry point for the document analysis system demo."""
    setup_logging()

    print("📄 Enterprise Document Analysis System with Claude + KayGraph")
    print("=" * 70)

    # Print available workflows
    print_available_workflows()

    # Run demo
    asyncio.run(run_all_demos())