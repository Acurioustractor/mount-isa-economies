-- Mount Isa Economic Observatory - Scalable Database Schema V2
-- Designed to handle millions of transactions and continuous data scraping

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy text matching
CREATE EXTENSION IF NOT EXISTS btree_gin; -- For multi-column indexes
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE; -- For time-series data (optional but recommended)

-- =====================================================
-- CORE: DATA PROVENANCE & SOURCE TRACKING
-- =====================================================

CREATE TABLE data_sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(200) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL, -- 'API', 'WEB_SCRAPE', 'MANUAL', 'COMMUNITY_INPUT'
    source_url TEXT,
    api_endpoint TEXT,
    update_frequency VARCHAR(50), -- 'DAILY', 'WEEKLY', 'MONTHLY', 'REAL_TIME'
    last_fetch_at TIMESTAMP,
    next_fetch_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    scraper_config JSONB, -- Store scraper settings
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sources_active ON data_sources(is_active, next_fetch_at);

-- Track every data fetch with full provenance
CREATE TABLE data_fetch_log (
    fetch_id BIGSERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES data_sources(source_id),
    fetch_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    records_fetched INTEGER,
    records_new INTEGER,
    records_updated INTEGER,
    file_hash VARCHAR(64), -- SHA-256
    file_path TEXT,
    status VARCHAR(50), -- 'SUCCESS', 'FAILED', 'PARTIAL'
    error_message TEXT,
    metadata JSONB
);

CREATE INDEX idx_fetch_log_source ON data_fetch_log(source_id, fetch_timestamp DESC);
CREATE INDEX idx_fetch_log_status ON data_fetch_log(status, fetch_timestamp DESC);

-- =====================================================
-- GEOGRAPHIC DATA (PostGIS powered)
-- =====================================================

CREATE TABLE geography (
    geo_id SERIAL PRIMARY KEY,
    geo_type VARCHAR(50) NOT NULL, -- 'LGA', 'SA2', 'SA3', 'SUBURB', 'POSTCODE', 'INDIGENOUS_LAND'
    geo_code VARCHAR(50) NOT NULL,
    geo_name VARCHAR(200) NOT NULL,
    parent_geo_id INTEGER REFERENCES geography(geo_id),
    boundary GEOMETRY(MULTIPOLYGON, 4326),
    centroid GEOMETRY(POINT, 4326),
    area_sqkm DECIMAL(12, 2),
    population INTEGER,
    indigenous_population INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(geo_type, geo_code)
);

CREATE INDEX idx_geo_boundary ON geography USING GIST(boundary);
CREATE INDEX idx_geo_centroid ON geography USING GIST(centroid);
CREATE INDEX idx_geo_type ON geography(geo_type);

-- Pre-populate Mount Isa geography
INSERT INTO geography (geo_type, geo_code, geo_name, centroid, metadata) VALUES
('LGA', 'LGA35300', 'Mount Isa (C)', ST_SetSRID(ST_MakePoint(139.4927, -20.7256), 4326),
 '{"state": "QLD", "traditional_owners": "Kalkadoon", "population_2021": 18916}'::jsonb),
('POSTCODE', '4825', 'Mount Isa', ST_SetSRID(ST_MakePoint(139.4927, -20.7256), 4326),
 '{"state": "QLD"}'::jsonb);

-- =====================================================
-- ENTITIES (Businesses, Orgs, Government, People)
-- =====================================================

