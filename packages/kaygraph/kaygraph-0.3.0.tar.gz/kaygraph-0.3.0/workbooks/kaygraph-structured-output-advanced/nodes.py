"""
Node implementations for advanced structured output workflows.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Type, TypeVar
from datetime import datetime
import re
import traceback

from kaygraph import Node, ValidatedNode
from pydantic import BaseModel, ValidationError
from models import (
    TicketCategory, Priority, Sentiment, ResponseTone,
    ValidationResult, SafetyCheck, CustomerInfo,
    TicketStep, TicketResolution,
    ReportSection, ReportMetadata, StructuredReport,
    FormFieldType, FormFieldValidation, FormField, ProcessedFormData,
    APIErrorDetail, APIResponse,
    WorkflowStep, WorkflowDefinition,
    BatchItem, BatchResult
)
from utils import call_llm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


def _clean_json_response(response: str) -> str:
    """Clean LLM response to extract JSON."""
    response = response.strip()
    
    # Remove thinking tags if present
    if "<think>" in response and "</think>" in response:
        parts = response.split("</think>")
        if len(parts) > 1:
            response = parts[-1].strip()
    
    # Remove markdown code blocks - handle various formats
    if "```json" in response:
        # Extract content between ```json and ```
        parts = response.split("```json")
        if len(parts) > 1:
            response = parts[1].split("```")[0]
    elif "```" in response:
        # Extract content between first ``` pair
        parts = response.split("```")
        if len(parts) >= 2:
            response = parts[1]
    
    response = response.strip()
    
    # If response doesn't start with { or [, try to find JSON
    if not response.startswith(("{", "[")):
        import re
        # Try to find complete JSON object - handle nested objects
        json_match = re.search(r'(\{(?:[^{}]|(?:\{[^{}]*\}))*\})', response, re.DOTALL)
        if json_match:
            response = json_match.group(1)
    
    return response.strip()


# ============== Base Structured Generation Node ==============

class StructuredGenerationNode(Node):
    """Base node for structured output generation with retry logic."""
    
    max_retries = 3
    wait = 0.5
    
    def __init__(self, 
                 output_model: Type[T],
                 system_prompt: Optional[str] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.output_model = output_model
        self.system_prompt = system_prompt or "You are a helpful assistant that generates structured data."
    
    def generate_schema_prompt(self) -> str:
        """Generate prompt explaining the schema."""
        # For simpler models, use a more straightforward prompt
        model_name = self.output_model.__name__
        
        # Create a simple example instead of full schema for basic models
        if model_name == "TicketResolution":
            return """Return ONLY a JSON object with these exact fields (no other text):
{
  "ticket_id": "TICKET-12345",
  "category": "billing",
  "priority": "high",
  "sentiment": "negative",
  "customer_info": {
    "customer_id": "CUST-789",
    "email": "customer@example.com",
    "name": "Customer Name"
  },
  "issue_summary": "Brief summary",
  "steps": [
    {
      "step_number": 1,
      "description": "Step description",
      "action": "Action to take",
      "requires_customer_input": false,
      "estimated_time_minutes": 5
    }
  ],
  "final_resolution": "Resolution message",
  "response_tone": "empathetic",
  "confidence": 0.9,
  "requires_follow_up": true,
  "safety_check": {
    "has_pii": false,
    "has_harmful_content": false,
    "has_prompt_injection": false,
    "pii_entities": [],
    "harmful_categories": [],
    "confidence": 0.95
  }
}"""
        
        # Fall back to simplified schema for other models
        schema = self.output_model.model_json_schema()
        # Simplify the schema for LLMs
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        simple_schema = {"required_fields": required}
        for field, config in properties.items():
            simple_schema[field] = config.get("type", "string")
            if "enum" in config:
                simple_schema[field] = f"one of: {config['enum']}"
        
        return f"""Return ONLY a JSON object with these fields:
{json.dumps(simple_schema, indent=2)}"""
    
    def progressive_prompt(self, attempt: int) -> str:
        """Progressive prompting for retries."""
        if attempt == 1:
            return self.generate_schema_prompt()
        elif attempt == 2:
            return f"{self.generate_schema_prompt()}\n\nPlease ensure all required fields are present and types are correct."
        else:
            # Simplified schema for last attempt
            return f"""Generate a JSON response with these fields:
{json.dumps(self._get_simplified_schema(), indent=2)}

