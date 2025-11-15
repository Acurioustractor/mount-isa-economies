-- Migration script to add confidence tracking to existing documents table
-- Use this if you already have a documents table with data

-- Add new confidence and tracking fields
ALTER TABLE documents ADD COLUMN IF NOT EXISTS date_confidence NUMERIC(3,2) CHECK (date_confidence >= 0 AND date_confidence <= 1);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS date_extraction_method TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS date_raw_text TEXT;

ALTER TABLE documents ADD COLUMN IF NOT EXISTS funding_confidence NUMERIC(3,2) CHECK (funding_confidence >= 0 AND funding_confidence <= 1);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS funding_extraction_method TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS funding_raw_text TEXT;

ALTER TABLE documents ADD COLUMN IF NOT EXISTS location_confidence NUMERIC(3,2);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS lga_code TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS sa2_code TEXT;

ALTER TABLE documents ADD COLUMN IF NOT EXISTS program_type TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS payer_type TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS payee_type TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS industry_anzsic TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS categorization_confidence NUMERIC(3,2);

ALTER TABLE documents ADD COLUMN IF NOT EXISTS source_url TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS review_notes TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS validation_warnings JSONB;

ALTER TABLE documents ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE documents ADD COLUMN IF NOT EXISTS checksum TEXT;

ALTER TABLE documents ADD COLUMN IF NOT EXISTS summary TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS recipient TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS program_name TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_documents_date ON documents(date);
CREATE INDEX IF NOT EXISTS idx_documents_location ON documents(location);
CREATE INDEX IF NOT EXISTS idx_documents_lga_code ON documents(lga_code);
CREATE INDEX IF NOT EXISTS idx_documents_source_system ON documents(source_system);
CREATE INDEX IF NOT EXISTS idx_documents_needs_review ON documents(needs_review);
CREATE INDEX IF NOT EXISTS idx_documents_checksum ON documents(checksum);

CREATE INDEX IF NOT EXISTS idx_documents_low_confidence
ON documents((LEAST(date_confidence, funding_confidence, location_confidence)));

-- Create views
CREATE OR REPLACE VIEW documents_needing_review AS
SELECT
    id,
    title,
    date,
    date_confidence,
    funding_amount,
    funding_confidence,
    location,
    location_confidence,
    validation_warnings,
    needs_review,
    review_notes,
    source_system,
    scraped_at
FROM documents
WHERE
    needs_review = TRUE
    OR date_confidence < 0.7
    OR funding_confidence < 0.7
    OR location_confidence < 0.7
    OR validation_warnings IS NOT NULL
ORDER BY scraped_at DESC;

CREATE OR REPLACE VIEW documents_high_quality AS
SELECT *
FROM documents
WHERE
    (date_confidence IS NULL OR date_confidence >= 0.8)
    AND (funding_confidence IS NULL OR funding_confidence >= 0.8)
    AND (location_confidence IS NULL OR location_confidence >= 0.8)
    AND needs_review = FALSE
    AND validation_warnings IS NULL;

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Statistics view
CREATE OR REPLACE VIEW document_statistics AS
SELECT
    COUNT(*) as total_documents,
    COUNT(funding_amount) as documents_with_funding,
    COUNT(DISTINCT date) as unique_dates,
    COUNT(CASE WHEN date = CURRENT_DATE THEN 1 END) as documents_with_today_date,
    COUNT(CASE WHEN needs_review = TRUE THEN 1 END) as documents_needing_review,
    ROUND(AVG(date_confidence), 2) as avg_date_confidence,
    ROUND(AVG(funding_confidence), 2) as avg_funding_confidence,
    ROUND(AVG(location_confidence), 2) as avg_location_confidence,
    SUM(funding_amount) as total_funding,
    COUNT(DISTINCT location) as unique_locations,
    COUNT(DISTINCT source_system) as unique_sources
FROM documents;

CREATE OR REPLACE VIEW location_statistics AS
SELECT
    location,
    COUNT(*) as document_count,
    SUM(funding_amount) as total_funding,
    ROUND(AVG(funding_confidence), 2) as avg_confidence,
    COUNT(CASE WHEN needs_review = TRUE THEN 1 END) as needing_review
FROM documents
WHERE location IS NOT NULL
GROUP BY location
ORDER BY document_count DESC;

-- Add comments
COMMENT ON COLUMN documents.date_confidence IS 'Confidence score (0-1) for extracted date';
COMMENT ON COLUMN documents.funding_confidence IS 'Confidence score (0-1) for extracted funding amount';
COMMENT ON COLUMN documents.validation_warnings IS 'JSON array of validation warnings and data quality issues';
COMMENT ON COLUMN documents.needs_review IS 'Flag indicating document needs manual review';

-- Mark all existing documents for review (they have no confidence scores)
UPDATE documents
SET needs_review = TRUE
WHERE date_confidence IS NULL AND funding_confidence IS NULL;

SELECT 'Migration complete! Added confidence tracking fields to documents table.' as result;
