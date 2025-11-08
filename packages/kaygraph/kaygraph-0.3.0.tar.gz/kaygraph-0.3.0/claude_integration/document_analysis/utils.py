"""
Document Analysis Utilities.

This module contains utilities specific to document processing and analysis,
including text extraction, document parsing, compliance rules, and report templates.
"""

import os
import re
import json
import hashlib
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import mimetypes


@dataclass
class TextExtractionConfig:
    """Configuration for text extraction."""
    max_file_size: int = 10_000_000  # 10MB
    supported_formats: List[str] = field(default_factory=lambda: ["txt", "pdf", "docx", "html", "json", "csv", "md"])
    extract_tables: bool = True
    extract_images: bool = False
    extract_metadata: bool = True
    ocr_enabled: bool = False
    language: str = "en"


class TextExtractor:
    """
    Extracts text content from various document formats.

    This class handles text extraction from different file types,
    preserving structure where possible.
    """

    def __init__(self, config: TextExtractionConfig = None):
        self.config = config or TextExtractionConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def extract_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text content from a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing extracted text and metadata
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.config.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.config.max_file_size})")

        # Detect file type
        file_type = file_path.suffix.lower().lstrip('.')
        mime_type, _ = mimetypes.guess_type(str(file_path))

        if file_type not in self.config.supported_formats:
            raise ValueError(f"Unsupported file format: {file_type}")

        # Extract based on file type
        extractors = {
            'txt': self._extract_txt,
            'pdf': self._extract_pdf,
            'docx': self._extract_docx,
            'html': self._extract_html,
            'json': self._extract_json,
            'csv': self._extract_csv,
            'md': self._extract_markdown
        }

        extractor = extractors.get(file_type, self._extract_txt)
        content = await extractor(file_path)

        # Extract metadata
        metadata = {
            'filename': file_path.name,
            'file_type': file_type,
            'mime_type': mime_type,
            'file_size': file_size,
            'created_at': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            'checksum': self._calculate_checksum(file_path)
        }

        return {
            'content': content,
            'metadata': metadata,
            'extraction_timestamp': datetime.now().isoformat()
        }

    async def _extract_txt(self, file_path: Path) -> str:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()

    async def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        # Mock implementation - in production, use PyPDF2 or pdfplumber
        self.logger.info(f"PDF extraction for: {file_path}")
        return f"[PDF content would be extracted from {file_path.name}]"

    async def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        # Mock implementation - in production, use python-docx
        self.logger.info(f"DOCX extraction for: {file_path}")
        return f"[DOCX content would be extracted from {file_path.name}]"

    async def _extract_html(self, file_path: Path) -> str:
        """Extract text from HTML file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Simple HTML tag removal (in production, use BeautifulSoup)
        text = re.sub('<[^<]+?>', '', html_content)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    async def _extract_json(self, file_path: Path) -> str:
        """Extract text from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return json.dumps(data, indent=2)

    async def _extract_csv(self, file_path: Path) -> str:
        """Extract text from CSV file."""
        # Mock implementation - in production, use pandas
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    async def _extract_markdown(self, file_path: Path) -> str:
        """Extract text from Markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


@dataclass
class ComplianceRule:
    """Represents a compliance rule."""
    id: str
    name: str
    category: str
    description: str
    regex_patterns: List[str]
    severity: str  # low, medium, high, critical
    remediation: str
    tags: List[str] = field(default_factory=list)


class ComplianceRules:
    """
    Manages compliance rules for document checking.

    This class provides a framework for checking documents
    against various compliance requirements.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.rules = self._load_default_rules()

    def _load_default_rules(self) -> List[ComplianceRule]:
        """Load default compliance rules."""
        return [
            ComplianceRule(
                id="gdpr_001",
                name="GDPR Personal Data",
                category="data_privacy",
                description="Check for personal data that requires GDPR compliance",
                regex_patterns=[
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
                    r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'  # Phone
                ],
                severity="high",
                remediation="Ensure proper consent and data protection measures",
                tags=["gdpr", "privacy", "personal_data"]
            ),
            ComplianceRule(
                id="pci_001",
                name="PCI DSS Credit Card Data",
                category="financial",
                description="Check for credit card information",
                regex_patterns=[
                    r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12})\b',  # Credit card
                    r'\b\d{3,4}\b'  # CVV
                ],
                severity="critical",
                remediation="Remove or encrypt credit card data",
                tags=["pci", "financial", "credit_card"]
            ),
            ComplianceRule(
                id="hipaa_001",
                name="HIPAA Protected Health Information",
                category="healthcare",
                description="Check for protected health information",
                regex_patterns=[
                    r'\b(?:patient|diagnosis|treatment|medical|health)\b',
                    r'\b\d{3}-\d{2}-\d{4}\b'  # SSN
                ],
                severity="high",
                remediation="Ensure HIPAA compliance for health information",
                tags=["hipaa", "healthcare", "phi"]
            ),
            ComplianceRule(
                id="sec_001",
                name="Security Credentials",
                category="security",
                description="Check for exposed credentials",
                regex_patterns=[
                    r'(?i)(api[_-]?key|apikey|secret[_-]?key|password|pwd|token|bearer)\s*[:=]\s*["\']?[\w-]+["\']?',
                    r'(?i)bearer\s+[\w\-\.]+',
                    r'(?i)aws[_-]?access[_-]?key[_-]?id\s*[:=]\s*[A-Z0-9]{20}'
                ],
                severity="critical",
                remediation="Remove or secure exposed credentials",
                tags=["security", "credentials", "secrets"]
            )
        ]

    async def check_document(self, content: str) -> List[Dict[str, Any]]:
        """
        Check document content against compliance rules.

        Args:
            content: Document text content

        Returns:
            List of compliance violations found
        """
        violations = []

        for rule in self.rules:
            for pattern in rule.regex_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    violations.append({
                        'rule_id': rule.id,
                        'rule_name': rule.name,
                        'category': rule.category,
                        'severity': rule.severity,
                        'match': match.group()[:50],  # Truncate for privacy
                        'position': match.span(),
                        'remediation': rule.remediation
                    })

        return violations

    def get_rules_by_category(self, category: str) -> List[ComplianceRule]:
        """Get all rules for a specific category."""
        return [rule for rule in self.rules if rule.category == category]

    def add_custom_rule(self, rule: ComplianceRule):
        """Add a custom compliance rule."""
        self.rules.append(rule)
        self.logger.info(f"Added custom rule: {rule.id}")


