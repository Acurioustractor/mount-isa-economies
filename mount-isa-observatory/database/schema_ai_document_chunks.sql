-- ============================================================================
-- AI-POWERED DOCUMENT CHUNKING & SEMANTIC SEARCH SCHEMA
-- ============================================================================
-- Purpose: Store media statements with chunking for RAG/semantic search
--          Enable AI analysis, story generation, and continuous learning
--
-- Key Features:
-- 1. Document chunking for embedding generation
-- 2. Vector embeddings for semantic search (pgvector)
-- 3. AI-generated analysis and insights
-- 4. Story templates and generation
-- 5. Cross-reference and citation tracking
-- 6. Continuous ingestion pipeline
--
-- Usage:
--   1. Load to Supabase SQL editor
--   2. Enable pgvector extension first: CREATE EXTENSION vector;
--   3. Run this schema
-- ============================================================================

-- Enable pgvector extension for semantic search
-- Run this first if not already enabled:
-- CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- CORE TABLES: Documents & Chunks
-- ============================================================================

-- Main documents table (enhanced from existing media_statements)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic metadata
    url TEXT UNIQUE NOT NULL,
    statement_id TEXT,
    title TEXT NOT NULL,
    published_date DATE NOT NULL,
    scraped_date TIMESTAMP DEFAULT NOW(),

    -- Source info
    source_type VARCHAR(50) DEFAULT 'media_statement', -- 'media_statement', 'budget_paper', 'contract', 'foi'
    source_organization VARCHAR(200) DEFAULT 'Queensland Government',
    minister_name TEXT,
    portfolio TEXT,

    -- Content
    full_text TEXT NOT NULL,
    markdown_text TEXT,
    summary TEXT, -- AI-generated summary

    -- Extracted entities
    funding_amount_extracted NUMERIC, -- Primary amount in statement
    funding_amounts_all JSONB, -- All amounts found: [{amount: 24, unit: 'M', context: '...'}]
    programs_mentioned TEXT[], -- Array of program names
    locations_mentioned TEXT[], -- Array of locations/communities
    organizations_mentioned TEXT[], -- Array of org names
    people_mentioned JSONB, -- [{name: 'Hon. X Y', role: 'Minister'}]

    -- AI analysis
    ai_analysis_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'complete', 'failed'
    ai_analysis_results JSONB, -- AI-generated insights, sentiment, themes
    embedding_status VARCHAR(50) DEFAULT 'pending', -- Track embedding generation

    -- Search and classification
    keywords TEXT[],
    categories TEXT[], -- ['early_intervention', 'rehabilitation', 'detention']
    relevance_score NUMERIC, -- How relevant to youth justice (0-1)

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT 'system',

    -- Indexes
    CONSTRAINT valid_source_type CHECK (source_type IN ('media_statement', 'budget_paper', 'contract', 'foi', 'parliamentary', 'report', 'evaluation'))
);

CREATE INDEX idx_documents_published_date ON documents(published_date DESC);
CREATE INDEX idx_documents_source_type ON documents(source_type);
CREATE INDEX idx_documents_ai_status ON documents(ai_analysis_status);
CREATE INDEX idx_documents_embedding_status ON documents(embedding_status);
CREATE INDEX idx_documents_programs ON documents USING GIN(programs_mentioned);
CREATE INDEX idx_documents_locations ON documents USING GIN(locations_mentioned);
CREATE INDEX idx_documents_keywords ON documents USING GIN(keywords);
CREATE INDEX idx_documents_categories ON documents USING GIN(categories);


-- Document chunks for embedding/RAG
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,

    -- Chunk metadata
    chunk_index INTEGER NOT NULL, -- Position in document (0, 1, 2...)
    chunk_text TEXT NOT NULL,
    chunk_size INTEGER NOT NULL, -- Character count

    -- Chunk type/context
    chunk_type VARCHAR(50) DEFAULT 'paragraph', -- 'paragraph', 'quote', 'funding_detail', 'heading'
    section_heading TEXT, -- Parent section this chunk belongs to

    -- Embeddings for semantic search (1536 dimensions for OpenAI ada-002)
    embedding vector(1536), -- Use pgvector extension

    -- Extracted info from this chunk
    entities_in_chunk JSONB, -- Entities mentioned in this specific chunk
    funding_amount NUMERIC, -- If chunk contains funding amount

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_document_chunk UNIQUE(document_id, chunk_index)
);

