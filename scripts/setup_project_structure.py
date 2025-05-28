import os
import pathlib

def create_file(filepath, content=""):
    """Create a file with optional content if it doesn't exist."""
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created file: {filepath}")

def create_python_file(filepath):
    """Create a Python file with a basic docstring."""
    content = '"""Module for Agentic AI Workflow."""\n'
    create_file(filepath, content)

def create_init_file(filepath):
    """Create an __init__.py file."""
    create_file(filepath, "# __init__.py for Agentic AI Workflow\n")

def create_sql_file(filepath, migration_name):
    """Create an SQL migration file with a basic comment."""
    content = f"-- Migration: {migration_name}\n-- Add your migration SQL here\n"
    create_file(filepath, content)

def create_project_structure():
    """Create the folder structure for the Agentic AI Workflow project."""
    project_root = "agentic-ai-workflow"
    os.makedirs(project_root, exist_ok=True)

    # Root files
    create_file(f"{project_root}/README.md", "# Agentic AI Workflow\n\nA project for agentic AI code analysis and improvement.\n")
    create_file(f"{project_root}/requirements.txt", "# Python dependencies\n")
    create_file(f"{project_root}/setup.py", "# Setup script for the project\n")
    create_file(f"{project_root}/.env.example", "# Example environment variables\nOPENAI_API_KEY=\nGITHUB_MCP_TOKEN=\n")
    create_file(f"{project_root}/.gitignore", "# Python\n*.pyc\n__pycache__/\n\n# Environment\n.env\n\n# Data\ndata/database/*.db\n")
    create_file(f"{project_root}/pyproject.toml", "[project]\nname = \"agentic-ai-workflow\"\nversion = \"0.1.0\"\n")

    # config/
    config_files = [
        "__init__.py",
        "settings.py",
        "database.py",
        "api_config.py",
        "logging_config.py"
    ]
    for file in config_files:
        create_python_file(f"{project_root}/config/{file}" if file != "__init__.py" else f"{project_root}/config/{file}")

    # src/
    create_init_file(f"{project_root}/src/__init__.py")

    # src/agents/
    create_init_file(f"{project_root}/src/agents/__init__.py")
    create_python_file(f"{project_root}/src/agents/base_agent.py")
    # src/agents/developer_agent/
    create_init_file(f"{project_root}/src/agents/developer_agent/__init__.py")
    for file in ["developer_agent.py", "improvement_engine.py", "context_manager.py", "suggestion_generator.py"]:
        create_python_file(f"{project_root}/src/agents/developer_agent/{file}")
    # src/agents/tester_agent/
    create_init_file(f"{project_root}/src/agents/tester_agent/__init__.py")
    for file in ["tester_agent.py", "suggestion_evaluator.py", "feedback_generator.py"]:
        create_python_file(f"{project_root}/src/agents/tester_agent/{file}")
    # src/agents/researcher_agent/
    create_init_file(f"{project_root}/src/agents/researcher_agent/__init__.py")
    create_python_file(f"{project_root}/src/agents/researcher_agent/researcher_agent.py")

    # src/workflow/
    create_init_file(f"{project_root}/src/workflow/__init__.py")
    for file in ["workflow_manager.py", "state_machine.py", "decision_engine.py", "orchestrator.py"]:
        create_python_file(f"{project_root}/src/workflow/{file}")

    # src/integrations/
    create_init_file(f"{project_root}/src/integrations/__init__.py")
    # src/integrations/github_mcp/
    create_init_file(f"{project_root}/src/integrations/github_mcp/__init__.py")
    for file in ["mcp_client.py", "repository_manager.py", "pull_request_manager.py", "branch_manager.py"]:
        create_python_file(f"{project_root}/src/integrations/github_mcp/{file}")
    # src/integrations/gpt4o/
    create_init_file(f"{project_root}/src/integrations/gpt4o/__init__.py")
    for file in ["api_client.py", "prompt_templates.py", "response_parser.py", "rate_limiter.py"]:
        create_python_file(f"{project_root}/src/integrations/gpt4o/{file}")
    # src/integrations/adk/
    create_init_file(f"{project_root}/src/integrations/adk/__init__.py")
    for file in ["adk_wrapper.py", "agent_factory.py"]:
        create_python_file(f"{project_root}/src/integrations/adk/{file}")

    # src/core/
    create_init_file(f"{project_root}/src/core/__init__.py")
    # src/core/database/
    create_init_file(f"{project_root}/src/core/database/__init__.py")
    for file in ["models.py", "repositories.py", "connection.py"]:
        create_python_file(f"{project_root}/src/core/database/{file}")
    # src/core/database/migrations/
    create_init_file(f"{project_root}/src/core/database/migrations/__init__.py")
    create_sql_file(f"{project_root}/src/core/database/migrations/001_initial_schema.sql", "Initial schema")
    create_sql_file(f"{project_root}/src/core/database/migrations/002_add_workflow_tables.sql", "Workflow tables")
    # src/core/utils/
    create_init_file(f"{project_root}/src/core/utils/__init__.py")
    for file in ["file_utils.py", "string_utils.py", "validation.py", "encryption.py"]:
        create_python_file(f"{project_root}/src/core/utils/{file}")
    # src/core/exceptions/
    create_init_file(f"{project_root}/src/core/exceptions/__init__.py")
    for file in ["agent_exceptions.py", "workflow_exceptions.py", "integration_exceptions.py"]:
        create_python_file(f"{project_root}/src/core/exceptions/{file}")

    # src/tools/
    create_init_file(f"{project_root}/src/tools/__init__.py")
    # src/tools/code_analysis/
    create_init_file(f"{project_root}/src/tools/code_analysis/__init__.py")
    for file in ["ast_parser.py", "language_detector.py", "pattern_matcher.py", "quality_analyzer.py", "dependency_analyzer.py"]:
        create_python_file(f"{project_root}/src/tools/code_analysis/{file}")
    # src/tools/github_tools/
    create_init_file(f"{project_root}/src/tools/github_tools/__init__.py")
    for file in ["repo_fetcher.py", "file_reader.py", "pr_creator.py"]:
        create_python_file(f"{project_root}/src/tools/github_tools/{file}")
    # src/tools/text_processing/
    create_init_file(f"{project_root}/src/tools/text_processing/__init__.py")
    for file in ["diff_generator.py", "formatter.py"]:
        create_python_file(f"{project_root}/src/tools/text_processing/{file}")
    # src/tools/database_tools/
    create_init_file(f"{project_root}/src/tools/database_tools/__init__.py")
    for file in ["query_builder.py", "data_validator.py"]:
        create_python_file(f"{project_root}/src/tools/database_tools/{file}")

    # src/terminal/
    create_init_file(f"{project_root}/src/terminal/__init__.py")
    for file in ["cli_interface.py", "prompt_handler.py", "output_formatter.py", "command_parser.py"]:
        create_python_file(f"{project_root}/src/terminal/{file}")

    # src/services/
    create_init_file(f"{project_root}/src/services/__init__.py")
    for file in ["suggestion_service.py", "workflow_service.py", "repository_service.py", "notification_service.py"]:
        create_python_file(f"{project_root}/src/services/{file}")

    # tests/
    create_init_file(f"{project_root}/tests/__init__.py")
    create_python_file(f"{project_root}/tests/conftest.py")
    # tests/unit/
    create_init_file(f"{project_root}/tests/unit/__init__.py")
    # tests/unit/test_agents/
    create_init_file(f"{project_root}/tests/unit/test_agents/__init__.py")
    for file in ["test_developer_agent.py", "test_tester_agent.py"]:
        create_python_file(f"{project_root}/tests/unit/test_agents/{file}")
    # tests/unit/test_workflow/
    create_init_file(f"{project_root}/tests/unit/test_workflow/__init__.py")
    for file in ["test_workflow_manager.py", "test_state_machine.py"]:
        create_python_file(f"{project_root}/tests/unit/test_workflow/{file}")
    # tests/unit/test_integrations/
    create_init_file(f"{project_root}/tests/unit/test_integrations/__init__.py")
    for file in ["test_github_mcp.py", "test_gpt4o.py"]:
        create_python_file(f"{project_root}/tests/unit/test_integrations/{file}")
    # tests/unit/test_core/
    create_init_file(f"{project_root}/tests/unit/test_core/__init__.py")
    for file in ["test_database.py", "test_code_analysis.py"]:
        create_python_file(f"{project_root}/tests/unit/test_core/{file}")
    # tests/unit/test_tools/
    create_init_file(f"{project_root}/tests/unit/test_tools/__init__.py")
    for file in ["test_code_analysis.py", "test_github_tools.py", "test_text_processing.py", "test_database_tools.py"]:
        create_python_file(f"{project_root}/tests/unit/test_tools/{file}")
    # tests/integration/
    create_init_file(f"{project_root}/tests/integration/__init__.py")
    for file in ["test_end_to_end.py", "test_agent_communication.py", "test_workflow_execution.py"]:
        create_python_file(f"{project_root}/tests/integration/{file}")
    # tests/fixtures/
    create_init_file(f"{project_root}/tests/fixtures/__init__.py")
    create_file(f"{project_root}/tests/fixtures/test_data.json", "{}")
    os.makedirs(f"{project_root}/tests/fixtures/sample_repositories", exist_ok=True)
    os.makedirs(f"{project_root}/tests/fixtures/mock_responses", exist_ok=True)

    # scripts/
    for file in ["setup_environment.py", "run_migrations.py", "test_connections.py", "deploy.py"]:
        create_python_file(f"{project_root}/scripts/{file}")

    # docs/
    doc_files = [
        "README.md",
        "installation.md",
        "configuration.md",
        "api_reference.md",
        "workflow_guide.md",
        "troubleshooting.md"
    ]
    for file in doc_files:
        create_file(f"{project_root}/docs/{file}", f"# {file.replace('.md', '').title().replace('_', ' ')}\n")

    # data/
    os.makedirs(f"{project_root}/data/database", exist_ok=True)
    os.makedirs(f"{project_root}/data/logs", exist_ok=True)
    os.makedirs(f"{project_root}/data/temp/repositories", exist_ok=True)
    # Note: Not creating agentic_workflow.db to avoid empty database initialization
    for file in ["application.log", "workflow.log", "error.log"]:
        create_file(f"{project_root}/data/logs/{file}", "")

    # deployment/
    # deployment/docker/
    create_file(f"{project_root}/deployment/docker/Dockerfile", "# Dockerfile for Agentic AI Workflow\n")
    create_file(f"{project_root}/deployment/docker/docker-compose.yml", "# Docker Compose configuration\n")
    # deployment/kubernetes/
    create_file(f"{project_root}/deployment/kubernetes/deployment.yaml", "# Kubernetes deployment\n")
    create_file(f"{project_root}/deployment/kubernetes/service.yaml", "# Kubernetes service\n")
    # deployment/terraform/
    create_file(f"{project_root}/deployment/terraform/main.tf", "# Terraform configuration\n")
    create_file(f"{project_root}/deployment/terraform/variables.tf", "# Terraform variables\n")

    # main.py
    create_python_file(f"{project_root}/main.py")

    print(f"Project structure created at {project_root}/")

if __name__ == "__main__":
    create_project_structure()