CREATE TABLE entities (
    entity_id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL, -- 'BUSINESS', 'CHARITY', 'GOVERNMENT', 'INDIVIDUAL', 'INDIGENOUS_CORP'

    -- Identifiers
    abn VARCHAR(11),
    acn VARCHAR(9),
    entity_name VARCHAR(500) NOT NULL,
    legal_name VARCHAR(500),
    trading_names TEXT[], -- Array of trading names

    -- Classification
    industry_anzsic VARCHAR(10),
    is_local BOOLEAN,
    is_indigenous_owned BOOLEAN DEFAULT FALSE,
    is_community_owned BOOLEAN DEFAULT FALSE,

    -- Location
    primary_geo_id INTEGER REFERENCES geography(geo_id),
    address TEXT,
    postcode VARCHAR(10),
    location GEOMETRY(POINT, 4326),

    -- Contact
    phone VARCHAR(50),
    email VARCHAR(200),
    website TEXT,

    -- Status
    status VARCHAR(50) DEFAULT 'ACTIVE', -- 'ACTIVE', 'INACTIVE', 'DORMANT'

    -- Rich data
    description TEXT,
    services_provided TEXT[],
    metadata JSONB, -- Flexible storage for source-specific data

    -- Provenance
    source_id INTEGER REFERENCES data_sources(source_id),
    source_record_id VARCHAR(200),
    confidence_score DECIMAL(3, 2), -- 0.00 to 1.00

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    verified_by VARCHAR(200)
);

-- Indexes for fast lookups
CREATE INDEX idx_entities_abn ON entities(abn);
CREATE INDEX idx_entities_name ON entities USING GIN(entity_name gin_trgm_ops); -- Fuzzy search
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_local ON entities(is_local);
CREATE INDEX idx_entities_indigenous ON entities(is_indigenous_owned);
CREATE INDEX idx_entities_location ON entities USING GIST(location);
CREATE INDEX idx_entities_geo ON entities(primary_geo_id);

-- =====================================================
-- SERVICES (from your service map!)
-- =====================================================

