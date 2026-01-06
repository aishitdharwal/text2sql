-- =====================================================
-- FEEDBACK SYSTEM SCHEMA
-- Create this table in each database (sales_db, marketing_db, operations_db)
-- =====================================================

CREATE TABLE IF NOT EXISTS query_feedback (
    feedback_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    team_name VARCHAR(50) NOT NULL,
    natural_language_query TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    rating VARCHAR(10) NOT NULL CHECK (rating IN ('thumbs_up', 'thumbs_down')),
    feedback_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE query_feedback IS 'User feedback on generated SQL queries';
COMMENT ON COLUMN query_feedback.session_id IS 'Session ID of the user who provided feedback';
COMMENT ON COLUMN query_feedback.team_name IS 'Team name (sales, marketing, operations)';
COMMENT ON COLUMN query_feedback.natural_language_query IS 'Original natural language query';
COMMENT ON COLUMN query_feedback.generated_sql IS 'SQL query that was generated';
COMMENT ON COLUMN query_feedback.rating IS 'User rating: thumbs_up or thumbs_down';
COMMENT ON COLUMN query_feedback.feedback_comment IS 'Optional comment for thumbs_down ratings';

-- Create index for faster queries
CREATE INDEX idx_feedback_team ON query_feedback(team_name);
CREATE INDEX idx_feedback_rating ON query_feedback(rating);
CREATE INDEX idx_feedback_created_at ON query_feedback(created_at);
