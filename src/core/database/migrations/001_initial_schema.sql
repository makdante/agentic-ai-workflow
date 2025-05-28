/*src/core/database/migrations/001_initial_schema.sql*/
-- Initial database schema for Agentic AI Workflow
-- Creates tables for repositories, code analysis, suggestions, and workflow states

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url VARCHAR(500) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    owner VARCHAR(100) NOT NULL,
    branch VARCHAR(50) DEFAULT 'main',
    local_path VARCHAR(500),
    clone_status VARCHAR(20) DEFAULT 'pending',
    description TEXT,
    language VARCHAR(50),
    size_kb INTEGER,
    file_count INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_analyzed DATETIME
);

-- Create indexes for repositories
CREATE INDEX IF NOT EXISTS idx_repositories_url ON repositories(url);
CREATE INDEX IF NOT EXISTS idx_repositories_owner_name ON repositories(owner, name);
CREATE INDEX IF NOT EXISTS idx_repositories_last_analyzed ON repositories(last_analyzed);

-- Code analyses table
CREATE TABLE IF NOT EXISTS code_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    language VARCHAR(50),
    lines_of_code INTEGER,
    complexity_score REAL,
    quality_score REAL,
    functions TEXT, -- JSON string
    classes TEXT,   -- JSON string
    imports TEXT,   -- JSON string
    comments TEXT,  -- JSON string
    summary TEXT,
    issues_found TEXT,   -- JSON string
    dependencies TEXT,   -- JSON string
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);

-- Create indexes for code analyses
CREATE INDEX IF NOT EXISTS idx_code_analyses_repository_id ON code_analyses(repository_id);
CREATE INDEX IF NOT EXISTS idx_code_analyses_file_path ON code_analyses(file_path);
CREATE INDEX IF NOT EXISTS idx_code_analyses_status ON code_analyses(status);
CREATE INDEX IF NOT EXISTS idx_code_analyses_language ON code_analyses(language);

-- Suggestions table
CREATE TABLE IF NOT EXISTS suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'generated',
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    original_code TEXT,
    suggested_code TEXT,
    line_start INTEGER,
    line_end INTEGER,
    confidence_score REAL,
    impact_score REAL,
    agent_name VARCHAR(50),
    test_results TEXT, -- JSON string
    feedback TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    FOREIGN KEY (analysis_id) REFERENCES code_analyses(id) ON DELETE CASCADE
);

-- Create indexes for suggestions
CREATE INDEX IF NOT EXISTS idx_suggestions_analysis_id ON suggestions(analysis_id);
CREATE INDEX IF NOT EXISTS idx_suggestions_type ON suggestions(type);
CREATE INDEX IF NOT EXISTS idx_suggestions_status ON suggestions(status);
CREATE INDEX IF NOT EXISTS idx_suggestions_confidence_score ON suggestions(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_suggestions_created_at ON suggestions(created_at DESC);

-- Workflow states table
CREATE TABLE IF NOT EXISTS workflow_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    workflow_id VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(20) DEFAULT 'initialized',
    current_agent VARCHAR(50),
    current_step VARCHAR(100),
    progress_percentage REAL DEFAULT 0.0,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    execution_time_seconds REAL,
    total_files_analyzed INTEGER DEFAULT 0,
    total_suggestions INTEGER DEFAULT 0,
    approved_suggestions INTEGER DEFAULT 0,
    agent_config TEXT, -- JSON string
    context_data TEXT, -- JSON string
    error_log TEXT,    -- JSON string
    branch_name VARCHAR(100),
    pull_request_url VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id) ON DELETE CASCADE
);

-- Create indexes for workflow states
CREATE INDEX IF NOT EXISTS idx_workflow_states_repository_id ON workflow_states(repository_id);
CREATE INDEX IF NOT EXISTS idx_workflow_states_workflow_id ON workflow_states(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_states_status ON workflow_states(status);
CREATE INDEX IF NOT EXISTS idx_workflow_states_created_at ON workflow_states(created_at DESC);

-- Create triggers for updating updated_at timestamps
CREATE TRIGGER IF NOT EXISTS update_repositories_timestamp 
    AFTER UPDATE ON repositories
    FOR EACH ROW
    BEGIN
        UPDATE repositories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_code_analyses_timestamp 
    AFTER UPDATE ON code_analyses
    FOR EACH ROW
    BEGIN
        UPDATE code_analyses SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_suggestions_timestamp 
    AFTER UPDATE ON suggestions
    FOR EACH ROW
    BEGIN
        UPDATE suggestions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_workflow_states_timestamp 
    AFTER UPDATE ON workflow_states
    FOR EACH ROW
    BEGIN
        UPDATE workflow_states SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;