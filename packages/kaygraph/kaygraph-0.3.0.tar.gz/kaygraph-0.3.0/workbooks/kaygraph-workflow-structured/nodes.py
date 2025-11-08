"""
Node implementations for structured data workflows.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Type, Union
from datetime import datetime
from pydantic import BaseModel, ValidationError

from kaygraph import Node, ValidatedNode, BatchNode, Graph
from models import (
    MeetingEvent, Invoice, ContactInfo, Product,
    DataTransformation, SchemaMapping, DataQualityMetrics,
    PipelineResult, PipelineStage
)
from utils import call_llm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _clean_json_response(response: str) -> str:
    """Clean LLM response to extract JSON."""
    response = response.strip()
    
    # Remove thinking tags if present
    if "<think>" in response and "</think>" in response:
        # Extract content after thinking
        parts = response.split("</think>")
        if len(parts) > 1:
            response = parts[-1].strip()
    
    # Remove markdown code blocks
    if response.startswith("```json"):
        response = response[7:]
    if response.endswith("```"):
        response = response[:-3]
    
    # Additional cleaning
    response = response.strip()
    
    return response


# ============== Extraction Nodes ==============

class MeetingExtractorNode(Node):
    """Extract meeting details from unstructured text."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get text to extract from."""
        return shared.get("text", "")
    
    def exec(self, text: str) -> Dict[str, Any]:
        """Extract meeting details using LLM."""
        if not text:
            return {"error": "No text provided"}
        
        prompt = f"""Extract meeting details from the following text and return ONLY a valid JSON object. Do not include any explanations, thinking, or markdown formatting.

Text: {text}

Expected JSON structure:
{{
  "name": "meeting title",
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "participants": [
    {{"name": "...", "email": "...", "role": "..."}}
  ],
  "location": {{
    "type": "virtual/in_person/hybrid",
    "name": "...",
    "address": "...",
    "meeting_link": "..."
  }},
  "agenda": ["item1", "item2"],
  "notes": "..."
}}

Output JSON only:"""
        
        system = "You are a JSON extraction bot. Return only valid JSON, no other text."
        
        try:
            response = call_llm(prompt, system, temperature=0.1)
            logger.info(f"Raw LLM response: {response[:200]}...")
            
            # Clean response and parse JSON
            cleaned = _clean_json_response(response)
            
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response was: {response[:500]}")
            return {"error": str(e), "raw_response": response}
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return {"error": str(e)}
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> Optional[str]:
        """Store extracted data."""
        shared["extracted_meeting"] = exec_res
        
        if "error" in exec_res:
            return "extraction_error"
        return None


class InvoiceExtractorNode(Node):
    """Extract invoice details from text."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get invoice text."""
        return shared.get("invoice_text", "")
    
    def exec(self, text: str) -> Dict[str, Any]:
        """Extract invoice details."""
        if not text:
            return {"error": "No invoice text provided"}
        
        prompt = f"""Extract invoice details from text and return ONLY valid JSON.

Text: {text}

Expected JSON structure:
{{
  "invoice_number": "...",
  "invoice_date": "YYYY-MM-DD",
  "due_date": "YYYY-MM-DD",
  "billing_address": {{
    "company_name": "...",
    "contact_name": "...",
    "street": "...",
    "city": "...",
    "state": "...",
    "postal_code": "...",
    "country": "..."
  }},
  "line_items": [
    {{
      "description": "...",
      "quantity": 0,
      "unit_price": 0,
      "tax_rate": 0,
      "discount_percent": 0
    }}
  ],
  "notes": "...",
  "payment_terms": "...",
  "currency": "..."
}}

Output JSON only:"""
        
        system = "You are a JSON extraction bot. Return only valid JSON, no other text."
        
        try:
            response = call_llm(prompt, system, temperature=0.1)
            cleaned = _clean_json_response(response)
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Invoice JSON parsing error: {e}")
            logger.error(f"Response was: {response[:500]}")
            return {"error": str(e), "raw_response": response}
        except Exception as e:
            logger.error(f"Invoice extraction error: {e}")
            return {"error": str(e)}
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> Optional[str]:
        """Store extracted invoice."""
        shared["extracted_invoice"] = exec_res
        
        if "error" in exec_res:
            return "extraction_error"
        return None