@dataclass
class RiskFactor:
    """Represents a risk factor in document analysis."""
    name: str
    category: str
    probability: str  # low, medium, high
    impact: str  # low, medium, high
    description: str
    mitigation_strategies: List[str]


class RiskAssessmentFramework:
    """
    Framework for assessing risks in documents.

    This class provides risk scoring and assessment capabilities
    for document analysis.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.risk_matrix = self._create_risk_matrix()

    def _create_risk_matrix(self) -> Dict[Tuple[str, str], str]:
        """Create risk assessment matrix."""
        return {
            ('low', 'low'): 'low',
            ('low', 'medium'): 'low',
            ('low', 'high'): 'medium',
            ('medium', 'low'): 'low',
            ('medium', 'medium'): 'medium',
            ('medium', 'high'): 'high',
            ('high', 'low'): 'medium',
            ('high', 'medium'): 'high',
            ('high', 'high'): 'critical'
        }

    async def assess_document_risk(self, document_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess overall risk for a document.

        Args:
            document_analysis: Analysis results from document processing

        Returns:
            Risk assessment report
        """
        risk_factors = []

        # Check content sensitivity
        if document_analysis.get('classification') == 'confidential':
            risk_factors.append(RiskFactor(
                name='Confidential Information',
                category='data_security',
                probability='high',
                impact='high',
                description='Document contains confidential information',
                mitigation_strategies=['Encrypt document', 'Restrict access']
            ))

        # Check compliance violations
        violations = document_analysis.get('compliance_violations', [])
        if violations:
            severity_counts = {}
            for violation in violations:
                severity = violation.get('severity', 'low')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            if severity_counts.get('critical', 0) > 0:
                risk_factors.append(RiskFactor(
                    name='Critical Compliance Violations',
                    category='compliance',
                    probability='high',
                    impact='high',
                    description=f"Found {severity_counts['critical']} critical violations",
                    mitigation_strategies=['Immediate remediation required', 'Legal review']
                ))

        # Calculate overall risk score
        overall_risk = self._calculate_overall_risk(risk_factors)

        return {
            'risk_factors': [self._risk_factor_to_dict(rf) for rf in risk_factors],
            'overall_risk_level': overall_risk,
            'risk_score': self._calculate_risk_score(risk_factors),
            'recommendations': self._generate_recommendations(risk_factors),
            'assessment_timestamp': datetime.now().isoformat()
        }

    def _calculate_overall_risk(self, risk_factors: List[RiskFactor]) -> str:
        """Calculate overall risk level."""
        if not risk_factors:
            return 'low'

        # Get highest risk level
        risk_levels = []
        for factor in risk_factors:
            risk_level = self.risk_matrix.get((factor.probability, factor.impact), 'medium')
            risk_levels.append(risk_level)

        # Priority order: critical > high > medium > low
        priority_order = ['critical', 'high', 'medium', 'low']
        for level in priority_order:
            if level in risk_levels:
                return level

        return 'low'

    def _calculate_risk_score(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate numerical risk score (0-100)."""
        if not risk_factors:
            return 0.0

        scores = {
            'low': 25,
            'medium': 50,
            'high': 75,
            'critical': 100
        }

        total_score = 0
        for factor in risk_factors:
            risk_level = self.risk_matrix.get((factor.probability, factor.impact), 'medium')
            total_score += scores.get(risk_level, 50)

        return min(100.0, total_score / len(risk_factors))

    def _generate_recommendations(self, risk_factors: List[RiskFactor]) -> List[str]:
        """Generate recommendations based on risk factors."""
        recommendations = []

        # Aggregate mitigation strategies
        all_strategies = []
        for factor in risk_factors:
            all_strategies.extend(factor.mitigation_strategies)

        # Deduplicate and prioritize
        seen = set()
        for strategy in all_strategies:
            if strategy not in seen:
                recommendations.append(strategy)
                seen.add(strategy)

        return recommendations[:5]  # Top 5 recommendations

    def _risk_factor_to_dict(self, risk_factor: RiskFactor) -> Dict[str, Any]:
        """Convert RiskFactor to dictionary."""
        return {
            'name': risk_factor.name,
            'category': risk_factor.category,
            'probability': risk_factor.probability,
            'impact': risk_factor.impact,
            'description': risk_factor.description,
            'mitigation_strategies': risk_factor.mitigation_strategies
        }


class ReportTemplate:
    """
    Manages report templates for document analysis results.

    This class provides various report formats for different audiences.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def generate_executive_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate executive-level report."""
        report = f"""
# EXECUTIVE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Document Information
- ID: {analysis_results.get('document_id', 'N/A')}
- Type: {analysis_results.get('document_type', 'N/A')}
- Classification: {analysis_results.get('classification', 'N/A')}

## Executive Summary
{analysis_results.get('executive_summary', 'No summary available')}

## Key Findings
"""
        for finding in analysis_results.get('key_findings', []):
            report += f"• {finding}\n"

        report += f"""
## Risk Assessment
Overall Risk Level: {analysis_results.get('overall_risk_level', 'Not assessed')}
Risk Score: {analysis_results.get('risk_score', 0):.1f}/100

## Recommendations
"""
        for rec in analysis_results.get('recommendations', []):
            report += f"• {rec}\n"

        report += """
## Next Steps
"""
        for step in analysis_results.get('next_steps', []):
            report += f"1. {step}\n"

        return report

    def generate_technical_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate technical detailed report."""
        report = f"""
# TECHNICAL ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Document Metadata
```json
{json.dumps(analysis_results.get('metadata', {}), indent=2)}
```

## Content Analysis
### Topics Identified
"""
        for topic in analysis_results.get('topics', []):
            report += f"- {topic}\n"

        report += """
### Entity Extraction
"""
        for entity in analysis_results.get('entities', []):
            report += f"- {entity.get('type', 'unknown')}: {entity.get('value', 'N/A')}\n"

        report += f"""
## Compliance Check Results
"""
        violations = analysis_results.get('compliance_violations', [])
        if violations:
            report += f"Found {len(violations)} compliance issues:\n"
            for violation in violations:
                report += f"- [{violation.get('severity', 'unknown')}] {violation.get('rule_name', 'N/A')}\n"
        else:
            report += "No compliance violations found.\n"

        report += """
## Technical Recommendations
"""
        for rec in analysis_results.get('technical_recommendations', []):
            report += f"- {rec}\n"

        return report

    def generate_compliance_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate compliance-focused report."""
        report = f"""
# COMPLIANCE ASSESSMENT REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Document Information
- Document ID: {analysis_results.get('document_id', 'N/A')}
- Review Date: {datetime.now().strftime('%Y-%m-%d')}
- Reviewer: Automated System

## Compliance Summary
Overall Compliance Score: {analysis_results.get('compliance_score', 0):.1%}

## Regulatory Framework Coverage
"""
        for framework in analysis_results.get('regulatory_frameworks', []):
            report += f"- {framework}: {'✓' if framework in analysis_results.get('compliant_frameworks', []) else '✗'}\n"

        report += """
## Violations and Issues
"""
        violations = analysis_results.get('compliance_violations', [])
        if violations:
            # Group by severity
            by_severity = {}
            for violation in violations:
                severity = violation.get('severity', 'unknown')
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(violation)

            for severity in ['critical', 'high', 'medium', 'low']:
                if severity in by_severity:
                    report += f"\n### {severity.upper()} Severity Issues\n"
                    for violation in by_severity[severity]:
                        report += f"- {violation.get('rule_name', 'N/A')}: {violation.get('remediation', 'N/A')}\n"
        else:
            report += "No compliance violations identified.\n"

        report += """
## Remediation Actions
"""
        for action in analysis_results.get('remediation_actions', []):
            report += f"1. {action}\n"

        report += f"""
## Sign-off Requirements
"""
        if analysis_results.get('approval_required', False):
            report += f"⚠️ This document requires approval from: {analysis_results.get('approver', 'Compliance Officer')}\n"
        else:
            report += "✓ No additional approval required\n"

        return report

    def generate_summary_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured summary suitable for APIs."""
        return {
            'report_type': 'summary',
            'generated_at': datetime.now().isoformat(),
            'document_id': analysis_results.get('document_id'),
            'summary': {
                'content': analysis_results.get('summary', ''),
                'word_count': analysis_results.get('word_count', 0),
                'reading_time': analysis_results.get('reading_time', 0)
            },
            'classification': {
                'type': analysis_results.get('document_type', 'unknown'),
                'sensitivity': analysis_results.get('classification', 'unclassified'),
                'tags': analysis_results.get('tags', [])
            },
            'analysis': {
                'topics': analysis_results.get('topics', []),
                'entities': analysis_results.get('entities', []),
                'sentiment': analysis_results.get('sentiment', 'neutral'),
                'complexity': analysis_results.get('complexity', 'moderate')
            },
            'compliance': {
                'score': analysis_results.get('compliance_score', 1.0),
                'violations': len(analysis_results.get('compliance_violations', [])),
                'risk_level': analysis_results.get('overall_risk_level', 'low')
            },
            'recommendations': analysis_results.get('recommendations', [])
        }


# Utility functions for document processing

def calculate_document_statistics(content: str) -> Dict[str, Any]:
    """Calculate various statistics for document content."""
    words = content.split()
    sentences = re.split(r'[.!?]+', content)
    paragraphs = content.split('\n\n')

    return {
        'character_count': len(content),
        'word_count': len(words),
        'sentence_count': len(sentences),
        'paragraph_count': len(paragraphs),
        'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
        'average_sentence_length': len(words) / len(sentences) if sentences else 0,
        'reading_time_minutes': max(1, len(words) // 200),  # Assuming 200 wpm
        'complexity_score': calculate_complexity_score(content)
    }


def calculate_complexity_score(content: str) -> float:
    """Calculate text complexity score (0-1)."""
    # Simple complexity calculation based on various factors
    words = content.split()
    if not words:
        return 0.0

    # Factors for complexity
    avg_word_length = sum(len(word) for word in words) / len(words)
    long_words = sum(1 for word in words if len(word) > 10)
    sentences = re.split(r'[.!?]+', content)
    avg_sentence_length = len(words) / len(sentences) if sentences else 0

    # Normalize scores (simple heuristic)
    word_complexity = min(1.0, avg_word_length / 10)
    long_word_ratio = min(1.0, long_words / len(words) * 5)
    sentence_complexity = min(1.0, avg_sentence_length / 30)

    # Combined score
    complexity = (word_complexity + long_word_ratio + sentence_complexity) / 3

    return round(complexity, 2)


def extract_document_structure(content: str) -> Dict[str, Any]:
    """Extract structural elements from document."""
    structure = {
        'headings': [],
        'lists': [],
        'quotes': [],
        'code_blocks': [],
        'urls': [],
        'tables': []
    }

    # Extract headings (markdown style)
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    for match in re.finditer(heading_pattern, content, re.MULTILINE):
        structure['headings'].append({
            'level': len(match.group(1)),
            'text': match.group(2)
        })

    # Extract URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]\'"]+'
    structure['urls'] = re.findall(url_pattern, content)

    # Extract quoted text
    quote_pattern = r'"([^"]+)"'
    structure['quotes'] = re.findall(quote_pattern, content)

    # Extract lists (simple bullet points)
    list_pattern = r'^\s*[-*+]\s+(.+)$'
    for match in re.finditer(list_pattern, content, re.MULTILINE):
        structure['lists'].append(match.group(1))

    return structure


def sanitize_document_content(content: str) -> str:
    """Sanitize document content for safe processing."""
    # Remove control characters
    content = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', content)

    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content)

    # Remove potential script tags (for HTML content)
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.IGNORECASE | re.DOTALL)

    return content.strip()