CREATE TABLE services (
    service_id BIGSERIAL PRIMARY KEY,
    service_name VARCHAR(500) NOT NULL,
    entity_id BIGINT REFERENCES entities(entity_id),

    -- Classification
    service_category VARCHAR(200), -- 'Health', 'Youth Justice', 'Education', etc.
    service_subcategory VARCHAR(200),
    service_type VARCHAR(200),

    -- Targeting
    target_population TEXT[], -- ['Indigenous youth', 'Families', 'Elderly']
    age_range VARCHAR(50),

    -- Access
    is_local BOOLEAN,
    is_culturally_safe BOOLEAN,
    requires_referral BOOLEAN,
    wait_time_days INTEGER,
    capacity_current INTEGER,
    capacity_max INTEGER,

    -- Location
    service_location GEOMETRY(POINT, 4326),
    service_area GEOMETRY(MULTIPOLYGON, 4326), -- Coverage area

    -- Rich data
    description TEXT,
    eligibility_criteria TEXT,
    cost_structure VARCHAR(200), -- 'FREE', 'BULK_BILLED', 'FEE_FOR_SERVICE'

    -- Community voice
    community_feedback TEXT[],
    sentiment_score DECIMAL(3, 2), -- From interview analysis

    -- Provenance
    source_id INTEGER REFERENCES data_sources(source_id),
    confidence_score DECIMAL(3, 2),

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_services_entity ON services(entity_id);
CREATE INDEX idx_services_category ON services(service_category);
CREATE INDEX idx_services_local ON services(is_local);
CREATE INDEX idx_services_location ON services USING GIST(service_location);
CREATE INDEX idx_services_area ON services USING GIST(service_area);

-- =====================================================
-- ECONOMIC FLOWS (Time-series partitioned for scale)
-- =====================================================

CREATE TABLE economic_flows (
    flow_id BIGSERIAL,
    flow_timestamp TIMESTAMP NOT NULL,

    -- Who paid whom
    payer_entity_id BIGINT REFERENCES entities(entity_id),
    payee_entity_id BIGINT REFERENCES entities(entity_id),

    -- What was it
    flow_type VARCHAR(100), -- 'WAGE', 'PROCUREMENT', 'GRANT', 'PURCHASE', 'INVESTMENT'
    program_type VARCHAR(100), -- 'MBS', 'PBS', 'NDIS', 'MINING_WAGE', etc.
    description TEXT,

    -- Amount
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'AUD',

    -- Geography
    from_geo_id INTEGER REFERENCES geography(geo_id),
    to_geo_id INTEGER REFERENCES geography(geo_id),

    -- Classification
    is_leakage BOOLEAN, -- Money leaving Mount Isa
    flow_direction VARCHAR(20), -- 'INFLOW', 'OUTFLOW', 'INTERNAL'
    industry VARCHAR(10), -- ANZSIC code

    -- Provenance
    source_id INTEGER REFERENCES data_sources(source_id),
    source_record_id VARCHAR(200),
    confidence_score DECIMAL(3, 2),

    -- Metadata
    metadata JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (flow_id, flow_timestamp)
) PARTITION BY RANGE (flow_timestamp);

-- Create partitions for each year (add more as needed)
CREATE TABLE economic_flows_2024 PARTITION OF economic_flows
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE economic_flows_2025 PARTITION OF economic_flows
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Indexes on partitioned table
CREATE INDEX idx_flows_payer ON economic_flows(payer_entity_id, flow_timestamp DESC);
CREATE INDEX idx_flows_payee ON economic_flows(payee_entity_id, flow_timestamp DESC);
CREATE INDEX idx_flows_type ON economic_flows(flow_type, flow_timestamp DESC);
CREATE INDEX idx_flows_leakage ON economic_flows(is_leakage, flow_timestamp DESC);
CREATE INDEX idx_flows_geo ON economic_flows(from_geo_id, to_geo_id);

-- =====================================================
-- GRANTS & FUNDING
-- =====================================================

CREATE TABLE grants (
    grant_id BIGSERIAL PRIMARY KEY,
    grant_name VARCHAR(500) NOT NULL,
    grant_program VARCHAR(200),
    funding_body VARCHAR(200), -- 'Queensland Government', 'Commonwealth', etc.

    -- Recipients
    recipient_entity_id BIGINT REFERENCES entities(entity_id),

    -- Amount & Duration
    total_amount DECIMAL(15, 2) NOT NULL,
    annual_amount DECIMAL(15, 2),
    start_date DATE,
    end_date DATE,

    -- Focus
    focus_area VARCHAR(200), -- 'Youth Justice', 'Health', 'Education'
    target_beneficiaries TEXT[],

    -- Indigenous
    is_indigenous_led BOOLEAN DEFAULT FALSE,
    is_culturally_designed BOOLEAN DEFAULT FALSE,
    elder_involvement BOOLEAN DEFAULT FALSE,

    -- Outcomes
    objectives TEXT,
    outcomes_achieved TEXT[],
    young_people_served INTEGER,
    jobs_created INTEGER,

    -- Provenance
    source_id INTEGER REFERENCES data_sources(source_id),
    announcement_url TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_grants_recipient ON grants(recipient_entity_id);
CREATE INDEX idx_grants_focus ON grants(focus_area);
CREATE INDEX idx_grants_indigenous ON grants(is_indigenous_led);
CREATE INDEX idx_grants_dates ON grants(start_date, end_date);

-- =====================================================
-- COMMUNITY VOICE & KNOWLEDGE
-- =====================================================

CREATE TABLE community_interviews (
    interview_id BIGSERIAL PRIMARY KEY,
    interview_date DATE,

    -- Respondent (anonymized)
    respondent_type VARCHAR(100), -- 'ELDER', 'YOUTH', 'PARENT', 'SERVICE_PROVIDER'
    respondent_demographic VARCHAR(100),
    is_indigenous BOOLEAN,

    -- Location
    geo_id INTEGER REFERENCES geography(geo_id),

    -- Content (from your 127 interviews!)
    themes TEXT[], -- Extracted themes
    service_gaps TEXT[],
    positive_feedback TEXT,
    concerns TEXT,
    suggestions TEXT,

    -- Analysis
    sentiment_score DECIMAL(3, 2), -- -1.00 to 1.00
    priority_score DECIMAL(3, 2), -- Urgency/importance
    ai_analysis JSONB, -- Full AI analysis

    -- Provenance
    source_id INTEGER REFERENCES data_sources(source_id),
    interviewer VARCHAR(200),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interviews_date ON community_interviews(interview_date DESC);
CREATE INDEX idx_interviews_type ON community_interviews(respondent_type);
CREATE INDEX idx_interviews_geo ON community_interviews(geo_id);

-- =====================================================
-- INDIGENOUS KNOWLEDGE & CULTURAL ECONOMY
-- =====================================================

CREATE TABLE indigenous_knowledge (
    knowledge_id BIGSERIAL PRIMARY KEY,
    knowledge_type VARCHAR(100), -- 'ART', 'STORY', 'PRACTICE', 'PLACE', 'CEREMONY'

    -- Content (with appropriate permissions)
    title VARCHAR(500),
    description TEXT,
    is_restricted BOOLEAN DEFAULT FALSE, -- Some knowledge is sacred/restricted
    permission_level VARCHAR(50), -- 'PUBLIC', 'COMMUNITY_ONLY', 'ELDER_ONLY'

    -- Custodians
    traditional_owner_group VARCHAR(200), -- 'Kalkadoon'
    knowledge_holders TEXT[], -- Names of Elders (if permitted)

    -- Economic value
    estimated_cultural_value DECIMAL(15, 2), -- If commodified (e.g., art sales)
    tourism_value DECIMAL(15, 2),
    educational_value DECIMAL(15, 2),

    -- Location
    location GEOMETRY(POINT, 4326),
    sacred_site BOOLEAN DEFAULT FALSE,

    -- Metadata
    metadata JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(200), -- Who recorded this
    approved_by VARCHAR(200) -- Elder approval
);

CREATE INDEX idx_knowledge_type ON indigenous_knowledge(knowledge_type);
CREATE INDEX idx_knowledge_location ON indigenous_knowledge USING GIST(location);

-- =====================================================
-- MATERIALIZED VIEWS FOR FAST ANALYTICS
-- =====================================================

-- Total leakage by category (refreshed daily)
CREATE MATERIALIZED VIEW mv_leakage_by_category AS
SELECT
    EXTRACT(YEAR FROM flow_timestamp) AS year,
    EXTRACT(QUARTER FROM flow_timestamp) AS quarter,
    flow_type,
    industry,
    SUM(amount) AS total_leakage,
    COUNT(*) AS transaction_count,
    AVG(amount) AS avg_transaction
FROM economic_flows
WHERE is_leakage = TRUE
GROUP BY EXTRACT(YEAR FROM flow_timestamp), EXTRACT(QUARTER FROM flow_timestamp), flow_type, industry;

CREATE INDEX idx_mv_leakage ON mv_leakage_by_category(year, quarter, total_leakage DESC);

-- Service capacity vs demand
CREATE MATERIALIZED VIEW mv_service_capacity AS
SELECT
    s.service_category,
    s.service_subcategory,
    COUNT(*) AS service_count,
    SUM(CASE WHEN s.is_local THEN 1 ELSE 0 END) AS local_service_count,
    AVG(s.wait_time_days) AS avg_wait_time,
    SUM(s.capacity_max) AS total_capacity,
    array_agg(DISTINCT ci.themes) AS community_identified_gaps
FROM services s
LEFT JOIN community_interviews ci ON ci.themes && ARRAY[s.service_category]
GROUP BY s.service_category, s.service_subcategory;

-- Refresh functions
CREATE OR REPLACE FUNCTION refresh_analytics_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_leakage_by_category;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_service_capacity;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCTIONS FOR ECONOMIC ANALYSIS
-- =====================================================

-- Calculate total economic activity
CREATE OR REPLACE FUNCTION calculate_economic_activity(
    p_geo_id INTEGER,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE(
    total_inflows DECIMAL,
    total_outflows DECIMAL,
    total_internal DECIMAL,
    leakage_amount DECIMAL,
    leakage_percent DECIMAL,
    local_multiplier DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH flows AS (
        SELECT
            SUM(CASE WHEN flow_direction = 'INFLOW' THEN amount ELSE 0 END) AS inflows,
            SUM(CASE WHEN flow_direction = 'OUTFLOW' THEN amount ELSE 0 END) AS outflows,
            SUM(CASE WHEN flow_direction = 'INTERNAL' THEN amount ELSE 0 END) AS internal,
            SUM(CASE WHEN is_leakage = TRUE THEN amount ELSE 0 END) AS leakage
        FROM economic_flows
        WHERE (from_geo_id = p_geo_id OR to_geo_id = p_geo_id)
          AND flow_timestamp BETWEEN p_start_date AND p_end_date
    )
    SELECT
        flows.inflows,
        flows.outflows,
        flows.internal,
        flows.leakage,
        CASE WHEN (flows.inflows + flows.internal) > 0
             THEN (flows.leakage / (flows.inflows + flows.internal) * 100)
             ELSE 0
        END,
        CASE WHEN flows.outflows > 0
             THEN (flows.internal / flows.outflows)
             ELSE 0
        END
    FROM flows;
END;
$$ LANGUAGE plpgsql;

-- Find investment opportunities
CREATE OR REPLACE FUNCTION find_investment_opportunities()
RETURNS TABLE(
    opportunity TEXT,
    service_category VARCHAR,
    current_leakage DECIMAL,
    local_providers INTEGER,
    estimated_investment DECIMAL,
    potential_jobs INTEGER,
    community_priority_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH service_demand AS (
        SELECT
            s.service_category,
            SUM(ef.amount) AS external_spending,
            COUNT(DISTINCT CASE WHEN e.is_local THEN e.entity_id END) AS local_count,
            AVG(ci.priority_score) AS community_priority
        FROM services s
        LEFT JOIN entities e ON s.entity_id = e.entity_id
        LEFT JOIN economic_flows ef ON ef.payee_entity_id = e.entity_id AND ef.is_leakage = TRUE
        LEFT JOIN community_interviews ci ON ci.themes && ARRAY[s.service_category]
        GROUP BY s.service_category
        HAVING SUM(ef.amount) > 100000 AND COUNT(DISTINCT CASE WHEN e.is_local THEN e.entity_id END) < 3
    )
    SELECT
        'Develop local ' || sd.service_category || ' capacity',
        sd.service_category,
        sd.external_spending,
        sd.local_count,
        (3 - sd.local_count) * 100000, -- $100k per provider
        (3 - sd.local_count), -- 1 job per provider
        COALESCE(sd.community_priority, 0.5)
    FROM service_demand sd
    ORDER BY sd.external_spending * COALESCE(sd.community_priority, 0.5) DESC;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- SAMPLE DATA POPULATION
-- =====================================================

-- Add data sources
INSERT INTO data_sources (source_name, source_type, source_url, update_frequency) VALUES
('Mount Isa Service Map', 'DATABASE', 'https://github.com/Acurioustractor/mount-isa-service-map', 'WEEKLY'),
('ABS CABEE', 'API', 'https://www.abs.gov.au/statistics/economy/business-indicators/counts-australian-businesses', 'QUARTERLY'),
('ACNC Charity Register', 'API', 'https://www.acnc.gov.au/charity', 'MONTHLY'),
('Queensland Youth Justice Grants', 'WEB_SCRAPE', 'https://www.youthjustice.qld.gov.au/partnerships/grants/', 'WEEKLY'),
('GrantConnect', 'WEB_SCRAPE', 'https://www.grants.gov.au/', 'DAILY'),
('Queensland Open Data', 'API', 'https://www.data.qld.gov.au/', 'WEEKLY'),
('Community Interviews', 'MANUAL', NULL, 'ONGOING');

COMMIT;
