"""
Pydantic models for prompt chaining workflows.
These define the structured data passed between chain stages.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ============== Event Extraction Models ==============

class EventExtraction(BaseModel):
    """First stage: Extract basic event information."""
    description: str = Field(description="Raw description of the event")
    is_calendar_event: bool = Field(description="Whether this describes a calendar event")
    confidence_score: float = Field(ge=0, le=1, description="Confidence score 0-1")
    event_type: Optional[str] = Field(default=None, description="Type of event if detected")


class EventDetails(BaseModel):
    """Second stage: Parse specific event details."""
    name: str = Field(description="Name of the event")
    date: str = Field(description="Date and time in ISO 8601 format")
    duration_minutes: int = Field(ge=15, le=480, description="Duration in minutes")
    participants: List[str] = Field(description="List of participants")
    location: Optional[str] = Field(default=None, description="Event location")
    
    @validator('date')
    def validate_date_format(cls, v):
        """Ensure date is parseable."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except:
            # If not ISO format, accept it anyway for flexibility
            pass
        return v


class EventConfirmation(BaseModel):
    """Third stage: Generate confirmation message."""
    confirmation_message: str = Field(description="Natural language confirmation")
    calendar_link: Optional[str] = Field(default=None, description="Calendar link if applicable")
    summary: str = Field(description="Brief event summary")


# ============== Document Processing Models ==============

class DocumentExtraction(BaseModel):
    """Extract key information from document."""
    title: Optional[str] = Field(default=None, description="Document title")
    author: Optional[str] = Field(default=None, description="Document author")
    content_type: str = Field(description="Type of content")
    main_topics: List[str] = Field(description="Main topics covered")
    word_count: int = Field(ge=0, description="Approximate word count")


class DocumentSummary(BaseModel):
    """Summarize document content."""
    executive_summary: str = Field(description="Brief executive summary")
    key_points: List[str] = Field(description="Key points from the document")
    recommendations: Optional[List[str]] = Field(default=None, description="Any recommendations")
    sentiment: str = Field(description="Overall sentiment")


class DocumentOutput(BaseModel):
    """Format final document output."""
    formatted_output: str = Field(description="Formatted final output")
    metadata: Dict[str, Any] = Field(description="Document metadata")
    citations: Optional[List[str]] = Field(default=None, description="Citations if any")


# ============== Analysis Chain Models ==============

class InitialAnalysis(BaseModel):
    """First analysis stage."""
    data_quality: str = Field(description="Assessment of data quality")
    completeness: float = Field(ge=0, le=1, description="Data completeness score")
    key_metrics: Dict[str, float] = Field(description="Initial metrics")
    issues_found: List[str] = Field(description="Any issues identified")


class CategoryAnalysis(BaseModel):
    """Categorize and classify data."""
    primary_category: str = Field(description="Main category")
    secondary_categories: List[str] = Field(description="Additional categories")
    confidence_scores: Dict[str, float] = Field(description="Category confidence scores")
    reasoning: str = Field(description="Categorization reasoning")


class AnalysisScore(BaseModel):
    """Score and rank analysis results."""
    overall_score: float = Field(ge=0, le=100, description="Overall score")
    dimension_scores: Dict[str, float] = Field(description="Scores by dimension")
    strengths: List[str] = Field(description="Key strengths")
    weaknesses: List[str] = Field(description="Key weaknesses")


class AnalysisReport(BaseModel):
    """Final analysis report."""
    executive_summary: str = Field(description="Executive summary")
    detailed_findings: List[str] = Field(description="Detailed findings")
    recommendations: List[str] = Field(description="Actionable recommendations")
    next_steps: List[str] = Field(description="Suggested next steps")
    confidence_level: str = Field(description="Overall confidence level")


# ============== Translation Chain Models ==============

class LanguageDetection(BaseModel):
    """Detect source language."""
    detected_language: str = Field(description="Detected language code")
    confidence: float = Field(ge=0, le=1, description="Detection confidence")
    script: Optional[str] = Field(default=None, description="Writing script if applicable")


class Translation(BaseModel):
    """Raw translation output."""
    translated_text: str = Field(description="Translated text")
    literal_translation: Optional[str] = Field(default=None, description="Literal translation if different")
    cultural_notes: Optional[List[str]] = Field(default=None, description="Cultural context notes")


class TranslationVerification(BaseModel):
    """Verify translation quality."""
    is_accurate: bool = Field(description="Whether translation is accurate")
    accuracy_score: float = Field(ge=0, le=1, description="Accuracy score")
    issues: List[str] = Field(description="Any issues found")
    suggestions: List[str] = Field(description="Improvement suggestions")


class PolishedTranslation(BaseModel):
    """Final polished translation."""
    final_translation: str = Field(description="Final polished translation")
    style: str = Field(description="Translation style used")
    register: str = Field(description="Language register")
    notes: Optional[str] = Field(default=None, description="Translator notes")


# ============== Research Chain Models ==============

class ResearchQuery(BaseModel):
    """Formulate research query."""
    main_question: str = Field(description="Primary research question")
    sub_questions: List[str] = Field(description="Supporting questions")
    search_terms: List[str] = Field(description="Key search terms")
    scope: str = Field(description="Research scope")


class ResearchFindings(BaseModel):
    """Raw research findings."""
    sources: List[Dict[str, str]] = Field(description="Information sources")
    key_findings: List[str] = Field(description="Key findings")
    data_points: Dict[str, Any] = Field(description="Specific data points")
    gaps: List[str] = Field(description="Identified gaps")


class ResearchSynthesis(BaseModel):
    """Synthesize research findings."""
    synthesis: str = Field(description="Synthesized findings")
    themes: List[str] = Field(description="Major themes")
    conclusions: List[str] = Field(description="Research conclusions")
    limitations: List[str] = Field(description="Research limitations")


class ResearchCitation(BaseModel):
    """Format research with citations."""
    formatted_report: str = Field(description="Report with inline citations")
    bibliography: List[str] = Field(description="Full bibliography")
    citation_style: str = Field(description="Citation style used")
    appendices: Optional[Dict[str, str]] = Field(default=None, description="Additional materials")