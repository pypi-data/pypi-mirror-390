"""
Shared data models for the Rohkun analysis platform.

Defines Pydantic models for endpoints, API calls, connections, and analysis results.
"""

from typing import List, Optional, Literal, TYPE_CHECKING
from pydantic import BaseModel
from enum import Enum

if TYPE_CHECKING:
    from server.shared.accuracy_report_schema import AccuracyReport


class DetectionConfidence(str, Enum):
    """Confidence levels for detected items based on accuracy boundaries."""
    CERTAIN = "certain"  # 100% - deterministic, structural (decorators with literals)
    HIGH = "high"  # 90-95% - framework conventions (static routes)
    MEDIUM = "medium"  # 60-80% - dynamic patterns (computed routes, cross-file)
    LOW = "low"  # <60% - heuristics only
    UNKNOWN = "unknown"  # 0% - runtime-dependent (env vars, eval)


class EvidenceType(str, Enum):
    """Evidence types for detection - determines confidence hierarchy."""
    STATIC_AST = "static_ast"  # AST-based extraction (highest confidence)
    FRAMEWORK_RULE = "framework_rule"  # Framework pattern matching
    STATIC_HEURISTIC = "static_heuristic"  # Regex/heuristic patterns
    RUNTIME_TRACE = "runtime_trace"  # Dynamic runtime detection


class Endpoint(BaseModel):
    """Backend endpoint definition."""
    path: str
    method: str  # GET, POST, PUT, DELETE, etc.
    handler: str  # Function/class name
    file_path: str
    line_number: int
    confidence: DetectionConfidence = DetectionConfidence.HIGH  # Detection confidence
    detection_method: str = "unknown"  # How it was detected (decorator, route_table, etc.)
    has_literal_path: bool = True  # True if path is a literal string
    requires_cross_file: bool = False  # True if detection required cross-file analysis
    evidence: List[EvidenceType] = []  # Evidence types that support this detection
    signature: Optional[str] = None  # Function signature (params, return type)
    decorators: List[str] = []  # Decorators/annotations (e.g., @app.route, @router.get)
    doc: Optional[str] = None  # Docstring/comment
    is_dummy_data: bool = False  # Flag for test/example code
    dummy_reason: Optional[str] = None  # Reason why it's dummy data
    context: Optional[str] = None  # Additional context


class ApiCall(BaseModel):
    """Frontend API call."""
    url: str
    method: str
    file_path: str
    line_number: int
    confidence: DetectionConfidence = DetectionConfidence.HIGH  # Detection confidence
    detection_method: str = "unknown"  # How it was detected (fetch, axios, react_query, etc.)
    has_literal_url: bool = True  # True if URL is a literal string
    requires_cross_file: bool = False  # True if detection required cross-file analysis
    evidence: List[EvidenceType] = []  # Evidence types that support this detection
    call_expression: Optional[str] = None  # The actual call expression (for AST-based)
    template_literal_parts: Optional[List[str]] = None  # Template literal parts if applicable
    is_dummy_data: bool = False  # Flag for test/example code
    dummy_reason: Optional[str] = None  # Reason why it's dummy data
    context: Optional[str] = None  # Additional context


class Connection(BaseModel):
    """Connection between endpoint and API call."""
    endpoint: str
    method: str
    used_in: List[str]  # List of file paths where it's called
    confidence: float = 0.0  # Confidence score (0.0-1.0)
    frontend_call: str = ""  # The actual frontend call/function
    frontend_file: str = ""  # Frontend file path
    frontend_line_number: int = 0  # Line number in frontend file
    backend_endpoint: str = ""  # Backend endpoint path
    backend_file: str = ""  # Backend file path
    backend_line_number: int = 0  # Line number in backend file


class Orphan(BaseModel):
    """Orphaned endpoint or API call."""
    item: str  # Endpoint or API call
    type: str  # "endpoint" or "api_call"
    reason: str
    file_path: str
    confidence: DetectionConfidence = DetectionConfidence.UNKNOWN  # Detection confidence
    detection_method: str = "unknown"  # How it was detected
    is_dummy_data: bool = False  # Flag for test/example code
    context: Optional[str] = None  # Additional context (e.g., "inside test block")