class ContactExtractorNode(Node):
    """Extract contact information from text."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get contact text."""
        return shared.get("contact_text", "")
    
    def exec(self, text: str) -> Dict[str, Any]:
        """Extract contact details."""
        if not text:
            return {"error": "No contact text provided"}
        
        prompt = f"""Extract contact information from text and return ONLY valid JSON.

Text: {text}

Expected JSON structure:
{{
  "first_name": "...",
  "last_name": "...",
  "middle_name": "...",
  "title": "...",
  "company": "...",
  "emails": [
    {{
      "type": "personal/work",
      "email": "...",
      "primary": true
    }}
  ],
  "phones": [
    {{
      "type": "mobile/work/home",
      "number": "...",
      "country_code": "+1",
      "primary": true
    }}
  ],
  "addresses": [],
  "social_media": [
    {{
      "platform": "...",
      "username": "...",
      "url": "..."
    }}
  ],
  "tags": []
}}

Output JSON only:"""
        
        system = "You are a JSON extraction bot. Return only valid JSON, no other text."
        
        try:
            response = call_llm(prompt, system, temperature=0.1)
            cleaned = _clean_json_response(response)
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Contact JSON parsing error: {e}")
            logger.error(f"Response was: {response[:500]}")
            return {"error": str(e), "raw_response": response}
        except Exception as e:
            logger.error(f"Contact extraction error: {e}")
            return {"error": str(e)}
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> Optional[str]:
        """Store extracted contact."""
        shared["extracted_contact"] = exec_res
        
        if "error" in exec_res:
            return "extraction_error"
        return None


# ============== Validation Nodes ==============

