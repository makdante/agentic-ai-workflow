#tests/unit/test_core/test_database.py
"""
Unit tests for database functionality.
Tests models, connections, repositories, and migrations.
"""

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path
from sqlalchemy import text

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database.models import (
    Base, Repository, CodeAnalysis, Suggestion, WorkflowState,
    AnalysisStatus, SuggestionStatus, SuggestionType, WorkflowStatus
)
from src.core.database.repositories import (
    repository_repo, code_analysis_repo, suggestion_repo, workflow_state_repo
)
from src.core.database.connection import DatabaseConnection, TransactionManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    
    db_url = f"sqlite:///{temp_file.name}"
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield SessionLocal, engine
    
    # Cleanup
    os.unlink(temp_file.name)


@pytest.fixture
def db_session(temp_db):
    """Create a database session for testing."""
    SessionLocal, engine = temp_db
    session = SessionLocal()
    yield session
    session.close()


class TestDatabaseModels:
    """Test database models."""
    
    def test_repository_model_creation(self, db_session):
        """Test Repository model creation and basic operations."""
        repo = Repository(
            url="https://github.com/test/repo",
            name="repo",
            owner="test",
            description="Test repository",
            language="Python"
        )
        
        db_session.add(repo)
        db_session.commit()
        
        assert repo.id is not None
        assert repo.url == "https://github.com/test/repo"
        assert repo.clone_status == "pending"
        assert repo.created_at is not None
    
    def test_code_analysis_model_creation(self, db_session):
        """Test CodeAnalysis model creation and relationships."""
        # Create repository first
        repo = Repository(
            url="https://github.com/test/repo",
            name="repo",
            owner="test"
        )
        db_session.add(repo)
        db_session.flush()
        
        # Create analysis
        analysis = CodeAnalysis(
            repository_id=repo.id,
            file_path="src/main.py",
            language="Python",
            lines_of_code=100,
            complexity_score=3.5,
            quality_score=8.2,
            functions=["main", "helper"],
            classes=["MyClass"],
            summary="Main application file"
        )
        
        db_session.add(analysis)
        db_session.commit()
        
        assert analysis.id is not None
        assert analysis.repository_id == repo.id
        assert analysis.status == AnalysisStatus.PENDING
        assert analysis.repository == repo
    
    def test_suggestion_model_creation(self, db_session):
        """Test Suggestion model creation and relationships."""
        # Create repository and analysis
        repo = Repository(url="https://github.com/test/repo", name="repo", owner="test")
        db_session.add(repo)
        db_session.flush()
        
        analysis = CodeAnalysis(
            repository_id=repo.id,
            file_path="src/main.py",
            language="Python"
        )
        db_session.add(analysis)
        db_session.flush()
        
        # Create suggestion
        suggestion = Suggestion(
            analysis_id=analysis.id,
            type=SuggestionType.BUG_FIX,
            title="Fix null pointer exception",
            description="Add null check before accessing variable",
            original_code="x.value",
            suggested_code="if x: x.value",
            confidence_score=0.95,
            agent_name="developer_agent"
        )
        
        db_session.add(suggestion)
        db_session.commit()
        
        assert suggestion.id is not None
        assert suggestion.status == SuggestionStatus.GENERATED
        assert suggestion.analysis == analysis
    
    def test_workflow_state_model_creation(self, db_session):
        """Test WorkflowState model creation and methods."""
        # Create repository
        repo = Repository(url="https://github.com/test/repo", name="repo", owner="test")
        db_session.add(repo)
        db_session.flush()
        
        # Create workflow state
        workflow = WorkflowState(
            repository_id=repo.id,
            workflow_id="workflow_123",
            status=WorkflowStatus.INITIALIZED
        )
        
        db_session.add(workflow)
        db_session.commit()
        
        assert workflow.id is not None
        assert workflow.progress_percentage == 0.0
        assert workflow.repository == repo
        
        # Test progress update
        workflow.update_progress(50.0, "analyzing_code", "developer_agent")
        assert workflow.progress_percentage == 50.0
        assert workflow.current_step == "analyzing_code"
        assert workflow.current_agent == "developer_agent"
        
        # Test completion
        workflow.mark_completed(success=True)
        assert workflow.status == WorkflowStatus.COMPLETED
        assert workflow.progress_percentage == 100.0
        assert workflow.end_time is not None
        
        # Test error addition
        workflow.add_error("Test error", "test_error")
        assert len(workflow.error_log) == 1
        assert workflow.error_log[0]["message"] == "Test error"


