"""
Parallelization nodes implementing concurrent processing patterns.
These nodes demonstrate parallel execution for performance optimization.
"""

import time
import json
import logging
import random
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from kaygraph import Node, ParallelBatchNode, AsyncNode
from utils import call_llm
from models import (
    ValidationResult, SecurityValidation, FormatValidation,
    BusinessRuleValidation, ParallelValidationSummary,
    EnrichmentSource, EnrichmentResult, UserProfileEnrichment,
    LocationEnrichment, CompanyEnrichment, EnrichedData,
    BatchItem, ProcessingResult, BatchConfiguration,
    BatchProgress, BatchResult,
    MapTask, MapResult, ReduceTask, ReduceResult, MapReduceJob,
    PipelineStage, StageResult, PipelineExecution,
    ParallelizationMetrics
)


# ============== Parallel Validation Nodes ==============

class ParallelValidationNode(Node):
    """
    Runs multiple validation checks in parallel.
    Demonstrates concurrent execution of independent validations.
    """
    
    def __init__(self, max_workers: int = 4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_workers = max_workers
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for validation."""
        return {
            "data": shared.get("input_data", {}),
            "validation_rules": shared.get("validation_rules", {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> ParallelValidationSummary:
        """Execute validations in parallel."""
        data = prep_res["data"]
        start_time = time.time()
        
        # Define validation tasks
        validation_tasks = [
            ("security", self._validate_security, data),
            ("format", self._validate_format, data),
            ("business_rules", self._validate_business_rules, data),
            ("external_api", self._validate_external_api, data)
        ]
        
        results = []
        parallel_start = time.time()
        
        # Execute validations in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_validation = {
                executor.submit(validator, data): (name, validator)
                for name, validator, data in validation_tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_validation):
                name, validator = future_to_validation[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Validation {name} failed: {e}")
                    results.append(ValidationResult(
                        check_name=name,
                        passed=False,
                        confidence=0.0,
                        error=str(e),
                        execution_time_ms=0
                    ))
        
        parallel_end = time.time()
        
        # Calculate sequential time (sum of individual times)
        sequential_time = sum(r.execution_time_ms for r in results)
        parallel_time = (parallel_end - parallel_start) * 1000
        
        # Create summary
        passed_checks = sum(1 for r in results if r.passed)
        
        return ParallelValidationSummary(
            total_checks=len(results),
            passed_checks=passed_checks,
            failed_checks=len(results) - passed_checks,
            total_execution_time_ms=sequential_time,
            parallel_execution_time_ms=parallel_time,
            speedup_factor=sequential_time / parallel_time if parallel_time > 0 else 1.0,
            all_validations=results
        )
    
    def _validate_security(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate security aspects."""
        start = time.time()
        
        # Simulate security check with LLM
        prompt = f"Check this data for security risks: {json.dumps(data)}"
        system = "Identify potential security risks like SQL injection, XSS, or data exposure."
        
        response = call_llm(prompt, system=system)
        
        # Parse response (simplified)
        is_safe = "safe" in response.lower() or "no risk" in response.lower()
        
        return ValidationResult(
            check_name="security",
            passed=is_safe,
            confidence=0.85 if is_safe else 0.3,
            details=response[:100],
            execution_time_ms=(time.time() - start) * 1000
        )
    
    def _validate_format(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate data format."""
        start = time.time()
        
        # Simulate format validation
        time.sleep(random.uniform(0.1, 0.3))  # Simulate work
        
        # Check required fields
        required_fields = ["email", "name", "date"]
        missing_fields = [f for f in required_fields if f not in data]
        
        passed = len(missing_fields) == 0
        
        return ValidationResult(
            check_name="format",
            passed=passed,
            confidence=1.0 if passed else 0.0,
            details=f"Missing fields: {missing_fields}" if missing_fields else "All fields present",
            execution_time_ms=(time.time() - start) * 1000
        )
    
    def _validate_business_rules(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate business rules."""
        start = time.time()
        
        # Simulate business rule validation
        time.sleep(random.uniform(0.2, 0.4))  # Simulate work
        
        # Example business rules
        rules_passed = []
        rules_failed = []
        
        # Rule 1: Email must be valid
        if data.get("email", "").count("@") == 1:
            rules_passed.append("valid_email")
        else:
            rules_failed.append("valid_email")
        
        # Rule 2: Name must be at least 2 characters
        if len(data.get("name", "")) >= 2:
            rules_passed.append("valid_name")
        else:
            rules_failed.append("valid_name")
        
        passed = len(rules_failed) == 0
        
        return ValidationResult(
            check_name="business_rules",
            passed=passed,
            confidence=0.9 if passed else 0.4,
            details=f"Passed: {rules_passed}, Failed: {rules_failed}",
            execution_time_ms=(time.time() - start) * 1000
        )
    
    def _validate_external_api(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate against external API (simulated)."""
        start = time.time()
        
        # Simulate API call
        time.sleep(random.uniform(0.5, 1.0))  # Simulate network latency
        
        # Simulate API response
        api_valid = random.random() > 0.2  # 80% success rate
        
        return ValidationResult(
            check_name="external_api",
            passed=api_valid,
            confidence=0.95 if api_valid else 0.1,
            details="External validation " + ("passed" if api_valid else "failed"),
            execution_time_ms=(time.time() - start) * 1000
        )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: ParallelValidationSummary) -> Optional[str]:
        """Store validation results."""
        shared["validation_summary"] = exec_res
        
        self.logger.info(
            f"Validation complete: {exec_res.passed_checks}/{exec_res.total_checks} passed. "
            f"Speedup: {exec_res.speedup_factor:.2f}x"
        )
        
        # Route based on validation results
        if exec_res.success_rate >= 0.75:
            return "valid"
        else:
            return "invalid"


# ============== Data Enrichment Nodes ==============

class ParallelEnrichmentNode(Node):
    """
    Enriches data from multiple sources in parallel.
    Fetches additional information concurrently.
    """
    
    def __init__(self, sources: List[EnrichmentSource] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sources = sources or [
            EnrichmentSource.USER_PROFILE,
            EnrichmentSource.LOCATION,
            EnrichmentSource.COMPANY
        ]
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for enrichment."""
        return shared.get("base_data", {})
    
    def exec(self, prep_res: Dict[str, Any]) -> EnrichedData:
        """Enrich data from multiple sources in parallel."""
        start_time = time.time()
        enrichment_results = {}
        
        # Define enrichment tasks
        enrichment_tasks = {
            EnrichmentSource.USER_PROFILE: self._enrich_user_profile,
            EnrichmentSource.LOCATION: self._enrich_location,
            EnrichmentSource.COMPANY: self._enrich_company,
            EnrichmentSource.SOCIAL_MEDIA: self._enrich_social_media
        }
        
        # Execute enrichments in parallel
        with ThreadPoolExecutor(max_workers=len(self.sources)) as executor:
            future_to_source = {
                executor.submit(enrichment_tasks[source], prep_res): source
                for source in self.sources
                if source in enrichment_tasks
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    result = future.result()
                    enrichment_results[source] = result
                except Exception as e:
                    self.logger.error(f"Enrichment {source} failed: {e}")
                    enrichment_results[source] = EnrichmentResult(
                        source=source,
                        success=False,
                        error=str(e),
                        fetch_time_ms=0
                    )
        
        # Count successful enrichments
        successful_sources = sum(1 for r in enrichment_results.values() if r.success)
        
        return EnrichedData(
            original_data=prep_res,
            enrichments=enrichment_results,
            total_sources=len(enrichment_results),
            successful_sources=successful_sources,
            total_enrichment_time_ms=(time.time() - start_time) * 1000
        )
    
    def _enrich_user_profile(self, data: Dict[str, Any]) -> EnrichmentResult:
        """Enrich user profile data."""
        start = time.time()
        
        # Simulate API call
        time.sleep(random.uniform(0.2, 0.5))
        
        # Mock enriched data
        profile_data = UserProfileEnrichment(
            full_name=data.get("name", "Unknown User"),
            email_verified=random.random() > 0.3,
            phone_verified=random.random() > 0.5,
            account_age_days=random.randint(1, 1000),
            preferences={"theme": "dark", "notifications": True},
            segments=["active_user", "premium"]
        )
        
        return EnrichmentResult(
            source=EnrichmentSource.USER_PROFILE,
            success=True,
            data=profile_data.dict(),
            confidence_score=0.85,
            fetch_time_ms=(time.time() - start) * 1000
        )
    
    def _enrich_location(self, data: Dict[str, Any]) -> EnrichmentResult:
        """Enrich location data."""
        start = time.time()
        
        # Simulate geocoding API
        time.sleep(random.uniform(0.3, 0.7))
        
        location_data = LocationEnrichment(
            country="United States",
            city="San Francisco",
            timezone="America/Los_Angeles",
            coordinates={"lat": 37.7749, "lng": -122.4194},
            ip_type="residential"
        )
        
        return EnrichmentResult(
            source=EnrichmentSource.LOCATION,
            success=True,
            data=location_data.dict(),
            confidence_score=0.92,
            fetch_time_ms=(time.time() - start) * 1000
        )
    
    def _enrich_company(self, data: Dict[str, Any]) -> EnrichmentResult:
        """Enrich company data."""
        start = time.time()
        
        # Simulate company lookup API
        time.sleep(random.uniform(0.4, 0.8))
        
        company_data = CompanyEnrichment(
            company_name="Tech Corp",
            industry="Software",
            employee_count=500,
            revenue_range="$10M-$50M",
            technologies=["Python", "AWS", "React"]
        )
        
        return EnrichmentResult(
            source=EnrichmentSource.COMPANY,
            success=True,
            data=company_data.dict(),
            confidence_score=0.78,
            fetch_time_ms=(time.time() - start) * 1000
        )
    
    def _enrich_social_media(self, data: Dict[str, Any]) -> EnrichmentResult:
        """Enrich social media data."""
        start = time.time()
        
        # Simulate social media API
        time.sleep(random.uniform(0.5, 1.0))
        
        # Simulate occasional failures
        if random.random() < 0.2:
            return EnrichmentResult(
                source=EnrichmentSource.SOCIAL_MEDIA,
                success=False,
                error="API rate limit exceeded",
                fetch_time_ms=(time.time() - start) * 1000
            )
        
        social_data = {
            "twitter_handle": "@user123",
            "follower_count": 1234,
            "verified": False,
            "bio": "Tech enthusiast"
        }
        
        return EnrichmentResult(
            source=EnrichmentSource.SOCIAL_MEDIA,
            success=True,
            data=social_data,
            confidence_score=0.70,
            fetch_time_ms=(time.time() - start) * 1000
        )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: EnrichedData) -> Optional[str]:
        """Store enriched data."""
        shared["enriched_data"] = exec_res
        
        self.logger.info(
            f"Enrichment complete: {exec_res.successful_sources}/{exec_res.total_sources} sources. "
            f"Time: {exec_res.total_enrichment_time_ms:.0f}ms"
        )
        
        return None


# ============== Batch Processing Nodes ==============

class BatchProcessingNode(ParallelBatchNode):
    """
    Processes batches of items in parallel.
    Inherits from ParallelBatchNode for built-in parallel support.
    """
    
    def __init__(self, worker_count: int = 4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker_count = worker_count
        self.logger = logging.getLogger(self.__class__.__name__)
        self.start_time = None
        self.processed_count = 0
    
    def prep(self, shared: Dict[str, Any]) -> List[BatchItem]:
        """Prepare batch items for processing."""
        self.start_time = time.time()
        
        # Get batch configuration
        config = shared.get("batch_config", BatchConfiguration())
        
        # Get items to process
        raw_items = shared.get("batch_items", [])
        
        # Convert to BatchItem objects
        batch_items = []
        for i, item in enumerate(raw_items):
            batch_items.append(BatchItem(
                item_id=f"item_{i}",
                data=item if isinstance(item, dict) else {"value": item},
                priority="high" if i < 5 else "normal"  # First 5 items high priority
            ))
        
        # Store config for later
        shared["batch_config"] = config
        shared["batch_start_time"] = datetime.now()
        
        return batch_items
    
    def exec(self, prep_res: BatchItem) -> ProcessingResult:
        """Process a single batch item."""
        start = time.time()
        
        try:
            # Simulate processing with variable time
            processing_time = random.uniform(0.1, 0.5)
            time.sleep(processing_time)
            
            # Simulate occasional failures
            if random.random() < 0.1:  # 10% failure rate
                raise Exception("Processing error")
            
            # Process the item (example: transform data)
            result = {
                "processed": True,
                "original_id": prep_res.item_id,
                "transformed_data": str(prep_res.data).upper(),
                "priority_boost": prep_res.priority == "high"
            }
            
            return ProcessingResult(
                item_id=prep_res.item_id,
                success=True,
                result=result,
                processing_time_ms=(time.time() - start) * 1000,
                worker_id=f"worker_{id(self) % self.worker_count}"
            )
            
        except Exception as e:
            return ProcessingResult(
                item_id=prep_res.item_id,
                success=False,
                error=str(e),
                processing_time_ms=(time.time() - start) * 1000,
                worker_id=f"worker_{id(self) % self.worker_count}"
            )
    
    def post(self, shared: Dict[str, Any], prep_res: List[BatchItem], exec_res: List[ProcessingResult]) -> Optional[str]:
        """Aggregate batch results."""
        # Create batch progress
        successful = sum(1 for r in exec_res if r.success)
        failed = len(exec_res) - successful
        elapsed = (time.time() - self.start_time) * 1000
        
        progress = BatchProgress(
            total_items=len(prep_res),
            processed_items=len(exec_res),
            successful_items=successful,
            failed_items=failed,
            retry_items=0,
            elapsed_time_ms=elapsed,
            current_throughput=len(exec_res) / (elapsed / 1000) if elapsed > 0 else 0
        )
        
        # Create batch result
        batch_result = BatchResult(
            batch_id=f"batch_{int(time.time())}",
            configuration=shared.get("batch_config", BatchConfiguration()),
            items_processed=exec_res,
            progress=progress,
            start_time=shared.get("batch_start_time", datetime.now()),
            end_time=datetime.now(),
            status="completed" if progress.success_rate >= 0.9 else "completed_with_errors"
        )
        
        shared["batch_result"] = batch_result
        
        self.logger.info(
            f"Batch processing complete: {successful}/{len(exec_res)} successful. "
            f"Throughput: {progress.current_throughput:.1f} items/sec"
        )
        
        return None


# ============== Map-Reduce Nodes ==============

class MapNode(Node):
    """
    Performs the map phase of map-reduce.
    Transforms input data into key-value pairs.
    """
    
    def __init__(self, mapper_count: int = 4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mapper_count = mapper_count
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> List[MapTask]:
        """Prepare map tasks."""
        input_data = shared.get("mapreduce_input", [])
        
        # Create map tasks
        tasks = []
        for i, data in enumerate(input_data):
            tasks.append(MapTask(
                task_id=f"map_task_{i}",
                input_data=data,
                mapper_name="word_count"  # Example mapper
            ))
        
        return tasks
    
    def exec(self, prep_res: List[MapTask]) -> List[MapResult]:
        """Execute map tasks in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.mapper_count) as executor:
            future_to_task = {
                executor.submit(self._execute_map_task, task): task
                for task in prep_res
            }
            
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    task_results = future.result()
                    results.extend(task_results)
                except Exception as e:
                    self.logger.error(f"Map task {task.task_id} failed: {e}")
        
        return results
    
    def _execute_map_task(self, task: MapTask) -> List[MapResult]:
        """Execute a single map task."""
        start = time.time()
        results = []
        
        # Example: word count mapper
        if task.mapper_name == "word_count":
            text = str(task.input_data)
            words = text.lower().split()
            
            for word in words:
                results.append(MapResult(
                    task_id=task.task_id,
                    key=word,
                    value=1,
                    processing_time_ms=(time.time() - start) * 1000,
                    worker_id=f"mapper_{id(self) % self.mapper_count}"
                ))
        
        return results
    
    def post(self, shared: Dict[str, Any], prep_res: List[MapTask], exec_res: List[MapResult]) -> Optional[str]:
        """Store map results for reduce phase."""
        shared["map_results"] = exec_res
        
        self.logger.info(f"Map phase complete: {len(exec_res)} key-value pairs generated")
        
        return None


class ReduceNode(Node):
    """
    Performs the reduce phase of map-reduce.
    Aggregates values for each key.
    """
    
    def __init__(self, reducer_count: int = 2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reducer_count = reducer_count
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> List[ReduceTask]:
        """Prepare reduce tasks by grouping map results."""
        map_results = shared.get("map_results", [])
        
        # Group by key (shuffle phase)
        key_groups = {}
        for result in map_results:
            if result.key not in key_groups:
                key_groups[result.key] = []
            key_groups[result.key].append(result.value)
        
        # Create reduce tasks
        tasks = []
        for key, values in key_groups.items():
            tasks.append(ReduceTask(
                key=key,
                values=values,
                reducer_name="sum"  # Example reducer
            ))
        
        return tasks
    
    def exec(self, prep_res: List[ReduceTask]) -> List[ReduceResult]:
        """Execute reduce tasks in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.reducer_count) as executor:
            future_to_task = {
                executor.submit(self._execute_reduce_task, task): task
                for task in prep_res
            }
            
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Reduce task for key {task.key} failed: {e}")
        
        return results
    
    def _execute_reduce_task(self, task: ReduceTask) -> ReduceResult:
        """Execute a single reduce task."""
        start = time.time()
        
        # Example: sum reducer
        if task.reducer_name == "sum":
            result = sum(task.values)
        else:
            result = task.values  # Default: return values as-is
        
        return ReduceResult(
            key=task.key,
            result=result,
            value_count=len(task.values),
            processing_time_ms=(time.time() - start) * 1000
        )
    
    def post(self, shared: Dict[str, Any], prep_res: List[ReduceTask], exec_res: List[ReduceResult]) -> Optional[str]:
        """Store reduce results."""
        shared["reduce_results"] = exec_res
        
        # Sort by result value (for word count example)
        sorted_results = sorted(exec_res, key=lambda x: x.result, reverse=True)
        shared["top_results"] = sorted_results[:10]  # Top 10
        
        self.logger.info(f"Reduce phase complete: {len(exec_res)} unique keys")
        
        return None


# ============== Pipeline Parallelization ==============

class ParallelPipelineNode(Node):
    """
    Executes pipeline stages with parallelism.
    Each stage can have multiple parallel workers.
    """
    
    def __init__(self, pipeline_stages: List[PipelineStage] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipeline_stages = pipeline_stages or self._default_pipeline()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _default_pipeline(self) -> List[PipelineStage]:
        """Default pipeline configuration."""
        return [
            PipelineStage(stage_name="validation", parallelism=4),
            PipelineStage(stage_name="transformation", parallelism=3),
            PipelineStage(stage_name="enrichment", parallelism=2),
            PipelineStage(stage_name="output", parallelism=1)
        ]
    
    def prep(self, shared: Dict[str, Any]) -> List[Any]:
        """Prepare pipeline input."""
        return shared.get("pipeline_input", [])
    
    def exec(self, prep_res: List[Any]) -> PipelineExecution:
        """Execute pipeline stages."""
        pipeline_id = f"pipeline_{int(time.time())}"
        stage_results = []
        total_start = time.time()
        
        # Execute each stage
        current_data = prep_res
        for stage in self.pipeline_stages:
            stage_result = self._execute_stage(stage, current_data)
            stage_results.append(stage_result)
            
            # Use output of this stage as input for next
            if stage_result.success:
                current_data = stage_result.output_data
            else:
                # Pipeline failed at this stage
                break
        
        # Determine bottleneck stage (slowest)
        bottleneck = max(stage_results, key=lambda x: x.execution_time_ms).stage_name
        
        # Calculate parallel speedup
        sequential_time = sum(s.execution_time_ms * s.parallel_executions for s in stage_results)
        parallel_time = (time.time() - total_start) * 1000
        
        return PipelineExecution(
            pipeline_id=pipeline_id,
            stages=self.pipeline_stages,
            stage_results=stage_results,
            total_execution_time_ms=parallel_time,
            parallel_speedup=sequential_time / parallel_time if parallel_time > 0 else 1.0,
            bottleneck_stage=bottleneck,
            overall_success=all(s.success for s in stage_results)
        )
    
    def _execute_stage(self, stage: PipelineStage, input_data: List[Any]) -> StageResult:
        """Execute a single pipeline stage with parallelism."""
        start = time.time()
        output_data = []
        errors = []
        
        # Execute stage with specified parallelism
        with ThreadPoolExecutor(max_workers=stage.parallelism) as executor:
            future_to_item = {
                executor.submit(self._process_stage_item, stage.stage_name, item): item
                for item in input_data
            }
            
            for future in as_completed(future_to_item):
                try:
                    result = future.result()
                    output_data.append(result)
                except Exception as e:
                    errors.append(str(e))
                    if not stage.optional:
                        # Required stage failed
                        break
        
        return StageResult(
            stage_name=stage.stage_name,
            input_data=input_data,
            output_data=output_data,
            success=len(errors) == 0 or stage.optional,
            execution_time_ms=(time.time() - start) * 1000,
            parallel_executions=stage.parallelism,
            errors=errors
        )
    
    def _process_stage_item(self, stage_name: str, item: Any) -> Any:
        """Process a single item in a stage."""
        # Simulate different stage processing
        if stage_name == "validation":
            time.sleep(random.uniform(0.05, 0.1))
            return {"valid": True, "data": item}
        elif stage_name == "transformation":
            time.sleep(random.uniform(0.1, 0.2))
            return {"transformed": str(item).upper()}
        elif stage_name == "enrichment":
            time.sleep(random.uniform(0.2, 0.3))
            return {"enriched": item, "metadata": {"processed": True}}
        else:
            return item
    
    def post(self, shared: Dict[str, Any], prep_res: List, exec_res: PipelineExecution) -> Optional[str]:
        """Store pipeline execution results."""
        shared["pipeline_execution"] = exec_res
        
        self.logger.info(
            f"Pipeline complete: {'Success' if exec_res.overall_success else 'Failed'}. "
            f"Speedup: {exec_res.parallel_speedup:.2f}x. "
            f"Bottleneck: {exec_res.bottleneck_stage}"
        )
        
        return "success" if exec_res.overall_success else "failure"


# ============== Performance Metrics Node ==============

class PerformanceMetricsNode(Node):
    """
    Collects and analyzes parallelization performance metrics.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather execution data from shared store."""
        return {
            "validation_summary": shared.get("validation_summary"),
            "batch_result": shared.get("batch_result"),
            "pipeline_execution": shared.get("pipeline_execution")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> ParallelizationMetrics:
        """Calculate overall performance metrics."""
        # Extract timing data
        sequential_time = 0
        parallel_time = 0
        worker_utilization = {}
        
        if prep_res["validation_summary"]:
            val = prep_res["validation_summary"]
            sequential_time += val.total_execution_time_ms
            parallel_time += val.parallel_execution_time_ms
        
        if prep_res["batch_result"]:
            batch = prep_res["batch_result"]
            # Estimate sequential time
            avg_item_time = batch.progress.elapsed_time_ms / batch.progress.processed_items
            sequential_time += avg_item_time * batch.progress.total_items
            parallel_time += batch.progress.elapsed_time_ms
            
            # Worker utilization from batch processing
            for result in batch.items_processed:
                worker = result.worker_id
                if worker not in worker_utilization:
                    worker_utilization[worker] = 0
                worker_utilization[worker] += result.processing_time_ms
        
        # Normalize worker utilization
        if worker_utilization:
            max_time = max(worker_utilization.values())
            for worker in worker_utilization:
                worker_utilization[worker] = worker_utilization[worker] / max_time
        
        # Calculate optimal worker count (simplified)
        optimal_workers = min(8, max(2, int(sequential_time / 1000)))  # 1 worker per second of work
        
        speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0
        efficiency = speedup / optimal_workers if optimal_workers > 0 else 1.0
        
        return ParallelizationMetrics(
            sequential_time_ms=sequential_time,
            parallel_time_ms=parallel_time,
            speedup_factor=speedup,
            efficiency=min(1.0, efficiency),
            worker_utilization=worker_utilization,
            overhead_ms=parallel_time - (sequential_time / optimal_workers),
            optimal_worker_count=optimal_workers
        )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: ParallelizationMetrics) -> Optional[str]:
        """Store performance metrics."""
        shared["performance_metrics"] = exec_res
        
        self.logger.info(
            f"Performance Analysis: Speedup={exec_res.speedup_factor:.2f}x, "
            f"Efficiency={exec_res.efficiency:.1%}, "
            f"Optimal Workers={exec_res.optimal_worker_count}"
        )
        
        return None