class DummyData(BaseModel):
    """Dummy/mock data found in frontend code."""
    location: str  # File path and description
    type: str  # "hardcoded_array", "mock_object", "placeholder_data", "static_data"
    file_path: str
    line_number: int
    reason: str  # Why it's considered dummy data


class FunctionDefinition(BaseModel):
    """Function definition found in code."""
    name: str  # Function name
    full_name: str  # Full qualified name (with class/module if applicable)
    file_path: str
    line_number: int
    parameters: List[str]  # List of parameter names
    is_async: bool = False
    is_method: bool = False  # True if it's a class method
    class_name: Optional[str] = None  # Class name if it's a method
    visibility: str = "public"  # public, private, protected (for OOP languages)
    confidence: DetectionConfidence = DetectionConfidence.CERTAIN  # Function definitions are 100% accurate (CERTAIN)


class FunctionCall(BaseModel):
    """Function call/invocation found in code."""
    name: str  # Function name being called
    full_name: Optional[str] = None  # Full qualified name if available
    file_path: str
    line_number: int
    is_method_call: bool = False  # True if it's a method call (obj.method())
    object_name: Optional[str] = None  # Object/module name if it's a method call
    is_imported: bool = False  # True if function is imported from another module
    confidence: DetectionConfidence = DetectionConfidence.CERTAIN  # Static function calls are 100% accurate (CERTAIN)


class FunctionConnection(BaseModel):
    """Connection between function definition and function call."""
    definition: FunctionDefinition
    call: FunctionCall
    is_resolved: bool = True  # True if call successfully matches a definition


class OrphanFunction(BaseModel):
    """Orphaned function (defined but never called, or called but not defined)."""
    function_name: str  # Function name
    file_path: str
    line_number: int
    type: str  # "unused" (defined but never called) or "missing" (called but not defined)
    reason: str  # Explanation
    full_name: Optional[str] = None  # Full qualified name if available


class AnalysisMetrics(BaseModel):
    """
    Unified metrics model - SINGLE SOURCE OF TRUTH for all analysis metrics.
    
    This model is created during analysis and stored once in reports.summary.
    All outputs (CLI, web app, dashboard, database) read from this same model.
    No duplication - one entity represented everywhere.
    """
    # Analysis counts
    files_processed: int = 0
    lines_analyzed: int = 0
    total_endpoints: int = 0
    total_api_calls: int = 0
    connected_endpoints: int = 0
    orphaned_endpoints: int = 0
    orphaned_api_calls: int = 0
    uncertain_connections: int = 0
    
    # Function analysis counts
    total_functions: int = 0
    total_function_calls: int = 0
    connected_functions: int = 0
    orphaned_functions: int = 0
    missing_functions: int = 0
    
    # Framework detection
    framework: str = "Unknown"
    
    # Savings metrics (calculated from analysis)
    tokens_saved: int = 0
    cost_savings_usd: float = 0.0
    savings_percent: int = 0
    
    
    # Analysis metadata
    project_name: str = "unknown"
    analyzed_date: str = ""
    
    class Config:
        """Pydantic config."""
        json_encoders = {
            # Ensure proper serialization
        }


class Report(BaseModel):
    """Analysis report - SINGLE SOURCE OF TRUTH."""
    project_id: str
    connections: List[Connection]
    orphaned_endpoints: List[Orphan]
    orphaned_api_calls: List[Orphan]
    dummy_data: List[DummyData]
    function_connections: List[FunctionConnection] = []
    orphaned_functions: List[OrphanFunction] = []
    summary: dict  # Contains AnalysisMetrics (serialized)
    metrics: Optional[AnalysisMetrics] = None  # Direct access to metrics model
    
    # NEW: Accuracy Report Integration
    accuracy_report: Optional['AccuracyReport'] = None  # Confidence-based accuracy metrics