class SchemaValidatorNode(ValidatedNode):
    """Validate extracted data against schema."""
    
    def __init__(self, schema_class: Type[BaseModel], data_key: str, **kwargs):
        self.schema_class = schema_class
        self.data_key = data_key
        super().__init__(**kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get data to validate."""
        return shared.get(self.data_key, {})
    
    def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against schema."""
        if "error" in data:
            return {"valid": False, "error": data["error"]}
        
        try:
            # Validate with Pydantic
            instance = self.schema_class(**data)
            return {
                "valid": True,
                "validated_data": instance.model_dump(),
                "instance": instance
            }
        except ValidationError as e:
            errors = []
            for error in e.errors():
                errors.append({
                    "field": ".".join(str(x) for x in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"]
                })
            
            return {
                "valid": False,
                "validation_errors": errors,
                "error_count": len(errors)
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> Optional[str]:
        """Store validation result."""
        result_key = f"{self.data_key}_validation"
        shared[result_key] = exec_res
        
        if exec_res.get("valid"):
            shared[f"{self.data_key}_validated"] = exec_res["validated_data"]
            return None
        else:
            logger.warning(f"Validation failed for {self.data_key}: {exec_res}")
            return "validation_failed"


class BusinessRuleValidatorNode(Node):
    """Apply business rules to validated data."""
    
    def __init__(self, rules: List[Dict[str, Any]], data_key: str, **kwargs):
        self.rules = rules
        self.data_key = data_key
        super().__init__(**kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get validated data."""
        return shared.get(f"{self.data_key}_validated", {})
    
    def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules."""
        violations = []
        
        for rule in self.rules:
            rule_name = rule.get("name", "Unknown")
            rule_type = rule.get("type", "custom")
            
            try:
                if rule_type == "required_field":
                    field = rule["field"]
                    if not data.get(field):
                        violations.append({
                            "rule": rule_name,
                            "field": field,
                            "message": f"Required field '{field}' is missing or empty"
                        })
                
                elif rule_type == "date_range":
                    start_field = rule["start_field"]
                    end_field = rule["end_field"]
                    start = data.get(start_field)
                    end = data.get(end_field)
                    
                    if start and end and start > end:
                        violations.append({
                            "rule": rule_name,
                            "fields": [start_field, end_field],
                            "message": f"{end_field} must be after {start_field}"
                        })
                
                elif rule_type == "min_value":
                    field = rule["field"]
                    min_val = rule["min_value"]
                    val = data.get(field)
                    
                    if val is not None and val < min_val:
                        violations.append({
                            "rule": rule_name,
                            "field": field,
                            "message": f"{field} must be at least {min_val}"
                        })
                
                elif rule_type == "custom":
                    # Execute custom validation function
                    func = rule.get("function")
                    if func and callable(func):
                        result = func(data)
                        if not result.get("valid"):
                            violations.append({
                                "rule": rule_name,
                                "message": result.get("message", "Custom validation failed")
                            })
            
            except Exception as e:
                logger.error(f"Error applying rule {rule_name}: {e}")
                violations.append({
                    "rule": rule_name,
                    "error": str(e)
                })
        
        return {
            "violations": violations,
            "violation_count": len(violations),
            "valid": len(violations) == 0
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> Optional[str]:
        """Store business rule validation results."""
        shared[f"{self.data_key}_business_validation"] = exec_res
        
        if not exec_res["valid"]:
            return "business_rules_violated"
        return None


# ============== Transformation Nodes ==============

class DataTransformerNode(Node):
    """Transform data between schemas."""
    
    def __init__(self, mapping: SchemaMapping, source_key: str, target_key: str, **kwargs):
        self.mapping = mapping
        self.source_key = source_key
        self.target_key = target_key
        super().__init__(**kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get source data."""
        return shared.get(self.source_key, {})
    
    def exec(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data according to mapping."""
        if not source_data:
            return {"error": "No source data"}
        
        target_data = {}
        errors = []
        
        for transform in self.mapping.transformations:
            try:
                source_val = self._get_nested_value(source_data, transform.source_field)
                
                if transform.transform_type == "rename":
                    self._set_nested_value(target_data, transform.target_field, source_val)
                
                elif transform.transform_type == "cast":
                    target_type = transform.parameters.get("type", "str")
                    if target_type == "int":
                        val = int(source_val) if source_val is not None else None
                    elif target_type == "float":
                        val = float(source_val) if source_val is not None else None
                    elif target_type == "bool":
                        val = bool(source_val) if source_val is not None else None
                    elif target_type == "str":
                        val = str(source_val) if source_val is not None else None
                    else:
                        val = source_val
                    
                    self._set_nested_value(target_data, transform.target_field, val)
                
                elif transform.transform_type == "calculate":
                    formula = transform.parameters.get("formula")
                    if formula:
                        # Simple calculation support
                        result = eval(formula, {"__builtins__": {}}, source_data)
                        self._set_nested_value(target_data, transform.target_field, result)
                
                elif transform.transform_type == "merge":
                    fields = transform.parameters.get("fields", [])
                    separator = transform.parameters.get("separator", " ")
                    values = [str(self._get_nested_value(source_data, f)) for f in fields]
                    merged = separator.join(v for v in values if v and v != "None")
                    self._set_nested_value(target_data, transform.target_field, merged)
                
                elif transform.transform_type == "split":
                    separator = transform.parameters.get("separator", " ")
                    max_split = transform.parameters.get("max_split", -1)
                    if source_val:
                        parts = str(source_val).split(separator, max_split)
                        self._set_nested_value(target_data, transform.target_field, parts)
            
            except Exception as e:
                errors.append({
                    "transform": transform.model_dump(),
                    "error": str(e)
                })
        
        return {
            "transformed_data": target_data,
            "errors": errors,
            "error_count": len(errors),
            "success": len(errors) == 0
        }
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dict using dot notation."""
        parts = path.split(".")
        value = data
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set value in nested dict using dot notation."""
        parts = path.split(".")
        current = data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> Optional[str]:
        """Store transformed data."""
        shared[self.target_key] = exec_res
        
        if not exec_res.get("success"):
            return "transformation_failed"
        
        shared[f"{self.target_key}_data"] = exec_res["transformed_data"]
        return None


# ============== Pipeline Nodes ==============

class PipelineMonitorNode(Node):
    """Monitor pipeline execution and collect metrics."""
    
    def __init__(self, pipeline_id: str, **kwargs):
        self.pipeline_id = pipeline_id
        self.start_time = None
        super().__init__(**kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize pipeline monitoring."""
        self.start_time = datetime.now()
        shared["pipeline_start_time"] = self.start_time
        shared["pipeline_stages_completed"] = []
        shared["pipeline_stages_failed"] = []
        shared["pipeline_metrics"] = DataQualityMetrics()
        return {"pipeline_id": self.pipeline_id}
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Start monitoring."""
        return {
            "pipeline_id": prep_res["pipeline_id"],
            "monitoring": "active",
            "start_time": self.start_time.isoformat()
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> Optional[str]:
        """Store monitoring state."""
        shared["pipeline_monitoring"] = exec_res
        return None


class PipelineStageNode(Node):
    """Execute a pipeline stage with error handling."""
    
    def __init__(self, stage: PipelineStage, stage_func, **kwargs):
        self.stage = stage
        self.stage_func = stage_func
        super().__init__(**kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get stage input."""
        input_data = shared.get(self.stage.input_schema or "pipeline_input", {})
        return {
            "input_data": input_data,
            "stage_config": self.stage.model_dump()
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute stage function."""
        try:
            result = self.stage_func(prep_res["input_data"])
            return {
                "success": True,
                "result": result,
                "stage": self.stage.stage_name
            }
        except Exception as e:
            logger.error(f"Stage {self.stage.stage_name} failed: {e}")
            
            if self.stage.error_handling == "fail":
                raise
            elif self.stage.error_handling == "skip":
                return {
                    "success": False,
                    "skipped": True,
                    "error": str(e),
                    "stage": self.stage.stage_name
                }
            else:  # default
                return {
                    "success": False,
                    "result": {},
                    "error": str(e),
                    "stage": self.stage.stage_name
                }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> Optional[str]:
        """Update pipeline state."""
        if exec_res.get("success"):
            shared["pipeline_stages_completed"].append(self.stage.stage_name)
            if self.stage.output_schema:
                shared[self.stage.output_schema] = exec_res["result"]
        else:
            shared["pipeline_stages_failed"].append(self.stage.stage_name)
            if exec_res.get("skipped"):
                metrics = shared.get("pipeline_metrics")
                if metrics:
                    metrics.skipped_records += 1
        
        return None


class PipelineFinalizerNode(Node):
    """Finalize pipeline and generate results."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather pipeline results."""
        return {
            "pipeline_id": shared.get("pipeline_monitoring", {}).get("pipeline_id"),
            "start_time": shared.get("pipeline_start_time"),
            "stages_completed": shared.get("pipeline_stages_completed", []),
            "stages_failed": shared.get("pipeline_stages_failed", []),
            "metrics": shared.get("pipeline_metrics")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> PipelineResult:
        """Create pipeline result."""
        result = PipelineResult(
            pipeline_id=prep_res["pipeline_id"] or "unknown",
            start_time=prep_res["start_time"] or datetime.now(),
            end_time=datetime.now(),
            stages_completed=prep_res["stages_completed"],
            stages_failed=prep_res["stages_failed"],
            data_quality=prep_res["metrics"] or DataQualityMetrics()
        )
        
        return result
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: PipelineResult) -> Optional[str]:
        """Store final results."""
        shared["pipeline_result"] = exec_res
        
        logger.info(f"Pipeline {exec_res.pipeline_id} completed:")
        logger.info(f"  Duration: {exec_res.duration_seconds:.2f}s")
        logger.info(f"  Success: {exec_res.success}")
        logger.info(f"  Stages completed: {len(exec_res.stages_completed)}")
        logger.info(f"  Stages failed: {len(exec_res.stages_failed)}")
        logger.info(f"  Data quality: {exec_res.data_quality.overall_quality_score:.2%}")
        
        if exec_res.success:
            return "pipeline_success"
        else:
            return "pipeline_failed"


# ============== Batch Processing Nodes ==============

class BatchValidatorNode(BatchNode):
    """Validate multiple records in batch."""
    
    def __init__(self, schema_class: Type[BaseModel], **kwargs):
        self.schema_class = schema_class
        super().__init__(**kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get records to validate."""
        return shared.get("batch_records", [])
    
    def exec(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate single record."""
        try:
            instance = self.schema_class(**record)
            return {
                "valid": True,
                "record": instance.model_dump(),
                "original": record
            }
        except ValidationError as e:
            return {
                "valid": False,
                "errors": [err["msg"] for err in e.errors()],
                "original": record
            }
    
    def post(self, shared: Dict[str, Any], prep_res: List[Dict[str, Any]], exec_res: List[Dict[str, Any]]) -> Optional[str]:
        """Store batch validation results."""
        valid_records = [r for r in exec_res if r.get("valid")]
        invalid_records = [r for r in exec_res if not r.get("valid")]
        
        shared["valid_records"] = valid_records
        shared["invalid_records"] = invalid_records
        
        metrics = shared.get("pipeline_metrics")
        if metrics:
            metrics.total_records = len(exec_res)
            metrics.valid_records = len(valid_records)
            metrics.invalid_records = len(invalid_records)
        
        logger.info(f"Batch validation: {len(valid_records)}/{len(exec_res)} valid")
        
        if len(invalid_records) > 0:
            return "partial_validation"
        return None


class DataQualityAnalyzerNode(Node):
    """Analyze data quality across the pipeline."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather quality data."""
        return {
            "valid_records": shared.get("valid_records", []),
            "invalid_records": shared.get("invalid_records", []),
            "pipeline_metrics": shared.get("pipeline_metrics")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> DataQualityMetrics:
        """Calculate quality metrics."""
        metrics = prep_res.get("pipeline_metrics") or DataQualityMetrics()
        valid = prep_res.get("valid_records", [])
        invalid = prep_res.get("invalid_records", [])
        
        total = len(valid) + len(invalid)
        if total > 0:
            # Completeness: ratio of non-null required fields
            completeness_scores = []
            for record in valid:
                data = record.get("record", {})
                fields = len(data)
                non_null = sum(1 for v in data.values() if v is not None)
                if fields > 0:
                    completeness_scores.append(non_null / fields)
            
            metrics.completeness_score = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
            
            # Accuracy: ratio of valid records
            metrics.accuracy_score = len(valid) / total
            
            # Consistency: check for duplicate keys or inconsistent data
            # Simple implementation - can be extended
            metrics.consistency_score = 0.95  # Placeholder
        
        return metrics
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: DataQualityMetrics) -> Optional[str]:
        """Store quality metrics."""
        shared["data_quality_analysis"] = exec_res
        shared["pipeline_metrics"] = exec_res
        
        logger.info(f"Data Quality Analysis:")
        logger.info(f"  Success rate: {exec_res.success_rate:.2%}")
        logger.info(f"  Completeness: {exec_res.completeness_score:.2%}")
        logger.info(f"  Accuracy: {exec_res.accuracy_score:.2%}")
        logger.info(f"  Consistency: {exec_res.consistency_score:.2%}")
        logger.info(f"  Overall: {exec_res.overall_quality_score:.2%}")
        
        return None