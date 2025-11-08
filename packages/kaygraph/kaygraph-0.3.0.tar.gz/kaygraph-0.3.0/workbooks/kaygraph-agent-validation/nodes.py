"""
Validation nodes implementing structured output patterns.
These nodes demonstrate how to ensure LLM outputs match expected schemas.
"""

import json
import logging
from typing import Dict, Any, Type, Optional, TypeVar
from pydantic import BaseModel, ValidationError
from kaygraph import Node
from utils import call_llm
from models import (
    TaskResult, 
    Meeting, 
    Order, 
    OrderItem,
    SupportTicket,
    Person,
    Address,
    Company
)


T = TypeVar('T', bound=BaseModel)


class BasicValidationNode(Node):
    """
    Basic validation - extract structured data from text.
    
    This node demonstrates the fundamental pattern from the cookbook:
    1. Define schema with Pydantic
    2. Prompt LLM to extract data
    3. Validate against schema
    4. Return typed object
    """
    
    def __init__(self, model_class: Type[T] = TaskResult, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = model_class
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare user input for extraction."""
        user_input = shared.get("input", "")
        if not user_input:
            raise ValueError("No input provided")
        
        self.logger.info(f"Extracting {self.model_class.__name__} from: {user_input}")
        return user_input
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Extract structured data using LLM."""
        # Get schema information
        schema = self.model_class.model_json_schema()
        
        # Create extraction prompt
        prompt = f"""Extract information from the user input and return it as JSON matching this schema:

{json.dumps(schema, indent=2)}

User input: {prep_res}

Return only valid JSON, no additional text."""
        
        # Get LLM response
        response = call_llm(
            prompt,
            system="You are a data extraction assistant. Always return valid JSON."
        )
        
        # Try to parse JSON
        try:
            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            data = json.loads(response.strip())
            
            # Validate with Pydantic
            validated = self.model_class(**data)
            
            return {
                "success": True,
                "data": validated,
                "raw_response": response
            }
            
        except (json.JSONDecodeError, ValidationError) as e:
            self.logger.error(f"Validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "raw_response": response
            }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store validated data or error."""
        if exec_res["success"]:
            shared["extracted_data"] = exec_res["data"]
            shared["validation_success"] = True
            self.logger.info(f"Successfully extracted {self.model_class.__name__}")
        else:
            shared["validation_error"] = exec_res["error"]
            shared["validation_success"] = False
            shared["raw_response"] = exec_res["raw_response"]
        
        return None


class RetryValidationNode(Node):
    """
    Validation with automatic retry on failure.
    
    If validation fails, retry with error feedback to help
    the LLM correct its output.
    """
    
    def __init__(
        self, 
        model_class: Type[T] = Meeting,
        max_retries: int = 3,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.model_class = model_class
        self.max_retries = max_retries
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare extraction context."""
        user_input = shared.get("input", "")
        if not user_input:
            raise ValueError("No input provided")
        
        return {
            "input": user_input,
            "attempts": 0,
            "errors": []
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Extract with retry logic."""
        user_input = prep_res["input"]
        schema = self.model_class.model_json_schema()
        
        for attempt in range(self.max_retries):
            self.logger.info(f"Extraction attempt {attempt + 1}/{self.max_retries}")
            
            # Build prompt with error feedback
            if attempt == 0:
                prompt = f"""Extract information from the user input and return it as JSON matching this schema:

{json.dumps(schema, indent=2)}

User input: {user_input}

Return only valid JSON."""
            else:
                # Include previous errors
                error_feedback = "\n".join([
                    f"Attempt {i+1} error: {err}"
                    for i, err in enumerate(prep_res["errors"])
                ])
                
                prompt = f"""Previous extraction attempts failed. Please correct the errors and try again.

{error_feedback}

Schema to match:
{json.dumps(schema, indent=2)}

User input: {user_input}

Return only valid JSON that fixes the previous errors."""
            
            # Get LLM response
            response = call_llm(
                prompt,
                system="You are a data extraction assistant. Learn from previous errors and return valid JSON."
            )
            
            # Try to validate
            try:
                # Clean JSON
                clean_response = response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]
                
                data = json.loads(clean_response.strip())
                validated = self.model_class(**data)
                
                return {
                    "success": True,
                    "data": validated,
                    "attempts": attempt + 1
                }
                
            except json.JSONDecodeError as e:
                error_msg = f"JSON parse error: {str(e)}"
                prep_res["errors"].append(error_msg)
                self.logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")
                
            except ValidationError as e:
                error_msg = f"Validation error: {e.json()}"
                prep_res["errors"].append(error_msg)
                self.logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")
        
        # All attempts failed
        return {
            "success": False,
            "errors": prep_res["errors"],
            "attempts": self.max_retries
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: Dict) -> Optional[str]:
        """Store results with retry information."""
        shared["attempts"] = exec_res["attempts"]
        
        if exec_res["success"]:
            shared["extracted_data"] = exec_res["data"]
            shared["validation_success"] = True
            self.logger.info(f"Extraction succeeded after {exec_res['attempts']} attempts")
        else:
            shared["validation_errors"] = exec_res["errors"]
            shared["validation_success"] = False
            self.logger.error(f"Extraction failed after {exec_res['attempts']} attempts")
        
        return None


class ComplexValidationNode(Node):
    """
    Complex nested schema validation.
    
    Demonstrates extraction of nested objects, lists,
    and complex relationships.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare input."""
        return shared.get("input", "")
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Extract complex nested data."""
        # For this example, we'll extract an Order with items
        
        prompt = f"""Extract order information from the text below. Return JSON with:
- items: array of objects with product (string), quantity (number), and optional unit_price (number)
- customer_name: optional string
- shipping_address: optional string  
- notes: optional string

Text: {prep_res}

Example format:
{{
    "items": [
        {{"product": "Laptop", "quantity": 2, "unit_price": 999.99}},
        {{"product": "Mouse", "quantity": 2}}
    ],
    "customer_name": "John Doe",
    "shipping_address": "123 Main St"
}}

Return only valid JSON."""
        
        response = call_llm(
            prompt,
            system="You are an order extraction assistant. Extract all mentioned items with quantities."
        )
        
        try:
            # Parse and validate
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            data = json.loads(clean_response.strip())
            order = Order(**data)
            
            return {
                "success": True,
                "order": order,
                "summary": {
                    "total_items": order.total_items,
                    "total_price": order.total_price,
                    "num_products": len(order.items)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Complex validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "raw_response": response
            }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store complex extraction results."""
        if exec_res["success"]:
            shared["order"] = exec_res["order"]
            shared["order_summary"] = exec_res["summary"]
            shared["validation_success"] = True
        else:
            shared["validation_error"] = exec_res["error"]
            shared["validation_success"] = False
        
        return None


class CustomValidatorNode(Node):
    """
    Validation with custom business logic.
    
    Shows how to add custom validation beyond basic
    type checking.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare support ticket input."""
        return shared.get("input", "")
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Extract and validate support ticket."""
        prompt = f"""Extract support ticket information from this text:

{prep_res}

Return JSON with:
- issue_type: one of "bug", "feature_request", "question", "complaint"
- severity: one of "low", "medium", "high", "critical" 
- description: detailed description of the issue
- affected_product: optional product name
- user_email: optional email address

Severity guidelines:
- critical: system down, data loss, security issue
- high: major functionality broken, blocking work
- medium: annoying but has workaround
- low: minor issue, enhancement

Return only valid JSON."""
        
        response = call_llm(
            prompt,
            system="You are a support ticket classifier. Accurately assess severity based on impact."
        )
        
        try:
            # Parse response
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            
            data = json.loads(clean_response.strip())
            
            # Custom business validation
            if data.get("issue_type") == "bug" and data.get("severity") == "low":
                self.logger.warning("Bugs typically shouldn't be low severity, upgrading to medium")
                data["severity"] = "medium"
            
            if "urgent" in prep_res.lower() and data.get("severity") in ["low", "medium"]:
                self.logger.warning("User mentioned urgent, upgrading severity")
                data["severity"] = "high"
            
            # Validate with model
            ticket = SupportTicket(**data)
            
            return {
                "success": True,
                "ticket": ticket,
                "auto_adjusted": data != json.loads(clean_response.strip())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store ticket with custom validation results."""
        if exec_res["success"]:
            shared["ticket"] = exec_res["ticket"]
            shared["auto_adjusted"] = exec_res.get("auto_adjusted", False)
            shared["validation_success"] = True
            
            if exec_res.get("auto_adjusted"):
                self.logger.info("Ticket was auto-adjusted based on business rules")
        else:
            shared["validation_error"] = exec_res["error"]
            shared["validation_success"] = False
        
        return None


class FallbackValidationNode(Node):
    """
    Validation with graceful degradation.
    
    If structured extraction fails, fall back to 
    unstructured text extraction.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare input."""
        return shared.get("input", "")
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Try structured extraction with fallback."""
        # First try structured extraction (Meeting)
        structured_prompt = f"""Extract meeting information as JSON:
{{
    "title": "string",
    "attendees": ["list", "of", "names"],
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "duration_minutes": number,
    "location": "optional string"
}}

Text: {prep_res}

Return only valid JSON."""
        
        response = call_llm(structured_prompt)
        
        # Try structured parsing
        try:
            clean = response.strip()
            if clean.startswith("```json"):
                clean = clean[7:]
            if clean.endswith("```"):
                clean = clean[:-3]
            
            data = json.loads(clean.strip())
            meeting = Meeting(**data)
            
            return {
                "success": True,
                "type": "structured",
                "meeting": meeting
            }
            
        except Exception as e:
            self.logger.warning(f"Structured extraction failed: {e}, trying fallback")
            
            # Fallback to unstructured extraction
            fallback_prompt = f"""Extract key meeting details from this text:
{prep_res}

List the following if present:
- What is the meeting about?
- Who is attending?
- When is it?
- Where is it?
- How long?

Be specific but don't make up information."""
            
            fallback_response = call_llm(fallback_prompt)
            
            return {
                "success": True,
                "type": "fallback",
                "unstructured_data": fallback_response,
                "original_error": str(e)
            }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store results with fallback information."""
        shared["extraction_type"] = exec_res["type"]
        
        if exec_res["type"] == "structured":
            shared["meeting"] = exec_res["meeting"]
            shared["validation_success"] = True
        else:
            shared["unstructured_data"] = exec_res["unstructured_data"]
            shared["validation_success"] = False
            shared["fallback_used"] = True
            self.logger.info("Used fallback extraction")
        
        return None