Focus on providing valid data even if some optional fields are omitted."""
    
    def _get_simplified_schema(self) -> Dict[str, Any]:
        """Get simplified schema for fallback."""
        schema = self.output_model.model_json_schema()
        # Remove complex validations
        simplified = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for field, config in schema.get("properties", {}).items():
            simplified["properties"][field] = {"type": config.get("type", "string")}
        
        simplified["required"] = schema.get("required", [])
        return simplified
    
    def parse_response(self, response: str, attempt: int) -> T:
        """Parse and validate response with progressive relaxation."""
        cleaned = _clean_json_response(response)
        data = json.loads(cleaned)
        
        if attempt < self.max_retries:
            # Strict validation
            return self.output_model.model_validate(data)
        else:
            # Relaxed validation on last attempt
            return self.output_model.model_validate(data, strict=False)
    
    def exec_fallback(self, prep_res: Any, exc: Exception) -> T:
        """Fallback to create minimal valid output."""
        logger.error(f"All generation attempts failed: {exc}")
        
        # Create model-specific fallback
        model_name = self.output_model.__name__
        
        if model_name == "TicketResolution":
            from models import TicketResolution, Priority, TicketCategory, Sentiment, ResponseTone, CustomerInfo
            return TicketResolution(
                ticket_id=f"ERROR-{hash(prep_res) % 10000:04d}",
                category=TicketCategory.GENERAL,
                priority=Priority.MEDIUM,
                sentiment=Sentiment.NEUTRAL,
                customer_info=CustomerInfo(
                    customer_id="ERROR-001",
                    email="error@example.com",
                    name="Error State"
                ),
                issue_summary=str(prep_res)[:100] if prep_res else "Failed to generate ticket",
                steps=[],
                final_resolution="We apologize for the inconvenience. This ticket could not be properly processed. Please contact support directly for assistance.",
                response_tone=ResponseTone.PROFESSIONAL,
                confidence=0.0,
                requires_follow_up=True
            )
        
        # Generic fallback for other models
        required_fields = {}
        for field_name, field_info in self.output_model.model_fields.items():
            if field_info.is_required():
                # Provide default based on type
                if field_info.annotation == str:
                    required_fields[field_name] = "Error: Generation failed"
                elif field_info.annotation == int:
                    required_fields[field_name] = 0
                elif field_info.annotation == float:
                    required_fields[field_name] = 0.0
                elif field_info.annotation == bool:
                    required_fields[field_name] = False
                elif field_info.annotation == list:
                    required_fields[field_name] = []
                elif field_info.annotation == dict:
                    required_fields[field_name] = {}
                else:
                    required_fields[field_name] = None
        
        return self.output_model(**required_fields)
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: T) -> Optional[str]:
        """Store the generated structured output in shared store."""
        # Store with a key based on the model name
        model_name = self.output_model.__name__.lower()
        if model_name.endswith("resolution"):
            shared["ticket_resolution"] = exec_res
        elif model_name.endswith("report"):
            shared["structured_report"] = exec_res
        elif model_name.endswith("form"):
            shared["processed_form"] = exec_res
        else:
            shared[f"generated_{model_name}"] = exec_res
        return None  # Default routing


# ============== Customer Support Nodes ==============

class TicketGenerationNode(StructuredGenerationNode):
    """Generate support ticket with full validation."""
    
    def __init__(self, **kwargs):
        super().__init__(
            output_model=TicketResolution,
            system_prompt="You are a customer support AI that creates detailed ticket resolutions.",
            **kwargs
        )
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get customer query."""
        return shared.get("query", shared.get("message", ""))
    
    def exec(self, query: str) -> TicketResolution:
        """Generate ticket resolution."""
        prompt = f"""Customer Query: {query}

Create a support ticket JSON for this query.

{self.generate_schema_prompt()}

Return ONLY the JSON object, no explanations or other text."""
        
        for attempt in range(1, self.max_retries + 1):
            try:
                response = call_llm(
                    prompt if attempt == 1 else f"{prompt}\n\n{self.progressive_prompt(attempt)}",
                    self.system_prompt,
                    temperature=0.3
                )
                
                result = self.parse_response(response, attempt)
                
                # Add safety check if not present
                if not result.safety_check:
                    result.safety_check = self._perform_safety_check(query, result)
                
                return result
                
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    return self.exec_fallback(query, e)
        
        # If we get here, no attempt succeeded
        return self.exec_fallback(query, Exception("All attempts failed"))
    
    def _perform_safety_check(self, query: str, result: TicketResolution) -> SafetyCheck:
        """Perform basic safety checks."""
        safety = SafetyCheck(confidence=0.8)
        
        # Check for PII patterns
        pii_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),
            (r'\b\d{16}\b', 'Credit Card'),
            (r'\b\d{3}-\d{3}-\d{4}\b', 'Phone')
        ]
        
        combined_text = f"{query} {result.final_resolution}"
        
        for pattern, pii_type in pii_patterns:
            if re.search(pattern, combined_text):
                safety.has_pii = True
                safety.pii_entities.append(pii_type)
        
        # Check for harmful content keywords
        harmful_keywords = ['spam', 'phishing', 'hack', 'steal']
        for keyword in harmful_keywords:
            if keyword in combined_text.lower():
                safety.has_harmful_content = True
                safety.harmful_categories.append(keyword)
        
        return safety