CREATE INDEX idx_chunks_document ON document_chunks(document_id);
CREATE INDEX idx_chunks_type ON document_chunks(chunk_type);
-- Vector similarity search index (will error if pgvector not enabled)
-- CREATE INDEX idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);


-- ============================================================================
-- AI ANALYSIS & INSIGHTS
-- ============================================================================

-- AI-generated analysis results
CREATE TABLE IF NOT EXISTS ai_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,

    -- Analysis metadata
    analysis_type VARCHAR(100) NOT NULL, -- 'summary', 'entity_extraction', 'sentiment', 'verification', 'story_ideas'
    analysis_version VARCHAR(50) DEFAULT 'v1', -- Track model versions
    model_used VARCHAR(100), -- 'gpt-4', 'claude-3', etc.

    -- Results
    analysis_result JSONB NOT NULL,
    confidence_score NUMERIC, -- How confident is the AI (0-1)

    -- Specific analysis types
    -- For 'verification' type:
    verification_status VARCHAR(50), -- 'verified', 'unverified', 'contradicted', 'partially_verified'
    verification_evidence JSONB, -- Links to supporting/contradicting documents

    -- For 'story_ideas' type:
    story_template VARCHAR(100), -- 'accountability', 'evidence', 'community_voice'
    story_priority INTEGER, -- 1-10 priority score
    story_outline TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT 'ai_system',

    -- Constraints
    CONSTRAINT unique_analysis UNIQUE(document_id, analysis_type, analysis_version)
);

CREATE INDEX idx_ai_analysis_type ON ai_analysis(analysis_type);
CREATE INDEX idx_ai_analysis_document ON ai_analysis(document_id);
CREATE INDEX idx_ai_verification_status ON ai_analysis(verification_status);


-- ============================================================================
-- CROSS-REFERENCES & CITATIONS
-- ============================================================================

-- Links between documents (citations, mentions, contradictions)
CREATE TABLE IF NOT EXISTS document_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    source_document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    target_document_id UUID REFERENCES documents(id) ON DELETE CASCADE,

    link_type VARCHAR(50) NOT NULL, -- 'cites', 'mentions', 'updates', 'contradicts', 'supports'
    link_strength NUMERIC DEFAULT 0.5, -- How strong is the connection (0-1)

    -- Context
    context_snippet TEXT, -- Text where the link occurs
    auto_detected BOOLEAN DEFAULT FALSE, -- Was this auto-detected by AI?

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT 'system',

    CONSTRAINT no_self_reference CHECK (source_document_id != target_document_id)
);

CREATE INDEX idx_links_source ON document_links(source_document_id);
CREATE INDEX idx_links_target ON document_links(target_document_id);
CREATE INDEX idx_links_type ON document_links(link_type);


-- ============================================================================
-- STORY GENERATION & TEMPLATES
-- ============================================================================

-- Story templates for JusticeHub
CREATE TABLE IF NOT EXISTS story_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    template_name VARCHAR(200) NOT NULL UNIQUE,
    template_type VARCHAR(100) NOT NULL, -- 'accountability', 'evidence', 'verification', 'impact'

    -- Template structure
    headline_pattern TEXT, -- "Government announces $X for Y, still no payment Z days later"
    required_data JSONB, -- What data points are needed
    optional_data JSONB,

    -- Generation instructions
    ai_generation_prompt TEXT, -- Prompt for AI to fill template
    example_output TEXT,

    -- Priority and filtering
    priority INTEGER DEFAULT 5, -- 1-10
    min_funding_amount NUMERIC, -- Only for announcements > this amount
    required_categories TEXT[], -- Must match these categories

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE
);


-- Generated stories ready to publish
CREATE TABLE IF NOT EXISTS generated_stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Story metadata
    template_id UUID REFERENCES story_templates(id),
    headline TEXT NOT NULL,
    story_type VARCHAR(100),

    -- Content
    story_text TEXT NOT NULL,
    story_summary TEXT,
    key_findings JSONB, -- Bullet points

    -- Supporting documents
    primary_document_id UUID REFERENCES documents(id),
    supporting_document_ids UUID[], -- Array of related document IDs

    -- Data/evidence
    evidence_data JSONB, -- All the data points used in story
    quotes JSONB, -- [{text: '...', source: '...'}]

    -- Publication
    publication_status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'review', 'published', 'archived'
    published_date TIMESTAMP,
    published_url TEXT,

    -- Quality metrics
    ai_confidence_score NUMERIC, -- How confident is AI in this story (0-1)
    human_reviewed BOOLEAN DEFAULT FALSE,
    review_notes TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT 'ai_system'
);

