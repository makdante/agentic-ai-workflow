/*src/core/database/migrations/002_add_workflow_tables.sql*/
-- Additional workflow-specific tables and enhancements
-- Adds agent communication logs, context management, and performance metrics

-- Agent interaction logs table
CREATE TABLE IF NOT EXISTS agent_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id VARCHAR(50) NOT NULL,
    from_agent VARCHAR(50),
    to_agent VARCHAR(50),
    interaction_type VARCHAR(50) NOT NULL, -- 'handoff', 'feedback', 'query', 'result'
    message_content TEXT,
    metadata TEXT, -- JSON string for additional data
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflow_states(workflow_id) ON DELETE CASCADE
);

-- Context snapshots table for maintaining agent context
CREATE TABLE IF NOT EXISTS context_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id VARCHAR(50) NOT NULL,
    agent_name VARCHAR(50) NOT NULL,
    context_type VARCHAR(50) NOT NULL, -- 'code_analysis', 'suggestions', 'repository_state'
    context_data TEXT NOT NULL, -- JSON string
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflow_states(workflow_id) ON DELETE CASCADE
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id VARCHAR(50) NOT NULL,
    agent_name VARCHAR(50),
    operation_name VARCHAR(100) NOT NULL,
    execution_time_ms INTEGER,
    memory_usage_mb REAL,
    api_calls_count INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflow_states(workflow_id) ON DELETE CASCADE
);

-- Code quality metrics table
CREATE TABLE IF NOT EXISTS quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value REAL NOT NULL,
    metric_category VARCHAR(50), -- 'complexity', 'maintainability', 'security', 'performance'
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES code_analyses(id) ON DELETE CASCADE
);

-- Suggestion voting/scoring table for future ML improvements
CREATE TABLE IF NOT EXISTS suggestion_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    suggestion_id INTEGER NOT NULL,
    feedback_type VARCHAR(20) NOT NULL, -- 'accept', 'reject', 'modify'
    feedback_source VARCHAR(50) DEFAULT 'tester_agent',
    score REAL, -- 0.0 to 1.0
    reasoning TEXT,
    metadata TEXT, -- JSON string for additional feedback data
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (suggestion_id) REFERENCES suggestions(id) ON DELETE CASCADE
);

-- Create indexes for new tables
CREATE INDEX IF NOT EXISTS idx_agent_interactions_workflow_id ON agent_interactions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_timestamp ON agent_interactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_type ON agent_interactions(interaction_type);

CREATE INDEX IF NOT EXISTS idx_context_snapshots_workflow_id ON context_snapshots(workflow_id);
CREATE INDEX IF NOT EXISTS idx_context_snapshots_agent ON context_snapshots(agent_name);
CREATE INDEX IF NOT EXISTS idx_context_snapshots_type ON context_snapshots(context_type);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_workflow_id ON performance_metrics(workflow_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_agent ON performance_metrics(agent_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_operation ON performance_metrics(operation_name);

CREATE INDEX IF NOT EXISTS idx_quality_metrics_analysis_id ON quality_metrics(analysis_id);
CREATE INDEX IF NOT EXISTS idx_quality_metrics_category ON quality_metrics(metric_category);

CREATE INDEX IF NOT EXISTS idx_suggestion_feedback_suggestion_id ON suggestion_feedback(suggestion_id);
CREATE INDEX IF NOT EXISTS idx_suggestion_feedback_type ON suggestion_feedback(feedback_type);

-- Add new columns to existing tables for enhanced functionality
ALTER TABLE repositories ADD COLUMN complexity_summary TEXT; -- JSON summary of repository complexity
ALTER TABLE repositories ADD COLUMN dependencies_summary TEXT; -- JSON summary of dependencies

ALTER TABLE code_analyses ADD COLUMN security_issues TEXT; -- JSON array of security concerns
ALTER TABLE code_analyses ADD COLUMN performance_issues TEXT; -- JSON array of performance issues

ALTER TABLE suggestions ADD COLUMN implementation_difficulty VARCHAR(20) DEFAULT 'medium'; -- 'easy', 'medium', 'hard'
ALTER TABLE suggestions ADD COLUMN estimated_time_minutes INTEGER; -- Estimated implementation time

-- Create views for common queries
CREATE VIEW IF NOT EXISTS repository_summary AS
SELECT 
    r.id,
    r.name,
    r.owner,
    r.url,
    r.language,
    COUNT(DISTINCT ca.id) as total_files_analyzed,
    COUNT(DISTINCT s.id) as total_suggestions,
    AVG(ca.complexity_score) as avg_complexity,
    AVG(ca.quality_score) as avg_quality,
    MAX(r.last_analyzed) as last_analysis_date
FROM repositories r
LEFT JOIN code_analyses ca ON r.id = ca.repository_id
LEFT JOIN suggestions s ON ca.id = s.analysis_id
GROUP BY r.id, r.name, r.owner, r.url, r.language;

CREATE VIEW IF NOT EXISTS workflow_summary AS
SELECT 
    ws.workflow_id,
    ws.status,
    ws.current_agent,
    ws.progress_percentage,
    r.name as repository_name,
    r.owner as repository_owner,
    ws.total_suggestions,
    ws.approved_suggestions,
    ws.start_time,
    ws.execution_time_seconds,
    CASE 
        WHEN ws.status = 'completed' THEN 'success'
        WHEN ws.status = 'failed' THEN 'failed'
        ELSE 'running'
    END as execution_status
FROM workflow_states ws
JOIN repositories r ON ws.repository_id = r.id;

CREATE VIEW IF NOT EXISTS suggestion_summary AS
SELECT 
    s.id,
    s.type,
    s.status,
    s.confidence_score,
    s.impact_score,
    ca.file_path,
    r.name as repository_name,
    r.owner as repository_owner,
    s.created_at
FROM suggestions s
JOIN code_analyses ca ON s.analysis_id = ca.id
JOIN repositories r ON ca.repository_id = r.id;