class ContentValidationNode(ValidatedNode):
    """Validate generated content against business rules."""
    
    def prep(self, shared: Dict[str, Any]) -> TicketResolution:
        """Get ticket to validate."""
        ticket = shared.get("ticket_resolution")
        if ticket is None:
            # Return a minimal ticket for validation to process
            logger.warning("No ticket_resolution found in shared, creating minimal ticket")
            from models import TicketResolution, Priority, TicketCategory, Sentiment, ResponseTone
            return TicketResolution(
                ticket_id="ERROR-000",
                category=TicketCategory.OTHER,
                priority=Priority.LOW,
                sentiment=Sentiment.NEUTRAL,
                issue_summary="No ticket was generated",
                steps=[],
                final_resolution="Error: Failed to generate ticket",
                response_tone=ResponseTone.PROFESSIONAL,
                confidence=0.0
            )
        return ticket
    
    def exec(self, ticket: TicketResolution) -> ValidationResult:
        """Validate ticket content."""
        result = ValidationResult(is_valid=True)
        
        # Handle None ticket
        if ticket is None:
            result.is_valid = False
            result.errors.append("No ticket was generated")
            return result
        
        # Business rule validations
        if ticket.priority == Priority.URGENT and len(ticket.steps) > 5:
            result.warnings.append("Urgent tickets should have concise steps (5 or fewer)")
        
        if ticket.sentiment == Sentiment.ANGRY and ticket.response_tone != ResponseTone.EMPATHETIC:
            result.errors.append("Angry customers require empathetic tone")
            result.is_valid = False
        
        if ticket.safety_check and ticket.safety_check.has_pii:
            result.errors.append("Response contains PII that must be removed")
            result.is_valid = False
        
        # Length validations
        if len(ticket.final_resolution) < 50:
            result.errors.append("Final resolution too short")
            result.is_valid = False
        
        # Suggestions
        if ticket.confidence < 0.7:
            result.suggestions.append("Low confidence - consider human review")
        
        if not ticket.requires_follow_up and ticket.category == TicketCategory.BUG_REPORT:
            result.suggestions.append("Bug reports typically require follow-up")
        
        return result
    
    def validate_input(self, ticket: TicketResolution) -> TicketResolution:
        """Validate input is a ticket."""
        if ticket is None:
            # Return the minimal ticket created in prep
            return ticket  # Will be handled in exec
        if not isinstance(ticket, TicketResolution):
            raise ValueError("Input must be a TicketResolution")
        return ticket
    
    def validate_output(self, result: ValidationResult) -> None:
        """Ensure validation was performed."""
        if result.is_valid and result.errors:
            raise ValueError("Invalid state: marked valid but has errors")
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: ValidationResult) -> Optional[str]:
        """Store validation result."""
        shared["validation_result"] = exec_res
        return None  # Default routing