CREATE INDEX idx_stories_status ON generated_stories(publication_status);
CREATE INDEX idx_stories_template ON generated_stories(template_id);
CREATE INDEX idx_stories_primary_doc ON generated_stories(primary_document_id);


-- ============================================================================
-- CONTINUOUS INGESTION & PROCESSING PIPELINE
-- ============================================================================

-- Queue for processing new documents
CREATE TABLE IF NOT EXISTS processing_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,

    -- Processing stages
    stage VARCHAR(100) NOT NULL, -- 'chunking', 'embedding', 'ai_analysis', 'story_generation'
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'complete', 'failed'

    priority INTEGER DEFAULT 5, -- 1-10, higher = more urgent

    -- Error handling
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    last_error TEXT,
    last_attempt_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_document_stage UNIQUE(document_id, stage)
);

CREATE INDEX idx_queue_status ON processing_queue(status);
CREATE INDEX idx_queue_stage ON processing_queue(stage);
CREATE INDEX idx_queue_priority ON processing_queue(priority DESC);


-- Processing logs
CREATE TABLE IF NOT EXISTS processing_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    stage VARCHAR(100),

    status VARCHAR(50),
    duration_ms INTEGER, -- How long it took

    log_message TEXT,
    metadata JSONB,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_logs_document ON processing_logs(document_id);
CREATE INDEX idx_logs_created ON processing_logs(created_at DESC);


-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Documents with full AI analysis
CREATE OR REPLACE VIEW v_documents_analyzed AS
SELECT
    d.id,
    d.url,
    d.title,
    d.published_date,
    d.minister_name,
    d.funding_amount_extracted,
    d.programs_mentioned,
    d.locations_mentioned,
    d.summary,
    d.categories,

    -- Count of chunks
    COUNT(DISTINCT dc.id) as chunk_count,

    -- AI analysis status
    d.ai_analysis_status,

    -- Get all AI analyses
    json_agg(DISTINCT jsonb_build_object(
        'type', aa.analysis_type,
        'result', aa.analysis_result,
        'confidence', aa.confidence_score
    )) FILTER (WHERE aa.id IS NOT NULL) as ai_analyses,

    -- Related stories
    COUNT(DISTINCT gs.id) as story_count

FROM documents d
LEFT JOIN document_chunks dc ON d.id = dc.document_id
LEFT JOIN ai_analysis aa ON d.id = aa.document_id
LEFT JOIN generated_stories gs ON d.id = gs.primary_document_id
GROUP BY d.id;


-- Unverified funding announcements (accountability stories)
CREATE OR REPLACE VIEW v_unverified_funding AS
SELECT
    d.id,
    d.title,
    d.published_date,
    d.funding_amount_extracted,
    d.programs_mentioned,
    d.locations_mentioned,

    -- Days since announcement
    CURRENT_DATE - d.published_date as days_since_announcement,

    -- Has verification?
    COALESCE(aa.verification_status, 'unverified') as verification_status,
    aa.verification_evidence

FROM documents d
LEFT JOIN ai_analysis aa ON d.id = aa.document_id
    AND aa.analysis_type = 'verification'
WHERE d.funding_amount_extracted > 0
  AND d.categories && ARRAY['youth_justice', 'early_intervention', 'on_country']
ORDER BY d.funding_amount_extracted DESC;


-- Story opportunities (high-priority stories to generate)
CREATE OR REPLACE VIEW v_story_opportunities AS
SELECT
    st.template_name,
    st.template_type,
    st.priority,

    COUNT(d.id) as matching_documents,
    SUM(d.funding_amount_extracted) as total_funding,

    -- Most recent matching document
    MAX(d.published_date) as most_recent_document,

    -- Sample documents
    array_agg(d.id ORDER BY d.published_date DESC LIMIT 5) as sample_document_ids

