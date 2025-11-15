-- ============================================================================
-- NEWS ARTICLES TABLE - Community Voice & Media Monitoring
-- ============================================================================
-- Captures news coverage of Mount Isa youth justice programs
-- Tracks community voice, success stories, problems, accountability
--
-- Add this to your existing Supabase database
-- ============================================================================

-- News articles table
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Article metadata
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    published_date TIMESTAMP WITH TIME ZONE,
    source VARCHAR(100),  -- North West Star, ABC, Guardian, etc.
    author VARCHAR(200),

    -- Content
    summary TEXT,
    full_text TEXT,  -- If scraped
    excerpt TEXT,     -- Pull quote or key paragraph

    -- Classification
    article_type VARCHAR(50),  -- success_story, problem, funding_announcement, outcome_report, policy, general
    sentiment VARCHAR(20),     -- positive, neutral, negative

    -- Entities mentioned
    programs_mentioned TEXT[],        -- Array of program names
    organizations_mentioned TEXT[],   -- Array of organization names
    funding_mentioned TEXT[],         -- Dollar amounts mentioned
    locations_mentioned TEXT[],       -- Mount Isa, Doomadgee, etc.

    -- Quotes (for rich storytelling)
    quotes JSONB,  -- [{text: "...", speaker: "...", role: "..."}]

    -- Themes/tags
    themes TEXT[],  -- indigenous_leadership, cultural_healing, accountability, outcomes, etc.
    keywords TEXT[],

    -- Engagement (if available)
    shares INTEGER,
    comments INTEGER,

    -- Verification
    fact_checked BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(100),
    verification_notes TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX idx_news_articles_published ON news_articles(published_date DESC);
CREATE INDEX idx_news_articles_source ON news_articles(source);
CREATE INDEX idx_news_articles_type ON news_articles(article_type);
CREATE INDEX idx_news_articles_sentiment ON news_articles(sentiment);
CREATE INDEX idx_news_articles_programs ON news_articles USING GIN(programs_mentioned);
CREATE INDEX idx_news_articles_orgs ON news_articles USING GIN(organizations_mentioned);
CREATE INDEX idx_news_articles_themes ON news_articles USING GIN(themes);

-- Full text search index
CREATE INDEX idx_news_articles_search ON news_articles USING GIN(to_tsvector('english', title || ' ' || COALESCE(summary, '')));

-- Update timestamp trigger
CREATE TRIGGER update_news_articles_updated_at
    BEFORE UPDATE ON news_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- USEFUL VIEWS
-- ============================================================================

-- Recent news by type
CREATE OR REPLACE VIEW v_news_by_type AS
SELECT
    article_type,
    COUNT(*) as article_count,
    MAX(published_date) as most_recent,
    ARRAY_AGG(DISTINCT source) as sources
FROM news_articles
WHERE published_date > NOW() - INTERVAL '30 days'
GROUP BY article_type
ORDER BY article_count DESC;

-- Sentiment analysis
CREATE OR REPLACE VIEW v_news_sentiment_trend AS
SELECT
    DATE_TRUNC('week', published_date) as week,
    sentiment,
    COUNT(*) as count
FROM news_articles
WHERE published_date > NOW() - INTERVAL '90 days'
GROUP BY week, sentiment
ORDER BY week DESC, sentiment;

-- Program mentions
CREATE OR REPLACE VIEW v_program_media_coverage AS
SELECT
    unnest(programs_mentioned) as program,
    COUNT(*) as mention_count,
    SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive_mentions,
    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_mentions,
    SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral_mentions,
    MAX(published_date) as last_mentioned
FROM news_articles
WHERE programs_mentioned IS NOT NULL
GROUP BY program
ORDER BY mention_count DESC;

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Recent success stories
-- SELECT title, source, published_date, summary
-- FROM news_articles
-- WHERE article_type = 'success_story'
--   AND published_date > NOW() - INTERVAL '30 days'
-- ORDER BY published_date DESC;

-- Articles mentioning Mithangkaya Nguli
-- SELECT title, source, published_date, sentiment
-- FROM news_articles
-- WHERE 'Mithangkaya Nguli' = ANY(organizations_mentioned)
-- ORDER BY published_date DESC;

-- Sentiment trend for On-Country program
-- SELECT published_date, sentiment, title
-- FROM news_articles
-- WHERE 'On-Country Program' = ANY(programs_mentioned)
-- ORDER BY published_date DESC;

-- Most covered programs
-- SELECT * FROM v_program_media_coverage
-- LIMIT 10;

-- ============================================================================
-- NOTES
-- ============================================================================
--
-- This table enables:
-- 1. Community voice tracking (what locals are saying)
-- 2. Media sentiment analysis (positive/negative coverage)
-- 3. Accountability journalism (are promises kept?)
-- 4. Success story identification (for JusticeHub)
-- 5. Problem detection (emerging issues)
--
-- Integration with existing data:
-- - Link articles to funding_announcements via programs_mentioned
-- - Cross-reference with actual_payments (did media cover the payment?)
-- - Connect to program_outcomes (did media report the results?)
--
-- For JusticeHub:
-- - success_story articles = featured content
-- - positive + outcome_report = evidence stories
-- - problem + accountability = investigation stories
--
-- ============================================================================