# ============== Report Generation Nodes ==============

class ReportGenerationNode(StructuredGenerationNode):
    """Generate structured reports with nested sections."""
    
    def __init__(self, **kwargs):
        super().__init__(
            output_model=StructuredReport,
            system_prompt="You are a report generation AI that creates well-structured, professional reports.",
            **kwargs
        )
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get report request details."""
        return {
            "topic": shared.get("topic", ""),
            "report_type": shared.get("report_type", "general"),
            "data": shared.get("data", {}),
            "requirements": shared.get("requirements", [])
        }
    
    def exec(self, request: Dict[str, Any]) -> StructuredReport:
        """Generate structured report."""
        prompt = f"""Create a professional report on the following topic:

Topic: {request['topic']}
Report Type: {request['report_type']}
Data: {json.dumps(request['data'], indent=2) if request['data'] else 'No specific data provided'}
Requirements: {', '.join(request['requirements']) if request['requirements'] else 'Standard report'}

{self.generate_schema_prompt()}

Guidelines:
- Create meaningful sections with substantive content
- Include data-driven insights where possible
- Provide actionable conclusions and recommendations
- Ensure professional tone throughout
- Structure sections hierarchically if needed

Generate the complete StructuredReport JSON:"""
        
        attempt = 0
        while attempt < self.max_retries:
            attempt += 1
            try:
                response = call_llm(prompt, self.system_prompt, temperature=0.4)
                return self.parse_response(response, attempt)
            except Exception as e:
                logger.warning(f"Report generation attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    # Create basic report
                    return StructuredReport(
                        metadata=ReportMetadata(
                            report_id=f"error_{datetime.now().timestamp()}",
                            title=f"Report on {request['topic']}",
                            author="System"
                        ),
                        executive_summary="Report generation encountered errors. Basic structure provided.",
                        sections=[
                            ReportSection(
                                title="Overview",
                                content="This section would contain the main report content. Generation failed due to technical issues."
                            )
                        ],
                        conclusions=["Report generation incomplete"],
                        quality_score=0.3
                    )


class ReportQualityNode(Node):
    """Assess and enhance report quality."""
    
    def prep(self, shared: Dict[str, Any]) -> StructuredReport:
        """Get generated report."""
        return shared.get("report")
    
    def exec(self, report: StructuredReport) -> StructuredReport:
        """Enhance report quality."""
        # Calculate quality metrics
        total_content_length = len(report.executive_summary)
        for section in report.sections:
            total_content_length += len(section.content)
        
        # Quality score based on multiple factors
        length_score = min(total_content_length / 1000, 1.0)  # Normalize to 1000 chars
        section_score = min(len(report.sections) / 3, 1.0)  # At least 3 sections
        conclusion_score = min(len(report.conclusions) / 2, 1.0)  # At least 2 conclusions
        
        report.quality_score = (length_score + section_score + conclusion_score) / 3
        
        # Add recommendations if missing and quality is good
        if not report.recommendations and report.quality_score > 0.7:
            report.recommendations = [
                "Consider implementing the findings from this report",
                "Schedule follow-up review in 30 days"
            ]
        
        return report


# ============== Form Processing Nodes ==============

class FormSchemaGenerationNode(Node):
    """Generate dynamic form schemas based on requirements."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get form requirements."""
        return shared.get("form_description", "")
    
    def exec(self, description: str) -> List[FormField]:
        """Generate form fields."""
        prompt = f"""Create a form schema based on this description:

{description}

Generate a list of FormField objects with appropriate:
- Field types (text, number, email, date, select, etc.)
- Validation rules (required, min/max length, patterns)
- Help text for users
- Conditional dependencies if applicable

Return a JSON array of FormField objects."""
        
        system = "You are a form designer that creates user-friendly, well-validated forms."
        
        try:
            response = call_llm(prompt, system, temperature=0.3)
            cleaned = _clean_json_response(response)
            fields_data = json.loads(cleaned)
            
            # Parse into FormField objects
            fields = []
            for field_data in fields_data:
                validation_data = field_data.get("validation", {})
                validation = FormFieldValidation(**validation_data)
                
                field = FormField(
                    field_id=field_data["field_id"],
                    label=field_data["label"],
                    field_type=FormFieldType(field_data["field_type"]),
                    validation=validation,
                    default_value=field_data.get("default_value"),
                    help_text=field_data.get("help_text"),
                    depends_on=field_data.get("depends_on")
                )
                fields.append(field)
            
            return fields
            
        except Exception as e:
            logger.error(f"Form generation error: {e}")
            # Return basic form
            return [
                FormField(
                    field_id="name",
                    label="Name",
                    field_type=FormFieldType.TEXT,
                    validation=FormFieldValidation(required=True)
                ),
                FormField(
                    field_id="email",
                    label="Email",
                    field_type=FormFieldType.EMAIL,
                    validation=FormFieldValidation(required=True)
                )
            ]