class TestDatabaseRepositories:
    """Test repository pattern implementations."""
    
    def test_repository_repo_operations(self, db_session):
        """Test RepositoryRepo CRUD operations."""
        # Create
        repo = repository_repo.create(
            db_session,
            url="https://github.com/test/repo",
            name="repo",
            owner="test",
            description="Test repository"
        )
        
        assert repo.id is not None
        assert repo.url == "https://github.com/test/repo"
        
        # Read
        found_repo = repository_repo.get_by_url(db_session, "https://github.com/test/repo")
        assert found_repo is not None
        assert found_repo.id == repo.id
        
        # Update
        updated_repo = repository_repo.update(
            db_session, 
            repo.id, 
            clone_status="completed",
            local_path="/tmp/repo"
        )
        assert updated_repo.clone_status == "completed"
        assert updated_repo.local_path == "/tmp/repo"
        
        # Delete
        success = repository_repo.delete(db_session, repo.id)
        assert success is True
        
        deleted_repo = repository_repo.get_by_id(db_session, repo.id)
        assert deleted_repo is None
    
    def test_code_analysis_repo_operations(self, db_session):
        """Test CodeAnalysisRepo operations."""
        # Setup
        repo = repository_repo.create(
            db_session,
            url="https://github.com/test/repo",
            name="repo",
            owner="test"
        )
        
        # Create analysis
        analysis = code_analysis_repo.create(
            db_session,
            repository_id=repo.id,
            file_path="src/main.py",
            language="Python",
            status=AnalysisStatus.COMPLETED
        )
        
        # Test get by repository
        analyses = code_analysis_repo.get_by_repository(db_session, repo.id)
        assert len(analyses) == 1
        assert analyses[0].id == analysis.id
        
        # Test get by file path
        found_analysis = code_analysis_repo.get_by_file_path(
            db_session, repo.id, "src/main.py"
        )
        assert found_analysis.id == analysis.id
        
        # Test status update
        updated_analysis = code_analysis_repo.update_status(
            db_session, analysis.id, AnalysisStatus.FAILED
        )
        assert updated_analysis.status == AnalysisStatus.FAILED
        
        # Test summary stats
        stats = code_analysis_repo.get_summary_stats(db_session, repo.id)
        assert stats['total_files'] == 1
        assert AnalysisStatus.FAILED.value in stats['by_status']
    
    def test_suggestion_repo_operations(self, db_session):
        """Test SuggestionRepo operations."""
        # Setup
        repo = repository_repo.create(
            db_session,
            url="https://github.com/test/repo",
            name="repo",
            owner="test"
        )
        
        analysis = code_analysis_repo.create(
            db_session,
            repository_id=repo.id,
            file_path="src/main.py",
            language="Python"
        )
        
        # Create suggestions
        suggestion1 = suggestion_repo.create(
            db_session,
            analysis_id=analysis.id,
            type=SuggestionType.BUG_FIX,
            title="Fix bug",
            description="Fix the bug",
            confidence_score=0.9
        )
        
        suggestion2 = suggestion_repo.create(
            db_session,
            analysis_id=analysis.id,
            type=SuggestionType.IMPROVEMENT,
            title="Improve code",
            description="Improve the code",
            confidence_score=0.7
        )
        
        # Test get by analysis
        suggestions = suggestion_repo.get_by_analysis(db_session, analysis.id)
        assert len(suggestions) == 2
        # Should be ordered by confidence score descending
        assert suggestions[0].confidence_score >= suggestions[1].confidence_score
        
        # Test get by type
        bug_fixes = suggestion_repo.get_by_type(db_session, SuggestionType.BUG_FIX)
        assert len(bug_fixes) == 1
        assert bug_fixes[0].id == suggestion1.id
        
        # Test high confidence suggestions
        high_conf = suggestion_repo.get_high_confidence(db_session, min_confidence=0.8)
        assert len(high_conf) == 1
        assert high_conf[0].id == suggestion1.id
        
        # Test status update
        updated_suggestion = suggestion_repo.update_status(
            db_session, suggestion1.id, SuggestionStatus.APPROVED, "Looks good"
        )
        assert updated_suggestion.status == SuggestionStatus.APPROVED
        assert updated_suggestion.feedback == "Looks good"
        assert updated_suggestion.reviewed_at is not None
    
    def test_workflow_state_repo_operations(self, db_session):
        """Test WorkflowStateRepo operations."""
        # Setup
        repo = repository_repo.create(
            db_session,
            url="https://github.com/test/repo",
            name="repo",
            owner="test"
        )
        
        # Create workflow states
        workflow1 = workflow_state_repo.create(
            db_session,
            repository_id=repo.id,
            workflow_id="workflow_123",
            status=WorkflowStatus.IN_PROGRESS
        )
        
        workflow2 = workflow_state_repo.create(
            db_session,
            repository_id=repo.id,
            workflow_id="workflow_456",
            status=WorkflowStatus.COMPLETED
        )
        
        # Test get by workflow ID
        found_workflow = workflow_state_repo.get_by_workflow_id(db_session, "workflow_123")
        assert found_workflow.id == workflow1.id
        
        # Test get by repository
        workflows = workflow_state_repo.get_by_repository(db_session, repo.id)
        assert len(workflows) == 2
        
        # Test get active workflows
        active_workflows = workflow_state_repo.get_active_workflows(db_session)
        assert len(active_workflows) == 1
        assert active_workflows[0].id == workflow1.id
        
        # Test status update
        updated_workflow = workflow_state_repo.update_status(
            db_session, "workflow_123", WorkflowStatus.FAILED,
            current_step="error_occurred"
        )
        assert updated_workflow.status == WorkflowStatus.FAILED
        assert updated_workflow.current_step == "error_occurred"


