#src/core/exceptions/agent_exceptions.py
"""
Agent-specific exceptions for the Agentic AI Workflow.
Defines custom exceptions for different agent operations and error scenarios.
"""

from typing import Optional, Dict, Any


class AgentException(Exception):
    """Base exception for all agent-related errors."""
    
    def __init__(
        self, 
        message: str, 
        agent_name: str = None,
        error_code: str = None,
        context: Dict[str, Any] = None
    ):
        self.message = message
        self.agent_name = agent_name
        self.error_code = error_code
        self.context = context or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "exception_type": self.__class__.__name__,
            "message": self.message,
            "agent_name": self.agent_name,
            "error_code": self.error_code,
            "context": self.context
        }


class DeveloperAgentException(AgentException):
    """Exceptions specific to Developer Agent operations."""
    pass


class TesterAgentException(AgentException):
    """Exceptions specific to Tester Agent operations."""
    pass


class ResearcherAgentException(AgentException):
    """Exceptions specific to Researcher Agent operations."""
    pass


class CodeAnalysisException(DeveloperAgentException):
    """Exception raised during code analysis operations."""
    
    def __init__(
        self, 
        message: str, 
        file_path: str = None,
        analysis_type: str = None,
        **kwargs
    ):
        self.file_path = file_path
        self.analysis_type = analysis_type
        context = kwargs.get('context', {})
        context.update({
            "file_path": file_path,
            "analysis_type": analysis_type
        })
        super().__init__(
            message, 
            agent_name="developer_agent",
            error_code="CODE_ANALYSIS_ERROR",
            context=context
        )


class SuggestionGenerationException(DeveloperAgentException):
    """Exception raised during suggestion generation."""
    
    def __init__(
        self, 
        message: str, 
        suggestion_type: str = None,
        file_path: str = None,
        **kwargs
    ):
        self.suggestion_type = suggestion_type
        self.file_path = file_path
        context = kwargs.get('context', {})
        context.update({
            "suggestion_type": suggestion_type,
            "file_path": file_path
        })
        super().__init__(
            message,
            agent_name="developer_agent",
            error_code="SUGGESTION_GENERATION_ERROR",
            context=context
        )


class ContextWindowException(AgentException):
    """Exception raised when context window limits are exceeded."""
    
    def __init__(
        self, 
        message: str, 
        current_size: int = None,
        max_size: int = None,
        **kwargs
    ):
        self.current_size = current_size
        self.max_size = max_size
        context = kwargs.get('context', {})
        context.update({
            "current_size": current_size,
            "max_size": max_size
        })
        super().__init__(
            message,
            error_code="CONTEXT_WINDOW_EXCEEDED",
            context=context
        )


class AgentCommunicationException(AgentException):
    """Exception raised during agent-to-agent communication."""
    
    def __init__(
        self, 
        message: str, 
        from_agent: str = None,
        to_agent: str = None,
        communication_type: str = None,
        **kwargs
    ):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.communication_type = communication_type
        context = kwargs.get('context', {})
        context.update({
            "from_agent": from_agent,
            "to_agent": to_agent,
            "communication_type": communication_type
        })
        super().__init__(
            message,
            error_code="AGENT_COMMUNICATION_ERROR",
            context=context
        )


class AgentTimeoutException(AgentException):
    """Exception raised when agent operations timeout."""
    
    def __init__(
        self, 
        message: str, 
        timeout_seconds: int = None,
        operation: str = None,
        **kwargs
    ):
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        context = kwargs.get('context', {})
        context.update({
            "timeout_seconds": timeout_seconds,
            "operation": operation
        })
        super().__init__(
            message,
            error_code="AGENT_TIMEOUT",
            context=context
        )


