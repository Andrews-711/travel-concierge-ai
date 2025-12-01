"""
Observability Module: Logging, Tracing, and Metrics
Provides structured logging, request tracing, and performance metrics
"""
import logging
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
import uuid

# Configure structured logging
class StructuredLogger:
    """Structured JSON logger for better observability"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler with structured format
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        
        # Add handler if not already added
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    def _log_structured(self, level: str, message: str, **kwargs):
        """Log structured data as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        
        log_line = f"[{level}] {json.dumps(log_data)}"
        
        if level == "INFO":
            self.logger.info(log_line)
        elif level == "WARNING":
            self.logger.warning(log_line)
        elif level == "ERROR":
            self.logger.error(log_line)
        elif level == "DEBUG":
            self.logger.debug(log_line)
    
    def info(self, message: str, **kwargs):
        self._log_structured("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log_structured("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log_structured("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log_structured("DEBUG", message, **kwargs)


# Metrics Collection
class MetricsCollector:
    """In-memory metrics collector for performance monitoring"""
    
    def __init__(self):
        self.metrics = {
            "api_calls": {},
            "llm_calls": {},
            "errors": {},
            "response_times": []
        }
        self.start_time = datetime.utcnow()
    
    def record_api_call(self, endpoint: str, duration: float, status: str):
        """Record API endpoint call"""
        if endpoint not in self.metrics["api_calls"]:
            self.metrics["api_calls"][endpoint] = {
                "count": 0,
                "total_duration": 0,
                "success": 0,
                "errors": 0
            }
        
        self.metrics["api_calls"][endpoint]["count"] += 1
        self.metrics["api_calls"][endpoint]["total_duration"] += duration
        
        if status == "success":
            self.metrics["api_calls"][endpoint]["success"] += 1
        else:
            self.metrics["api_calls"][endpoint]["errors"] += 1
        
        self.metrics["response_times"].append({
            "endpoint": endpoint,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 100 response times
        if len(self.metrics["response_times"]) > 100:
            self.metrics["response_times"] = self.metrics["response_times"][-100:]
    
    def record_llm_call(self, model: str, tokens: int, duration: float):
        """Record LLM API call"""
        if model not in self.metrics["llm_calls"]:
            self.metrics["llm_calls"][model] = {
                "count": 0,
                "total_tokens": 0,
                "total_duration": 0
            }
        
        self.metrics["llm_calls"][model]["count"] += 1
        self.metrics["llm_calls"][model]["total_tokens"] += tokens
        self.metrics["llm_calls"][model]["total_duration"] += duration
    
    def record_error(self, error_type: str, endpoint: str):
        """Record error occurrence"""
        key = f"{endpoint}_{error_type}"
        if key not in self.metrics["errors"]:
            self.metrics["errors"][key] = 0
        self.metrics["errors"][key] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        # Calculate average response times per endpoint
        avg_times = {}
        for endpoint, data in self.metrics["api_calls"].items():
            if data["count"] > 0:
                avg_times[endpoint] = round(data["total_duration"] / data["count"], 3)
        
        return {
            "uptime_seconds": round(uptime, 2),
            "api_calls": self.metrics["api_calls"],
            "llm_calls": self.metrics["llm_calls"],
            "errors": self.metrics["errors"],
            "average_response_times": avg_times,
            "recent_response_times": self.metrics["response_times"][-10:]
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        total_calls = sum(data["count"] for data in self.metrics["api_calls"].values())
        total_errors = sum(self.metrics["errors"].values())
        total_llm_calls = sum(data["count"] for data in self.metrics["llm_calls"].values())
        total_tokens = sum(data["total_tokens"] for data in self.metrics["llm_calls"].values())
        
        return {
            "total_api_calls": total_calls,
            "total_errors": total_errors,
            "total_llm_calls": total_llm_calls,
            "total_tokens_used": total_tokens,
            "uptime_seconds": round((datetime.utcnow() - self.start_time).total_seconds(), 2)
        }


# Request Tracing
class RequestTracer:
    """Distributed tracing for request flows"""
    
    def __init__(self):
        self.active_traces = {}
    
    def start_trace(self, trace_id: Optional[str] = None) -> str:
        """Start a new trace"""
        if not trace_id:
            trace_id = str(uuid.uuid4())
        
        self.active_traces[trace_id] = {
            "trace_id": trace_id,
            "start_time": time.time(),
            "spans": []
        }
        
        return trace_id
    
    def add_span(self, trace_id: str, name: str, attributes: Dict[str, Any] = None):
        """Add a span to trace"""
        if trace_id not in self.active_traces:
            return
        
        span = {
            "name": name,
            "timestamp": datetime.utcnow().isoformat(),
            "attributes": attributes or {}
        }
        
        self.active_traces[trace_id]["spans"].append(span)
    
    def end_trace(self, trace_id: str) -> Dict[str, Any]:
        """End trace and get trace data"""
        if trace_id not in self.active_traces:
            return {}
        
        trace = self.active_traces[trace_id]
        trace["end_time"] = time.time()
        trace["duration"] = round(trace["end_time"] - trace["start_time"], 3)
        
        # Remove from active traces
        del self.active_traces[trace_id]
        
        return trace
    
    def get_active_traces(self) -> Dict[str, Any]:
        """Get all active traces"""
        return {
            "count": len(self.active_traces),
            "traces": list(self.active_traces.keys())
        }


# Global instances
logger = StructuredLogger("travel_concierge")
metrics = MetricsCollector()
tracer = RequestTracer()


# Decorators for easy observability
def trace_operation(operation_name: str):
    """Decorator to trace function execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            trace_id = tracer.start_trace()
            start_time = time.time()
            
            try:
                logger.info(
                    f"Starting {operation_name}",
                    trace_id=trace_id,
                    operation=operation_name
                )
                
                tracer.add_span(trace_id, operation_name, {
                    "status": "started"
                })
                
                result = await func(*args, **kwargs)
                
                duration = time.time() - start_time
                tracer.add_span(trace_id, operation_name, {
                    "status": "completed",
                    "duration": duration
                })
                
                logger.info(
                    f"Completed {operation_name}",
                    trace_id=trace_id,
                    duration=round(duration, 3)
                )
                
                tracer.end_trace(trace_id)
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                tracer.add_span(trace_id, operation_name, {
                    "status": "error",
                    "error": str(e)
                })
                
                logger.error(
                    f"Error in {operation_name}",
                    trace_id=trace_id,
                    error=str(e),
                    duration=round(duration, 3)
                )
                
                tracer.end_trace(trace_id)
                raise
        
        return wrapper
    return decorator


def measure_performance(endpoint_name: str):
    """Decorator to measure endpoint performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                metrics.record_error(type(e).__name__, endpoint_name)
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_api_call(endpoint_name, duration, status)
        
        return wrapper
    return decorator
