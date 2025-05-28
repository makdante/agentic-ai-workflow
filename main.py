#main.py
"""
Main entry point for the Agentic AI Workflow application.
Handles application initialization, CLI interface, and workflow execution.
"""

import sys
import argparse
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config.settings import get_settings
from config.database import init_database, check_database_connection
from config.api_config import api_config
from config.logging_config import get_logger, log_workflow_state

logger = get_logger(__name__)


def validate_environment() -> bool:
    """
    Validate that all required environment variables and dependencies are configured.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    logger.info("Validating environment configuration...")
    
    # Check database connection
    if not check_database_connection():
        logger.error("Database connection failed")
        return False
    
    # Validate API configurations
    validations = api_config.validate_configurations()
    
    failed_validations = [service for service, valid in validations.items() if not valid]
    if failed_validations:
        logger.error(f"Failed API validations: {failed_validations}")
        return False
    
    logger.info("Environment validation successful")
    return True


def initialize_application() -> bool:
    """
    Initialize the application with database setup and configuration validation.
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        logger.info("Initializing Agentic AI Workflow application...")
        
        # Initialize database
        init_database()
        logger.info("Database initialization completed")
        
        # Validate environment
        if not validate_environment():
            logger.error("Environment validation failed")
            return False
        
        logger.info("Application initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        return False


def create_arg_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Agentic AI Workflow - Multi-agent code analysis and improvement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --url https://github.com/user/repo
  python main.py --url https://github.com/user/repo --branch develop
  python main.py --interactive
  python main.py --validate-env
        """
    )
    
    # Primary workflow arguments
    parser.add_argument(
        "--url", "-u",
        type=str,
        help="GitHub repository URL to analyze"
    )
    
    parser.add_argument(
        "--branch", "-b",
        type=str,
        default="main",
        help="Repository branch to analyze (default: main)"
    )
    
    # Application modes
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start interactive terminal interface"
    )
    
    parser.add_argument(
        "--validate-env",
        action="store_true",
        help="Validate environment configuration and exit"
    )
    
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize database and exit"
    )
    
    # Configuration options
    parser.add_argument(
        "--config-check",
        action="store_true",
        help="Check configuration and display current settings"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    return parser


def run_workflow(repository_url: str, branch: str = "main") -> bool:
    """
    Run the main workflow for a repository.
    
    Args:
        repository_url: GitHub repository URL
        branch: Repository branch to analyze
        
    Returns:
        bool: True if workflow completed successfully
    """
    try:
        logger.info(f"Starting workflow for repository: {repository_url}")
        log_workflow_state("new_workflow", "initialized", 
                          repository_url=repository_url, branch=branch)
        
        # Import workflow manager here to avoid circular imports
        from src.workflow.workflow_manager import WorkflowManager
        
        # Create and execute workflow
        workflow_manager = WorkflowManager()
        success = workflow_manager.execute_workflow(repository_url, branch)
        
        if success:
            logger.info("Workflow completed successfully")
            log_workflow_state("new_workflow", "completed")
        else:
            logger.error("Workflow failed")
            log_workflow_state("new_workflow", "failed")
        
        return success
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        log_workflow_state("new_workflow", "failed", error=str(e))
        return False


def run_interactive_mode() -> None:
    """Run the application in interactive terminal mode."""
    try:
        logger.info("Starting interactive mode...")
        
        # Import terminal interface here to avoid circular imports
        from src.terminal.cli_interface import CLIInterface
        
        # Create and run CLI interface
        cli = CLIInterface()
        cli.run()
        
    except KeyboardInterrupt:
        logger.info("Interactive mode interrupted by user")
    except Exception as e:
        logger.error(f"Interactive mode failed: {e}")


def display_config_info() -> None:
    """Display current configuration information."""
    settings = get_settings()
    validations = api_config.validate_configurations()
    
    print("\n=== Agentic AI Workflow Configuration ===")
    print(f"App Name: {settings.app_name}")
    print(f"Version: {settings.app_version}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Log Level: {settings.log_level}")
    print(f"Database URL: {settings.database_url}")
    print()
    
    print("=== API Configuration Status ===")
    for service, is_valid in validations.items():
        status = "✓ Configured" if is_valid else "✗ Missing/Invalid"
        print(f"{service.replace('_', ' ').title()}: {status}")
    print()
    
    print("=== Repository Processing Settings ===")
    print(f"Temp Path: {settings.temp_repo_path}")
    print(f"Max Repo Size: {settings.max_repo_size_mb} MB")
    print(f"Clone Timeout: {settings.clone_timeout_seconds} seconds")
    print(f"Max Context Length: {settings.max_context_length}")
    print(f"Max Files per Analysis: {settings.max_files_per_analysis}")
    print()


def main() -> int:
    """
    Main application entry point.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = create_arg_parser()
    args = parser.parse_args()
    
    # Handle special modes first
    if args.validate_env:
        success = validate_environment()
        return 0 if success else 1
    
    if args.init_db:
        try:
            init_database()
            print("Database initialized successfully")
            return 0
        except Exception as e:
            print(f"Database initialization failed: {e}")
            return 1
    
    if args.config_check:
        display_config_info()
        return 0
    
    # Initialize application
    if not initialize_application():
        logger.error("Failed to initialize application")
        return 1
    
    try:
        # Determine execution mode
        if args.interactive:
            run_interactive_mode()
            return 0
        
        elif args.url:
            success = run_workflow(args.url, args.branch)
            return 0 if success else 1
        
        else:
            # No specific mode selected, show help and start interactive mode
            parser.print_help()
            print("\nNo repository URL provided. Starting interactive mode...\n")
            run_interactive_mode()
            return 0
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application failed with unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)