class FormDataProcessingNode(Node):
    """Process submitted form data."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get form schema and data."""
        return {
            "fields": shared.get("form_fields", []),
            "data": shared.get("form_data", {})
        }
    
    def exec(self, inputs: Dict[str, Any]) -> ProcessedFormData:
        """Process and validate form data."""
        fields = inputs["fields"]
        data = inputs["data"]
        
        validation_result = ValidationResult(is_valid=True)
        processed_data = {}
        
        # Validate each field
        for field in fields:
            field_value = data.get(field.field_id)
            
            # Required field check
            if field.validation.required and not field_value:
                validation_result.errors.append(f"{field.label} is required")
                validation_result.is_valid = False
                continue
            
            # Type-specific validation
            if field_value:
                if field.field_type == FormFieldType.EMAIL:
                    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(field_value)):
                        validation_result.errors.append(f"{field.label} must be a valid email")
                        validation_result.is_valid = False
                
                elif field.field_type == FormFieldType.NUMBER:
                    try:
                        num_value = float(field_value)
                        if field.validation.min_value is not None and num_value < field.validation.min_value:
                            validation_result.errors.append(f"{field.label} must be at least {field.validation.min_value}")
                            validation_result.is_valid = False
                    except ValueError:
                        validation_result.errors.append(f"{field.label} must be a number")
                        validation_result.is_valid = False
            
            processed_data[field.field_id] = field_value
        
        # Extract entities
        extracted_entities = {}
        if "email" in processed_data and processed_data["email"]:
            extracted_entities["emails"] = [processed_data["email"]]
        
        return ProcessedFormData(
            form_id="form_" + str(datetime.now().timestamp()),
            submission_id="sub_" + str(datetime.now().timestamp()),
            fields=processed_data,
            validation_result=validation_result,
            extracted_entities=extracted_entities
        )


# ============== Batch Processing Nodes ==============

class BatchStructuredGenerationNode(Node):
    """Generate structured outputs for multiple items in batch."""
    
    def __init__(self, output_model: Type[T], **kwargs):
        super().__init__(**kwargs)
        self.output_model = output_model
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get batch items to process."""
        return shared.get("batch_items", [])
    
    def exec(self, items: List[Dict[str, Any]]) -> BatchResult:
        """Process batch of items."""
        batch_id = f"batch_{datetime.now().timestamp()}"
        start_time = datetime.now()
        
        results = []
        successful = 0
        failed = 0
        
        for item in items:
            batch_item = BatchItem(
                item_id=item.get("id", str(len(results))),
                data=item,
                schema_type=self.output_model.__name__
            )
            
            try:
                # Generate structured output for item
                prompt = f"""Generate {self.output_model.__name__} for this data:
{json.dumps(item, indent=2)}