FROM story_templates st
LEFT JOIN documents d ON
    (st.required_categories && d.categories OR st.required_categories IS NULL)
    AND (d.funding_amount_extracted >= st.min_funding_amount OR st.min_funding_amount IS NULL)
WHERE st.active = TRUE
GROUP BY st.id, st.template_name, st.template_type, st.priority
HAVING COUNT(d.id) > 0
ORDER BY st.priority DESC, total_funding DESC;


-- Processing pipeline status
CREATE OR REPLACE VIEW v_processing_status AS
SELECT
    stage,
    status,
    COUNT(*) as count,
    AVG(attempts) as avg_attempts,
    MAX(updated_at) as last_updated
FROM processing_queue
GROUP BY stage, status
ORDER BY stage, status;


-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to add document to processing queue
CREATE OR REPLACE FUNCTION queue_document_for_processing(
    p_document_id UUID,
    p_stages TEXT[] DEFAULT ARRAY['chunking', 'embedding', 'ai_analysis', 'story_generation']
)
RETURNS VOID AS $$
BEGIN
    -- Add each stage to queue
    INSERT INTO processing_queue (document_id, stage, priority)
    SELECT p_document_id, unnest(p_stages), 5
    ON CONFLICT (document_id, stage) DO NOTHING;
END;
$$ LANGUAGE plpgsql;


-- Function to update document timestamps
CREATE OR REPLACE FUNCTION update_document_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_document_timestamp
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_document_timestamp();


-- ============================================================================
-- INITIAL DATA: Story Templates
-- ============================================================================

INSERT INTO story_templates (template_name, template_type, headline_pattern, required_data, ai_generation_prompt, priority, min_funding_amount) VALUES
(
    'Accountability: Unverified Payment',
    'accountability',
    'Government announced $X for Y in Z, but {days} days later, still no verification of payment',
    '{"funding_amount": true, "program_name": true, "announcement_date": true}',
    'Write an accountability story about a government funding announcement that has not been verified. Focus on: 1) What was announced, 2) How long ago, 3) Why verification matters, 4) Impact on community.',
    10,
    1000000
),
(
    'Evidence: What Works',
    'evidence',
    'Research shows {program_type} reduces youth crime by X%, but Queensland invests only $Y',
    '{"evidence_data": true, "program_effectiveness": true, "funding_gap": true}',
    'Write an evidence-based story comparing research on program effectiveness with actual funding allocations. Use data to show the gap between what works and what gets funded.',
    9,
    NULL
),
(
    'Community Voice: Impact Story',
    'community_voice',
    '{Community} receives $X for {program}, but locals say {reality}',
    '{"community_name": true, "funding_amount": true, "program_name": true}',
    'Write a community impact story. Balance the official announcement with what is actually happening on the ground. Include quotes and community perspective.',
    8,
    500000
),
(
    'Verification: Payment Confirmed',
    'verification',
    'Exclusive: $X payment for {program} confirmed, {months} months after announcement',
    '{"funding_amount": true, "program_name": true, "verification_date": true}',
    'Write a verification story confirming that announced funding has actually been paid. Include timeline, what the delay was, and what it means for the program.',
    7,
    1000000
);


-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE documents IS 'Main documents table with AI analysis status and embeddings metadata';
COMMENT ON TABLE document_chunks IS 'Text chunks from documents for RAG/semantic search with vector embeddings';
COMMENT ON TABLE ai_analysis IS 'AI-generated analysis results including verification, sentiment, story ideas';
COMMENT ON TABLE document_links IS 'Cross-references between documents for citation and contradiction tracking';
COMMENT ON TABLE story_templates IS 'Templates for automated story generation';
COMMENT ON TABLE generated_stories IS 'AI-generated stories ready for human review and publication';
COMMENT ON TABLE processing_queue IS 'Queue for processing documents through AI pipeline';
COMMENT ON TABLE processing_logs IS 'Audit log of all processing activities';

COMMENT ON COLUMN documents.embedding_status IS 'Track whether embeddings have been generated for RAG';
COMMENT ON COLUMN document_chunks.embedding IS 'Vector embedding (1536 dims) for semantic search using pgvector';
COMMENT ON COLUMN ai_analysis.verification_status IS 'Whether funding announcement has been verified with payment evidence';
COMMENT ON COLUMN generated_stories.ai_confidence_score IS 'How confident AI is in story accuracy (0-1)';
