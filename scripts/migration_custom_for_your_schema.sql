-- Custom migration for your existing documents table
-- Adds confidence tracking fields to match your schema

-- Add confidence scores for existing fields
ALTER TABLE documents ADD COLUMN IF NOT EXISTS published_date_confidence NUMERIC(3,2) CHECK (published_date_confidence >= 0 AND published_date_confidence <= 1);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS published_date_extraction_method TEXT;

ALTER TABLE documents ADD COLUMN IF NOT EXISTS funding_confidence NUMERIC(3,2) CHECK (funding_confidence >= 0 AND funding_confidence <= 1);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS funding_extraction_method TEXT;

ALTER TABLE documents ADD COLUMN IF NOT EXISTS location_confidence NUMERIC(3,2);

-- Add categorization fields
ALTER TABLE documents ADD COLUMN IF NOT EXISTS program_type TEXT;  -- 'MBS', 'PBS', 'grant', 'procurement', 'other'
ALTER TABLE documents ADD COLUMN IF NOT EXISTS payer_type TEXT;  -- 'Commonwealth', 'State', 'LGA', 'Household', 'Business'
ALTER TABLE documents ADD COLUMN IF NOT EXISTS payee_type TEXT;  -- 'Local business', 'External business', 'Household', 'Charity'
ALTER TABLE documents ADD COLUMN IF NOT EXISTS categorization_confidence NUMERIC(3,2);

-- Add quality tracking fields
ALTER TABLE documents ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS review_notes TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS validation_warnings JSONB;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS checksum TEXT;

-- Add LGA code for Mount Isa tracking
ALTER TABLE documents ADD COLUMN IF NOT EXISTS lga_code TEXT;  -- e.g., 'LGA35300' for Mount Isa

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_documents_published_date ON documents(published_date);
CREATE INDEX IF NOT EXISTS idx_documents_needs_review ON documents(needs_review);
CREATE INDEX IF NOT EXISTS idx_documents_checksum ON documents(checksum);
CREATE INDEX IF NOT EXISTS idx_documents_lga_code ON documents(lga_code);

-- Index for finding documents with low confidence
CREATE INDEX IF NOT EXISTS idx_documents_low_confidence
ON documents((LEAST(published_date_confidence, funding_confidence, location_confidence)));

-- View for documents needing review (low confidence or validation warnings)
CREATE OR REPLACE VIEW documents_needing_review AS
SELECT
    id,
    title,
    published_date,
    published_date_confidence,
    funding_amount_extracted,
    funding_confidence,
    locations_mentioned,
    location_confidence,
    validation_warnings,
    needs_review,
    review_notes,
    source_type,
    scraped_date
FROM documents
WHERE
    needs_review = TRUE
    OR published_date_confidence < 0.7
    OR funding_confidence < 0.7
    OR location_confidence < 0.7
    OR validation_warnings IS NOT NULL
ORDER BY scraped_date DESC;

-- View for high-quality documents only
CREATE OR REPLACE VIEW documents_high_quality AS
SELECT *
FROM documents
WHERE
    (published_date_confidence IS NULL OR published_date_confidence >= 0.8)
    AND (funding_confidence IS NULL OR funding_confidence >= 0.8)
    AND (location_confidence IS NULL OR location_confidence >= 0.8)
    AND needs_review = FALSE
    AND validation_warnings IS NULL;

-- Enhanced statistics view
CREATE OR REPLACE VIEW document_statistics AS
SELECT
    COUNT(*) as total_documents,
    COUNT(funding_amount_extracted) as documents_with_funding,
    COUNT(DISTINCT published_date) as unique_dates,
    COUNT(CASE WHEN published_date = CURRENT_DATE THEN 1 END) as documents_with_today_date,
    COUNT(CASE WHEN needs_review = TRUE THEN 1 END) as documents_needing_review,
    ROUND(AVG(published_date_confidence), 2) as avg_date_confidence,
    ROUND(AVG(funding_confidence), 2) as avg_funding_confidence,
    ROUND(AVG(location_confidence), 2) as avg_location_confidence,
    SUM(funding_amount_extracted) as total_funding,
    COUNT(DISTINCT source_type) as unique_sources
FROM documents;

-- Location statistics view
CREATE OR REPLACE VIEW location_statistics AS
SELECT
    unnest(locations_mentioned) as location,
    COUNT(*) as document_count,
    SUM(funding_amount_extracted) as total_funding,
    ROUND(AVG(funding_confidence), 2) as avg_confidence,
    COUNT(CASE WHEN needs_review = TRUE THEN 1 END) as needing_review
FROM documents
WHERE locations_mentioned IS NOT NULL
GROUP BY location
ORDER BY document_count DESC;

-- Add comments
COMMENT ON COLUMN documents.published_date_confidence IS 'Confidence score (0-1) for extracted published date';
COMMENT ON COLUMN documents.funding_confidence IS 'Confidence score (0-1) for extracted funding amount';
COMMENT ON COLUMN documents.validation_warnings IS 'JSON array of validation warnings and data quality issues';
COMMENT ON COLUMN documents.needs_review IS 'Flag indicating document needs manual review';
COMMENT ON COLUMN documents.lga_code IS 'ABS LGA code (e.g., LGA35300 for Mount Isa)';

-- Mark all existing documents for review (they have no confidence scores)
UPDATE documents
SET needs_review = TRUE
WHERE published_date_confidence IS NULL AND funding_confidence IS NULL;

SELECT 'Migration complete! Added confidence tracking fields to documents table.' as result;
SELECT COUNT(*) || ' documents marked for review' as status FROM documents WHERE needs_review = TRUE;