Schema: {self.output_model.model_json_schema()}"""
                
                response = call_llm(prompt, temperature=0.3)
                cleaned = _clean_json_response(response)
                parsed = self.output_model.model_validate_json(cleaned)
                
                batch_item.validation_status = "success"
                successful += 1
                
            except Exception as e:
                batch_item.validation_status = "failed"
                batch_item.errors = [str(e)]
                failed += 1
            
            results.append(batch_item)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return BatchResult(
            batch_id=batch_id,
            total_items=len(items),
            successful_items=successful,
            failed_items=failed,
            items=results,
            processing_time_seconds=processing_time,
            aggregate_metrics={
                "success_rate": successful / len(items) if items else 0,
                "avg_time_per_item": processing_time / len(items) if items else 0
            }
        )


# ============== Output Formatting Nodes ==============

class StructuredOutputFormatterNode(Node):
    """Format structured outputs for display."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all structured outputs."""
        return {
            "ticket": shared.get("ticket_resolution"),
            "report": shared.get("report"),
            "form": shared.get("processed_form"),
            "batch": shared.get("batch_result")
        }
    
    def exec(self, outputs: Dict[str, Any]) -> str:
        """Format outputs for display."""
        formatted_parts = []
        
        # Format ticket if present
        if outputs.get("ticket"):
            ticket = outputs["ticket"]
            formatted_parts.append(f"""=== Support Ticket ===
ID: {ticket.ticket_id}
Category: {ticket.category.value}
Priority: {ticket.priority.value}
Sentiment: {ticket.sentiment.value}

Issue: {ticket.issue_summary}

Resolution Steps:""")
            for step in ticket.steps:
                formatted_parts.append(f"{step.step_number}. {step.description}")
                formatted_parts.append(f"   Action: {step.action}")
            
            formatted_parts.append(f"\nFinal Resolution:\n{ticket.final_resolution}")
            
            if ticket.safety_check and ticket.safety_check.has_pii:
                formatted_parts.append("\n⚠️ Warning: PII detected and should be removed")
        
        # Format report if present
        if outputs.get("report"):
            report = outputs["report"]
            formatted_parts.append(f"""\n=== Report: {report.metadata.title} ===
Author: {report.metadata.author}
Quality Score: {report.quality_score:.2f}

Executive Summary:
{report.executive_summary}

Sections:""")
            for section in report.sections:
                formatted_parts.append(f"\n## {section.title}")
                formatted_parts.append(section.content[:200] + "...")
        
        # Format form if present
        if outputs.get("form"):
            form = outputs["form"]
            formatted_parts.append(f"""\n=== Form Submission ===
Form ID: {form.form_id}
Validation: {'✓ Valid' if form.validation_result.is_valid else '✗ Invalid'}""")
            
            if form.validation_result.errors:
                formatted_parts.append("\nErrors:")
                for error in form.validation_result.errors:
                    formatted_parts.append(f"- {error}")
        
        # Format batch if present
        if outputs.get("batch"):
            batch = outputs["batch"]
            formatted_parts.append(f"""\n=== Batch Processing ===
Batch ID: {batch.batch_id}
Total Items: {batch.total_items}
Successful: {batch.successful_items}
Failed: {batch.failed_items}
Processing Time: {batch.processing_time_seconds:.2f}s
Success Rate: {batch.aggregate_metrics.get('success_rate', 0):.1%}""")
        
        return "\n".join(formatted_parts) if formatted_parts else "No structured outputs generated"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: str) -> Optional[str]:
        """Store formatted output."""
        shared["formatted_output"] = exec_res
        return None