class TestDatabaseConnection:
    """Test database connection utilities."""
    
    def test_database_connection_creation(self):
        """Test DatabaseConnection instantiation."""
        db_conn = DatabaseConnection()
        assert db_conn.session_factory is not None
    
    def test_connection_with_retry(self, temp_db):
        """Test connection retry mechanism."""
        SessionLocal, engine = temp_db
        db_conn = DatabaseConnection()
        db_conn.session_factory = SessionLocal
        
        def test_operation(session):
            return session.execute(text("SELECT 1")).scalar()
        
        result = db_conn.execute_with_retry(test_operation)
        assert result == 1
    
    def test_transaction_manager(self, db_session):
        """Test transaction manager context."""
        with TransactionManager(db_session) as session:
            repo = Repository(
                url="https://github.com/test/repo",
                name="repo",
                owner="test"
            )
            session.add(repo)
            # Transaction should commit automatically
        
        # Verify data was committed
        found_repo = db_session.query(Repository).filter_by(
            url="https://github.com/test/repo"
        ).first()
        assert found_repo is not None
    
    def test_transaction_manager_rollback(self, db_session):
        """Test transaction manager rollback on exception."""
        try:
            with TransactionManager(db_session) as session:
                repo = Repository(
                    url="https://github.com/test/repo",
                    name="repo",
                    owner="test"
                )
                session.add(repo)
                # Force an exception
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Verify data was rolled back
        found_repo = db_session.query(Repository).filter_by(
            url="https://github.com/test/repo"
        ).first()
        assert found_repo is None


class TestDatabaseIntegration:
    """Integration tests for database functionality."""
    
    def test_complete_workflow_data_flow(self, db_session):
        """Test complete data flow through all models."""
        # Create repository
        repo = repository_repo.create(
            db_session,
            url="https://github.com/test/repo",
            name="repo",
            owner="test",
            description="Integration test repository"
        )
        
        # Create workflow
        workflow = workflow_state_repo.create(
            db_session,
            repository_id=repo.id,
            workflow_id="integration_test_workflow",
            status=WorkflowStatus.ANALYZING_CODE
        )
        
        # Create analyses
        analysis1 = code_analysis_repo.create(
            db_session,
            repository_id=repo.id,
            file_path="src/main.py",
            language="Python",
            status=AnalysisStatus.COMPLETED,
            complexity_score=5.2,
            quality_score=7.8
        )
        
        analysis2 = code_analysis_repo.create(
            db_session,
            repository_id=repo.id,
            file_path="src/utils.py",
            language="Python",
            status=AnalysisStatus.COMPLETED,
            complexity_score=3.1,
            quality_score=8.9
        )
        
        # Create suggestions
        suggestion1 = suggestion_repo.create(
            db_session,
            analysis_id=analysis1.id,
            type=SuggestionType.BUG_FIX,
            title="Fix null pointer",
            description="Add null check",
            confidence_score=0.95
        )
        
        suggestion2 = suggestion_repo.create(
            db_session,
            analysis_id=analysis1.id,
            type=SuggestionType.OPTIMIZATION,
            title="Optimize loop",
            description="Use list comprehension",
            confidence_score=0.85
        )
        
        suggestion3 = suggestion_repo.create(
            db_session,
            analysis_id=analysis2.id,
            type=SuggestionType.IMPROVEMENT,
            title="Add docstring",
            description="Add function documentation",
            confidence_score=0.75
        )
        
        # Test repository summary
        analyses = code_analysis_repo.get_by_repository(db_session, repo.id)
        assert len(analyses) == 2
        
        all_suggestions = suggestion_repo.get_by_repository(db_session, repo.id)
        assert len(all_suggestions) == 3
        
        # Test workflow completion
        workflow_state_repo.update_status(
            db_session, "integration_test_workflow", WorkflowStatus.COMPLETED,
            total_suggestions=3,
            approved_suggestions=2
        )
        
        final_workflow = workflow_state_repo.get_by_workflow_id(
            db_session, "integration_test_workflow"
        )
        assert final_workflow.status == WorkflowStatus.COMPLETED
        assert final_workflow.total_suggestions == 3
        assert final_workflow.approved_suggestions == 2
        
        # Test cleanup (cascade deletes)
        repository_repo.delete(db_session, repo.id)
        
        # Verify all related data was deleted
        remaining_analyses = code_analysis_repo.get_by_repository(db_session, repo.id)
        assert len(remaining_analyses) == 0
        
        remaining_workflows = workflow_state_repo.get_by_repository(db_session, repo.id)
        assert len(remaining_workflows) == 0