class AgentConfigurationException(AgentException):
    """Exception raised due to agent configuration issues."""
    
    def __init__(
        self, 
        message: str, 
        config_key: str = None,
        config_value: Any = None,
        **kwargs
    ):
        self.config_key = config_key
        self.config_value = config_value
        context = kwargs.get('context', {})
        context.update({
            "config_key": config_key,
            "config_value": str(config_value) if config_value is not None else None
        })
        super().__init__(
            message,
            error_code="AGENT_CONFIGURATION_ERROR",
            context=context
        )


class AgentResourceException(AgentException):
    """Exception raised due to resource constraints."""
    
    def __init__(
        self, 
        message: str, 
        resource_type: str = None,
        current_usage: float = None,
        limit: float = None,
        **kwargs
    ):
        self.resource_type = resource_type
        self.current_usage = current_usage
        self.limit = limit
        context = kwargs.get('context', {})
        context.update({
            "resource_type": resource_type,
            "current_usage": current_usage,
            "limit": limit
        })
        super().__init__(
            message,
            error_code="AGENT_RESOURCE_ERROR",
            context=context
        )


class SuggestionEvaluationException(TesterAgentException):
    """Exception raised during suggestion evaluation by Tester Agent."""
    
    def __init__(
        self, 
        message: str, 
        suggestion_id: int = None,
        evaluation_type: str = None,
        **kwargs
    ):
        self.suggestion_id = suggestion_id
        self.evaluation_type = evaluation_type
        context = kwargs.get('context', {})
        context.update({
            "suggestion_id": suggestion_id,
            "evaluation_type": evaluation_type
        })
        super().__init__(
            message,
            agent_name="tester_agent",
            error_code="SUGGESTION_EVALUATION_ERROR",
            context=context
        )


class FeedbackGenerationException(TesterAgentException):
    """Exception raised during feedback generation."""
    
    def __init__(
        self, 
        message: str, 
        feedback_type: str = None,
        target_suggestion: int = None,
        **kwargs
    ):
        self.feedback_type = feedback_type
        self.target_suggestion = target_suggestion
        context = kwargs.get('context', {})
        context.update({
            "feedback_type": feedback_type,
            "target_suggestion": target_suggestion
        })
        super().__init__(
            message,
            agent_name="tester_agent",
            error_code="FEEDBACK_GENERATION_ERROR",
            context=context
        )


def handle_agent_exception(
    exception: AgentException, 
    logger = None,
    reraise: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Handle agent exceptions with standardized logging and error reporting.
    
    Args:
        exception: The agent exception to handle
        logger: Logger instance for error logging
        reraise: Whether to reraise the exception after handling
        
    Returns:
        Exception details as dictionary, if not reraised
    """
    error_details = exception.to_dict()
    
    if logger:
        logger.error(
            f"Agent Exception: {exception.message}",
            extra={
                "agent_name": exception.agent_name,
                "error_code": exception.error_code,
                "context": exception.context
            }
        )
    
    if reraise:
        raise exception
    
    return error_details


def create_agent_exception(
    exception_type: str,
    message: str,
    **kwargs
) -> AgentException:
    """
    Factory function to create appropriate agent exception based on type.
    
    Args:
        exception_type: Type of exception to create
        message: Error message
        **kwargs: Additional context and parameters
        
    Returns:
        Appropriate AgentException subclass instance
    """
    exception_map = {
        "code_analysis": CodeAnalysisException,
        "suggestion_generation": SuggestionGenerationException,
        "context_window": ContextWindowException,
        "agent_communication": AgentCommunicationException,
        "agent_timeout": AgentTimeoutException,
        "agent_configuration": AgentConfigurationException,
        "agent_resource": AgentResourceException,
        "suggestion_evaluation": SuggestionEvaluationException,
        "feedback_generation": FeedbackGenerationException,
        "developer_agent": DeveloperAgentException,
        "tester_agent": TesterAgentException,
        "researcher_agent": ResearcherAgentException
    }
    
    exception_class = exception_map.get(exception_type, AgentException)
    return exception_class(message, **kwargs)