-- Enhanced database schema with confidence scores and validation
-- For Supabase PostgreSQL

CREATE TABLE IF NOT EXISTS documents (
    -- Primary key
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

    -- Core document fields
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    content TEXT,
    html TEXT,

    -- Extracted date with confidence
    date DATE,
    date_confidence NUMERIC(3,2) CHECK (date_confidence >= 0 AND date_confidence <= 1),
    date_extraction_method TEXT,
    date_raw_text TEXT,  -- Original text the date was extracted from

    -- Extracted funding amount with confidence
    funding_amount NUMERIC(12,2),
    funding_confidence NUMERIC(3,2) CHECK (funding_confidence >= 0 AND funding_confidence <= 1),
    funding_extraction_method TEXT,
    funding_raw_text TEXT,  -- Original text the amount was extracted from

    -- Location information
    location TEXT,
    location_confidence NUMERIC(3,2),
    lga_code TEXT,  -- ABS LGA code (e.g., LGA35300 for Mount Isa)
    sa2_code TEXT,  -- ABS SA2 code

    -- Categorization (as per your flow schema)
    program_type TEXT,  -- 'MBS', 'PBS', 'grant', 'procurement', 'other'
    payer_type TEXT,  -- 'Commonwealth', 'State', 'LGA', 'Household', 'Business'
    payee_type TEXT,  -- 'Local business', 'External business', 'Household', 'Charity'
    industry_anzsic TEXT,  -- ANZSIC code
    categorization_confidence NUMERIC(3,2),

    -- Source tracking
    source_system TEXT NOT NULL,  -- e.g., 'qld_gov_scraper', 'grants_connect', etc.
    source_url TEXT,

    -- Quality flags
    needs_review BOOLEAN DEFAULT FALSE,
    review_notes TEXT,
    validation_warnings JSONB,  -- Array of validation warnings

    -- Metadata
    scraped_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    checksum TEXT,  -- Hash of content to detect duplicates/changes

    -- Additional fields
    summary TEXT,
    recipient TEXT,
    program_name TEXT,
    metadata JSONB  -- Flexible field for additional data
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_documents_date ON documents(date);
CREATE INDEX IF NOT EXISTS idx_documents_location ON documents(location);
CREATE INDEX IF NOT EXISTS idx_documents_lga_code ON documents(lga_code);
CREATE INDEX IF NOT EXISTS idx_documents_source_system ON documents(source_system);
CREATE INDEX IF NOT EXISTS idx_documents_needs_review ON documents(needs_review);
CREATE INDEX IF NOT EXISTS idx_documents_checksum ON documents(checksum);

-- Index for finding documents with low confidence
CREATE INDEX IF NOT EXISTS idx_documents_low_confidence
ON documents((LEAST(date_confidence, funding_confidence, location_confidence)));

-- View for documents needing review (low confidence or validation warnings)
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

-- View for high-quality documents only
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

-- Location statistics
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

COMMENT ON TABLE documents IS 'Scraped documents from Queensland government sources with confidence scoring';
COMMENT ON COLUMN documents.date_confidence IS 'Confidence score (0-1) for extracted date';
COMMENT ON COLUMN documents.funding_confidence IS 'Confidence score (0-1) for extracted funding amount';
COMMENT ON COLUMN documents.validation_warnings IS 'JSON array of validation warnings and data quality issues';
COMMENT ON COLUMN documents.needs_review IS 'Flag indicating document needs manual review';
