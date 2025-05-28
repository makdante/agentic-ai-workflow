#src/core/database/repositories.py
"""
Data access layer for database operations.
Provides repository pattern implementation for all database models.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from src.core.database.models import (
    Repository, CodeAnalysis, Suggestion, WorkflowState,
    AnalysisStatus, SuggestionStatus, WorkflowStatus, SuggestionType
)
from config.database import get_db_session
from config.logging_config import get_logger

logger = get_logger(__name__)


class BaseRepository:
    """Base repository with common CRUD operations."""
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    def create(self, session: Session, **kwargs) -> any:
        """Create a new record."""
        obj = self.model_class(**kwargs)
        session.add(obj)
        session.flush()
        session.refresh(obj)
        return obj
    
    def get_by_id(self, session: Session, obj_id: int) -> Optional[any]:
        """Get record by ID."""
        return session.query(self.model_class).filter(
            self.model_class.id == obj_id
        ).first()
    
    def get_all(self, session: Session, limit: int = 100, offset: int = 0) -> List[any]:
        """Get all records with pagination."""
        return session.query(self.model_class).offset(offset).limit(limit).all()
    
    def update(self, session: Session, obj_id: int, **kwargs) -> Optional[any]:
        """Update record by ID."""
        obj = self.get_by_id(session, obj_id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.updated_at = datetime.utcnow()
            session.flush()
            session.refresh(obj)
        return obj
    
    def delete(self, session: Session, obj_id: int) -> bool:
        """Delete record by ID."""
        obj = self.get_by_id(session, obj_id)
        if obj:
            session.delete(obj)
            return True
        return False
    
    def count(self, session: Session) -> int:
        """Count total records."""
        return session.query(func.count(self.model_class.id)).scalar()


class RepositoryRepo(BaseRepository):
    """Repository operations for GitHub repositories."""
    
    def __init__(self):
        super().__init__(Repository)
    
    def get_by_url(self, session: Session, url: str) -> Optional[Repository]:
        """Get repository by URL."""
        return session.query(Repository).filter(Repository.url == url).first()
    
    def get_by_owner_name(self, session: Session, owner: str, name: str) -> Optional[Repository]:
        """Get repository by owner and name."""
        return session.query(Repository).filter(
            and_(Repository.owner == owner, Repository.name == name)
        ).first()
    
    def get_recently_analyzed(self, session: Session, limit: int = 10) -> List[Repository]:
        """Get recently analyzed repositories."""
        return session.query(Repository).filter(
            Repository.last_analyzed.isnot(None)
        ).order_by(desc(Repository.last_analyzed)).limit(limit).all()
    
    def update_clone_status(self, session: Session, repo_id: int, status: str, local_path: str = None) -> Optional[Repository]:
        """Update repository clone status."""
        update_data = {"clone_status": status}
        if local_path:
            update_data["local_path"] = local_path
        return self.update(session, repo_id, **update_data)
    
    def mark_analyzed(self, session: Session, repo_id: int) -> Optional[Repository]:
        """Mark repository as analyzed."""
        return self.update(session, repo_id, last_analyzed=datetime.utcnow())


class CodeAnalysisRepo(BaseRepository):
    """Repository operations for code analysis."""
    
    def __init__(self):
        super().__init__(CodeAnalysis)
    
    def get_by_repository(self, session: Session, repo_id: int, status: AnalysisStatus = None) -> List[CodeAnalysis]:
        """Get code analyses for a repository."""
        query = session.query(CodeAnalysis).filter(CodeAnalysis.repository_id == repo_id)
        if status:
            query = query.filter(CodeAnalysis.status == status)
        return query.all()
    
    def get_by_file_path(self, session: Session, repo_id: int, file_path: str) -> Optional[CodeAnalysis]:
        """Get analysis for specific file in repository."""
        return session.query(CodeAnalysis).filter(
            and_(
                CodeAnalysis.repository_id == repo_id,
                CodeAnalysis.file_path == file_path
            )
        ).first()
    
    def get_failed_analyses(self, session: Session) -> List[CodeAnalysis]:
        """Get all failed analyses for retry."""
        return session.query(CodeAnalysis).filter(
            CodeAnalysis.status == AnalysisStatus.FAILED
        ).all()
    
    def update_status(self, session: Session, analysis_id: int, status: AnalysisStatus) -> Optional[CodeAnalysis]:
        """Update analysis status."""
        return self.update(session, analysis_id, status=status)
    
    def get_summary_stats(self, session: Session, repo_id: int) -> Dict[str, Any]:
        """Get analysis summary statistics for repository."""
        stats = session.query(
            CodeAnalysis.status,
            func.count(CodeAnalysis.id).label('count'),
            func.avg(CodeAnalysis.complexity_score).label('avg_complexity'),
            func.avg(CodeAnalysis.quality_score).label('avg_quality')
        ).filter(
            CodeAnalysis.repository_id == repo_id
        ).group_by(CodeAnalysis.status).all()
        
        return {
            'total_files': sum(stat.count for stat in stats),
            'by_status': {stat.status.value: stat.count for stat in stats},
            'avg_complexity': sum(stat.avg_complexity or 0 for stat in stats) / len(stats) if stats else 0,
            'avg_quality': sum(stat.avg_quality or 0 for stat in stats) / len(stats) if stats else 0
        }


class SuggestionRepo(BaseRepository):
    """Repository operations for code suggestions."""
    
    def __init__(self):
        super().__init__(Suggestion)
    
    def get_by_analysis(self, session: Session, analysis_id: int, status: SuggestionStatus = None) -> List[Suggestion]:
        """Get suggestions for a code analysis."""
        query = session.query(Suggestion).filter(Suggestion.analysis_id == analysis_id)
        if status:
            query = query.filter(Suggestion.status == status)
        return query.order_by(desc(Suggestion.confidence_score)).all()
    
    def get_by_repository(self, session: Session, repo_id: int) -> List[Suggestion]:
        """Get all suggestions for a repository."""
        return session.query(Suggestion).join(CodeAnalysis).filter(
            CodeAnalysis.repository_id == repo_id
        ).order_by(desc(Suggestion.created_at)).all()
    
    def get_by_type(self, session: Session, suggestion_type: SuggestionType, status: SuggestionStatus = None) -> List[Suggestion]:
        """Get suggestions by type."""
        query = session.query(Suggestion).filter(Suggestion.type == suggestion_type)
        if status:
            query = query.filter(Suggestion.status == status)
        return query.order_by(desc(Suggestion.confidence_score)).all()
    
    def get_high_confidence(self, session: Session, min_confidence: float = 0.8) -> List[Suggestion]:
        """Get high-confidence suggestions."""
        return session.query(Suggestion).filter(
            Suggestion.confidence_score >= min_confidence
        ).order_by(desc(Suggestion.confidence_score)).all()
    
    def update_status(self, session: Session, suggestion_id: int, status: SuggestionStatus, feedback: str = None) -> Optional[Suggestion]:
        """Update suggestion status with optional feedback."""
        update_data = {"status": status, "reviewed_at": datetime.utcnow()}
        if feedback:
            update_data["feedback"] = feedback
        return self.update(session, suggestion_id, **update_data)
    
    def get_statistics(self, session: Session) -> Dict[str, Any]:
        """Get suggestion statistics."""
        stats = session.query(
            Suggestion.type,
            Suggestion.status,
            func.count(Suggestion.id).label('count'),
            func.avg(Suggestion.confidence_score).label('avg_confidence')
        ).group_by(Suggestion.type, Suggestion.status).all()
        
        return {
            'total_suggestions': session.query(func.count(Suggestion.id)).scalar(),
            'by_type_and_status': [
                {
                    'type': stat.type.value,
                    'status': stat.status.value,
                    'count': stat.count,
                    'avg_confidence': float(stat.avg_confidence or 0)
                }
                for stat in stats
            ]
        }


class WorkflowStateRepo(BaseRepository):
    """Repository operations for workflow states."""
    
    def __init__(self):
        super().__init__(WorkflowState)
    
    def get_by_workflow_id(self, session: Session, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow state by workflow ID."""
        return session.query(WorkflowState).filter(
            WorkflowState.workflow_id == workflow_id
        ).first()
    
    def get_by_repository(self, session: Session, repo_id: int) -> List[WorkflowState]:
        """Get workflow states for repository."""
        return session.query(WorkflowState).filter(
            WorkflowState.repository_id == repo_id
        ).order_by(desc(WorkflowState.created_at)).all()
    
    def get_active_workflows(self, session: Session) -> List[WorkflowState]:
        """Get currently active workflows."""
        active_statuses = [
            WorkflowStatus.INITIALIZED,
            WorkflowStatus.CLONING_REPO,
            WorkflowStatus.ANALYZING_CODE,
            WorkflowStatus.GENERATING_SUGGESTIONS,
            WorkflowStatus.TESTING_SUGGESTIONS,
            WorkflowStatus.CREATING_PR
        ]
        return session.query(WorkflowState).filter(
            WorkflowState.status.in_(active_statuses)
        ).all()
    
    def get_failed_workflows(self, session: Session) -> List[WorkflowState]:
        """Get failed workflows for analysis."""
        return session.query(WorkflowState).filter(
            WorkflowState.status == WorkflowStatus.FAILED
        ).order_by(desc(WorkflowState.updated_at)).all()
    
    def update_status(self, session: Session, workflow_id: str, status: WorkflowStatus, **kwargs) -> Optional[WorkflowState]:
        """Update workflow status."""
        workflow = self.get_by_workflow_id(session, workflow_id)
        if workflow:
            workflow.status = status
            for key, value in kwargs.items():
                setattr(workflow, key, value)
            workflow.updated_at = datetime.utcnow()
            session.flush()
            session.refresh(workflow)
        return workflow
    
    def get_workflow_statistics(self, session: Session) -> Dict[str, Any]:
        """Get workflow execution statistics."""
        stats = session.query(
            WorkflowState.status,
            func.count(WorkflowState.id).label('count'),
            func.avg(WorkflowState.execution_time_seconds).label('avg_execution_time')
        ).group_by(WorkflowState.status).all()
        
        return {
            'total_workflows': session.query(func.count(WorkflowState.id)).scalar(),
            'by_status': {stat.status.value: stat.count for stat in stats},
            'avg_execution_times': {
                stat.status.value: float(stat.avg_execution_time or 0) 
                for stat in stats if stat.avg_execution_time
            }
        }


# Repository instances
repository_repo = RepositoryRepo()
code_analysis_repo = CodeAnalysisRepo()
suggestion_repo = SuggestionRepo()
workflow_state_repo = WorkflowStateRepo()
