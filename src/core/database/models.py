#src/core/database/models.py
"""
Database models for the Agentic AI Workflow.
Defines SQLAlchemy models for repositories, analysis, suggestions, and workflow states.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, JSON, 
    ForeignKey, Float, Enum as SQLEnum
)
from sqlalchemy.orm import relationship

from config.database import Base


class AnalysisStatus(Enum):
    """Status of code analysis."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SuggestionType(Enum):
    """Type of code suggestion."""
    BUG_FIX = "bug_fix"
    IMPROVEMENT = "improvement"
    OPTIMIZATION = "optimization"
    CODE_COMPLETION = "code_completion"
    REFACTORING = "refactoring"


class SuggestionStatus(Enum):
    """Status of suggestion."""
    GENERATED = "generated"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class WorkflowStatus(Enum):
    """Status of workflow execution."""
    INITIALIZED = "initialized"
    CLONING_REPO = "cloning_repo"
    ANALYZING_CODE = "analyzing_code"
    GENERATING_SUGGESTIONS = "generating_suggestions"
    TESTING_SUGGESTIONS = "testing_suggestions"
    CREATING_PR = "creating_pr"
    COMPLETED = "completed"
    FAILED = "failed"


class Repository(Base):
    """Repository model for storing GitHub repository information."""
    
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    owner = Column(String(100), nullable=False)
    branch = Column(String(50), default="main")
    local_path = Column(String(500))
    clone_status = Column(String(20), default="pending")
    
    # Repository metadata
    description = Column(Text)
    language = Column(String(50))
    size_kb = Column(Integer)
    file_count = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analyzed = Column(DateTime)
    
    # Relationships
    analyses = relationship("CodeAnalysis", back_populates="repository", cascade="all, delete-orphan")
    workflow_states = relationship("WorkflowState", back_populates="repository", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Repository(id={self.id}, name='{self.name}', owner='{self.owner}')>"


class CodeAnalysis(Base):
    """Code analysis results for repository files."""
    
    __tablename__ = "code_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    
    # Analysis results
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    language = Column(String(50))
    lines_of_code = Column(Integer)
    complexity_score = Column(Float)
    quality_score = Column(Float)
    
    # Extracted code elements
    functions = Column(JSON)  # List of function definitions
    classes = Column(JSON)    # List of class definitions
    imports = Column(JSON)    # List of imports/dependencies
    comments = Column(JSON)   # List of comments and docstrings
    
    # Analysis summary
    summary = Column(Text)
    issues_found = Column(JSON)  # List of detected issues
    dependencies = Column(JSON)  # File dependencies
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="analyses")
    suggestions = relationship("Suggestion", back_populates="analysis", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<CodeAnalysis(id={self.id}, file_path='{self.file_path}', status='{self.status}')>"


class Suggestion(Base):
    """Code improvement suggestions generated by agents."""
    
    __tablename__ = "suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("code_analyses.id"), nullable=False)
    
    # Suggestion details
    type = Column(SQLEnum(SuggestionType), nullable=False)
    status = Column(SQLEnum(SuggestionStatus), default=SuggestionStatus.GENERATED)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Code changes
    original_code = Column(Text)
    suggested_code = Column(Text)
    line_start = Column(Integer)
    line_end = Column(Integer)
    
    # Metadata
    confidence_score = Column(Float)  # Agent's confidence in suggestion
    impact_score = Column(Float)      # Expected impact of change
    agent_name = Column(String(50))   # Agent that generated suggestion
    
    # Testing results
    test_results = Column(JSON)       # Results from tester agent
    feedback = Column(Text)           # Feedback from testing
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = Column(DateTime)
    
    # Relationships
    analysis = relationship("CodeAnalysis", back_populates="suggestions")
    
    def __repr__(self) -> str:
        return f"<Suggestion(id={self.id}, type='{self.type}', status='{self.status}')>"


class WorkflowState(Base):
    """Workflow execution state and progress tracking."""
    
    __tablename__ = "workflow_states"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    
    # Workflow identification
    workflow_id = Column(String(50), unique=True, index=True, nullable=False)
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.INITIALIZED)
    
    # Progress tracking
    current_agent = Column(String(50))
    current_step = Column(String(100))
    progress_percentage = Column(Float, default=0.0)
    
    # Execution details
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    execution_time_seconds = Column(Float)
    
    # Results and metadata
    total_files_analyzed = Column(Integer, default=0)
    total_suggestions = Column(Integer, default=0)
    approved_suggestions = Column(Integer, default=0)
    
    # Configuration and context
    agent_config = Column(JSON)       # Agent configuration used
    context_data = Column(JSON)       # Workflow context and state
    error_log = Column(JSON)          # Error messages and stack traces
    
    # GitHub integration
    branch_name = Column(String(100)) # Created branch for suggestions
    pull_request_url = Column(String(500))  # Created PR URL
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="workflow_states")
    
    def __repr__(self) -> str:
        return f"<WorkflowState(id={self.id}, workflow_id='{self.workflow_id}', status='{self.status}')>"
    
    def update_progress(self, percentage: float, step: str, agent: str = None) -> None:
        """Update workflow progress."""
        self.progress_percentage = min(100.0, max(0.0, percentage))
        self.current_step = step
        if agent:
            self.current_agent = agent
        self.updated_at = datetime.utcnow()
    
    def mark_completed(self, success: bool = True) -> None:
        """Mark workflow as completed."""
        self.status = WorkflowStatus.COMPLETED if success else WorkflowStatus.FAILED
        self.end_time = datetime.utcnow()
        self.progress_percentage = 100.0
        if self.start_time:
            self.execution_time_seconds = (self.end_time - self.start_time).total_seconds()
    
    def add_error(self, error_message: str, error_type: str = "general") -> None:
        """Add error to workflow state."""
        if not self.error_log:
            self.error_log = []
        
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": error_type,
            "message": error_message,
            "agent": self.current_agent,
            "step": self.current_step
        }
        self.error_log.append(error_entry)
