#src/core/exceptions/workflow_exceptions.py
"""
Workflow-specific exceptions for state management and orchestration errors.
"""

from typing import Optional, Dict, Any, List


class WorkflowException(Exception):
    """Base exception for workflow-related errors."""
    
    def __init__(
        self, 
        message: str,
        workflow_id: str = None,
        current_state: str = None,
        error_code: str = None,
        context: Dict[str, Any] = None
    ):
        self.message = message
        self.workflow_id = workflow_id
        self.current_state = current_state
        self.error_code = error_code
        self.context = context or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "exception_type": self.__class__.__name__,
            "message": self.message,
            "workflow_id": self.workflow_id,
            "current_state": self.current_state,
            "error_code": self.error_code,
            "context": self.context
        }


class WorkflowStateException(WorkflowException):
    """Exception raised during workflow state transitions."""
    
    def __init__(
        self, 
        message: str,
        workflow_id: str = None,
        from_state: str = None,
        to_state: str = None,
        **kwargs
    ):
        self.from_state = from_state
        self.to_state = to_state
        context = kwargs.get('context', {})
        context.update({
            "from_state": from_state,
            "to_state": to_state
        })
        super().__init__(
            message,
            workflow_id=workflow_id,
            current_state=from_state,
            error_code="WORKFLOW_STATE_TRANSITION_ERROR",
            context=context
        )


class WorkflowInitializationException(WorkflowException):
    """Exception raised during workflow initialization."""
    
    def __init__(
        self, 
        message: str,
        repository_url: str = None,
        initialization_step: str = None,
        **kwargs
    ):
        self.repository_url = repository_url
        self.initialization_step = initialization_step
        context = kwargs.get('context', {})
        context.update({
            "repository_url": repository_url,
            "initialization_step": initialization_step
        })
        super().__init__(
            message,
            current_state="initialization",
            error_code="WORKFLOW_INITIALIZATION_ERROR",
            context=context
        )


class WorkflowOrchestrationException(WorkflowException):
    """Exception raised during workflow orchestration."""
    
    def __init__(
        self, 
        message: str,
        orchestration_phase: str = None,
        failed_agents: List[str] = None,
        **kwargs
    ):
        self.orchestration_phase = orchestration_phase
        self.failed_agents = failed_agents or []
        context = kwargs.get('context', {})
        context.update({
            "orchestration_phase": orchestration_phase,
            "failed_agents": self.failed_agents
        })
        super().__init__(
            message,
            error_code="WORKFLOW_ORCHESTRATION_ERROR",
            context=context
        )


class WorkflowTimeoutException(WorkflowException):
    """Exception raised when workflow execution times out."""
    
    def __init__(
        self, 
        message: str,
        timeout_seconds: int = None,
        elapsed_seconds: float = None,
        **kwargs
    ):
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds
        context = kwargs.get('context', {})
        context.update({
            "timeout_seconds": timeout_seconds,
            "elapsed_seconds": elapsed_seconds
        })
        super().__init__(
            message,
            error_code="WORKFLOW_TIMEOUT",
            context=context
        )


class WorkflowConfigurationException(WorkflowException):
    """Exception raised due to workflow configuration issues."""
    
    def __init__(
        self, 
        message: str,
        config_section: str = None,
        missing_config: List[str] = None,
        **kwargs
    ):
        self.config_section = config_section
        self.missing_config = missing_config or []
        context = kwargs.get('context', {})
        context.update({
            "config_section": config_section,
            "missing_config": self.missing_config
        })
        super().__init__(
            message,
            error_code="WORKFLOW_CONFIGURATION_ERROR",
            context=context
        )


class WorkflowDependencyException(WorkflowException):
    """Exception raised when workflow dependencies are not met."""
    
    def __init__(
        self, 
        message: str,
        missing_dependencies: List[str] = None,
        dependency_type: str = None,
        **kwargs
    ):
        self.missing_dependencies = missing_dependencies or []
        self.dependency_type = dependency_type
        context = kwargs.get('context', {})
        context.update({
            "missing_dependencies": self.missing_dependencies,
            "dependency_type": dependency_type
        })
        super().__init__(
            message,
            error_code="WORKFLOW_DEPENDENCY_ERROR",
            context=context
        )


class WorkflowDataException(WorkflowException):
    """Exception raised due to workflow data issues."""
    
    def __init__(
        self, 
        message: str,
        data_type: str = None,
        validation_errors: List[str] = None,
        **kwargs
    ):
        self.data_type = data_type
        self.validation_errors = validation_errors or []
        context = kwargs.get('context', {})
        context.update({
            "data_type": data_type,
            "validation_errors": self.validation_errors
        })
        super().__init__(
            message,
            error_code="WORKFLOW_DATA_ERROR",
            context=context
        )


class WorkflowRecoveryException(WorkflowException):
    """Exception raised during workflow recovery attempts."""
    
    def __init__(
        self, 
        message: str,
        recovery_attempt: int = None,
        max_attempts: int = None,
        **kwargs
    ):
        self.recovery_attempt = recovery_attempt
        self.max_attempts = max_attempts
        context = kwargs.get('context', {})
        context.update({
            "recovery_attempt": recovery_attempt,
            "max_attempts": max_attempts
        })
        super().__init__(
            message,
            error_code="WORKFLOW_RECOVERY_ERROR",
            context=context
        )


def handle_workflow_exception(
    exception: WorkflowException,
    logger = None,
    workflow_state_repo = None,
    reraise: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Handle workflow exceptions with standardized logging and state updates.
    
    Args:
        exception: The workflow exception to handle
        logger: Logger instance for error logging
        workflow_state_repo: Repository for updating workflow state
        reraise: Whether to reraise the exception after handling
        
    Returns:
        Exception details as dictionary, if not reraised
    """
    error_details = exception.to_dict()
    
    if logger:
        logger.error(
            f"Workflow Exception: {exception.message}",
            extra={
                "workflow_id": exception.workflow_id,
                "current_state": exception.current_state,
                "error_code": exception.error_code,
                "context": exception.context
            }
        )
    
    # Update workflow state if repository provided
    if workflow_state_repo and exception.workflow_id:
        try:
            from config.database import get_db_session
            with get_db_session() as session:
                workflow = workflow_state_repo.get_by_workflow_id(session, exception.workflow_id)
                if workflow:
                    workflow.add_error(exception.message, exception.error_code or "workflow_error")
                    workflow.status = "failed"
                    session.commit()
        except Exception as e:
            if logger:
                logger.error(f"Failed to update workflow state: {e}")
    
    if reraise:
        raise exception
    
    return error_details


def create_workflow_exception(
    exception_type: str,
    message: str,
    **kwargs
) -> WorkflowException:
    """
    Factory function to create appropriate workflow exception based on type.
    
    Args:
        exception_type: Type of exception to create
        message: Error message
        **kwargs: Additional context and parameters
        
    Returns:
        Appropriate WorkflowException subclass instance
    """
    exception_map = {
        "state_transition": WorkflowStateException,
        "initialization": WorkflowInitializationException,
        "orchestration": WorkflowOrchestrationException,
        "timeout": WorkflowTimeoutException,
        "configuration": WorkflowConfigurationException,
        "dependency": WorkflowDependencyException,
        "data": WorkflowDataException,
        "recovery": WorkflowRecoveryException
    }
    
    exception_class = exception_map.get(exception_type, WorkflowException)
    return exception_class(message, **kwargs)