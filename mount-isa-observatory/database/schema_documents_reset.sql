-- ============================================================================
-- RESET AND CREATE DOCUMENTS TABLE
-- ============================================================================
-- This will drop the old documents table and create it fresh
-- Run this if you're getting column errors
-- ============================================================================

-- Drop old table if exists (WARNING: This deletes all existing data!)
DROP TABLE IF EXISTS documents CASCADE;

-- Main documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic metadata
    url TEXT UNIQUE NOT NULL,
    statement_id TEXT,
    title TEXT NOT NULL,
    published_date DATE NOT NULL,
    scraped_date TIMESTAMP DEFAULT NOW(),

    -- Source info
    source_type VARCHAR(50) DEFAULT 'media_statement',
    source_organization VARCHAR(200) DEFAULT 'Queensland Government',
    minister_name TEXT,
    portfolio TEXT,

    -- Content
    full_text TEXT NOT NULL,
    markdown_text TEXT,
    summary TEXT,

    -- Extracted entities
    funding_amount_extracted NUMERIC,
    funding_amounts_all JSONB,
    programs_mentioned TEXT[],
    locations_mentioned TEXT[],
    organizations_mentioned TEXT[],
    people_mentioned JSONB,

    -- AI analysis (for future use)
    ai_analysis_status VARCHAR(50) DEFAULT 'pending',
    embedding_status VARCHAR(50) DEFAULT 'pending',

    -- Search and classification
    keywords TEXT[],
    categories TEXT[],

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT 'system'
);

-- Indexes for performance
CREATE INDEX idx_documents_published_date ON documents(published_date DESC);
CREATE INDEX idx_documents_source_type ON documents(source_type);
CREATE INDEX idx_documents_programs ON documents USING GIN(programs_mentioned);
CREATE INDEX idx_documents_locations ON documents USING GIN(locations_mentioned);
CREATE INDEX idx_documents_keywords ON documents USING GIN(keywords);
CREATE INDEX idx_documents_categories ON documents USING GIN(categories);

-- Useful views
CREATE OR REPLACE VIEW v_funding_summary AS
SELECT
    COUNT(*) as total_documents,
    COUNT(*) FILTER (WHERE published_date >= '2025-01-01') as docs_2025,
    COUNT(*) FILTER (WHERE published_date >= '2024-01-01' AND published_date < '2025-01-01') as docs_2024,
    SUM(funding_amount_extracted) / 1000 as total_funding_billions,
    AVG(funding_amount_extracted) as avg_funding_millions,
    MIN(published_date) as earliest_date,
    MAX(published_date) as latest_date
FROM documents;

CREATE OR REPLACE VIEW v_funding_by_location AS
SELECT
    UNNEST(locations_mentioned) as location,
    COUNT(*) as announcements,
    SUM(funding_amount_extracted) as total_funding_m,
    AVG(funding_amount_extracted) as avg_funding_m,
    MIN(published_date) as first_announcement,
    MAX(published_date) as latest_announcement
FROM documents
WHERE funding_amount_extracted > 0
GROUP BY location
ORDER BY total_funding_m DESC;

CREATE OR REPLACE VIEW v_funding_by_program AS
SELECT
    UNNEST(programs_mentioned) as program,
    COUNT(*) as mentions,
    SUM(funding_amount_extracted) as total_funding_m,
    AVG(funding_amount_extracted) as avg_funding_m
FROM documents
WHERE funding_amount_extracted > 0
GROUP BY program
ORDER BY total_funding_m DESC;

CREATE OR REPLACE VIEW v_funding_by_year AS
SELECT
    EXTRACT(YEAR FROM published_date)::INTEGER as year,
    COUNT(*) as documents,
    SUM(funding_amount_extracted) as total_funding_m,
    AVG(funding_amount_extracted) as avg_funding_m
FROM documents
GROUP BY year
ORDER BY year DESC;

CREATE OR REPLACE VIEW v_recent_announcements AS
SELECT
    published_date,
    title,
    funding_amount_extracted as funding_m,
    programs_mentioned,
    locations_mentioned,
    url
FROM documents
ORDER BY published_date DESC
LIMIT 50;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Documents table reset successfully!';
    RAISE NOTICE '✅ All views created';
    RAISE NOTICE '';
    RAISE NOTICE 'Next: Load your data';
    RAISE NOTICE 'python3 scripts/load_documents_to_ai_system.py --csv /path/to/csv';
END $$;