if __name__ == "__main__":
    """Test document analysis utilities."""
    import asyncio

    async def test_utilities():
        print("Testing Document Analysis Utilities\n")

        # Test text extraction
        extractor = TextExtractor()
        print("1. Text Extractor initialized ✅")

        # Test compliance rules
        compliance = ComplianceRules()
        test_content = "Contact us at john.doe@example.com or call 555-123-4567"
        violations = await compliance.check_document(test_content)
        print(f"2. Compliance check found {len(violations)} violations ✅")

        # Test risk assessment
        risk_framework = RiskAssessmentFramework()
        risk_analysis = await risk_framework.assess_document_risk({
            'classification': 'confidential',
            'compliance_violations': violations
        })
        print(f"3. Risk assessment: {risk_analysis['overall_risk_level']} ✅")

        # Test report generation
        reporter = ReportTemplate()
        report = reporter.generate_summary_report({
            'document_id': 'test_001',
            'summary': 'Test document summary',
            'topics': ['testing', 'utilities'],
            'compliance_score': 0.85
        })
        print(f"4. Report generated with {len(report)} sections ✅")

        # Test document statistics
        stats = calculate_document_statistics(test_content)
        print(f"5. Document statistics calculated: {stats['word_count']} words ✅")

        print("\n✅ All utilities tested successfully!")

    # Run tests
    asyncio.run(test_utilities())