-- Mount Isa Economic Observatory Database Schema
-- Tracks money flows, entities, and economic leakages

-- Enable PostGIS for geospatial operations
CREATE EXTENSION IF NOT EXISTS postgis;

-- =====================================================
-- DIMENSION TABLES
-- =====================================================

-- Geographic Regions (SA2, LGA, Postcodes)
CREATE TABLE dim_geography (
    geo_id SERIAL PRIMARY KEY,
    geo_type VARCHAR(20) NOT NULL, -- 'LGA', 'SA2', 'SA3', 'POSTCODE'
    geo_code VARCHAR(20) NOT NULL,
    geo_name VARCHAR(200) NOT NULL,
    state VARCHAR(3),
    asgs_edition VARCHAR(10),
    boundary GEOMETRY(MULTIPOLYGON, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(geo_type, geo_code, asgs_edition)
);

CREATE INDEX idx_geo_code ON dim_geography(geo_code);
CREATE INDEX idx_geo_type ON dim_geography(geo_type);
CREATE INDEX idx_geo_boundary ON dim_geography USING GIST(boundary);

-- Date Dimension
CREATE TABLE dim_date (
    date_id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20),
    financial_year VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_date ON dim_date(date);
CREATE INDEX idx_year_quarter ON dim_date(year, quarter);

-- Industry Classification (ANZSIC)
CREATE TABLE dim_industry (
    industry_id SERIAL PRIMARY KEY,
    anzsic_code VARCHAR(10) NOT NULL UNIQUE,
    anzsic_title VARCHAR(500) NOT NULL,
    division_code VARCHAR(5),
    division_title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_anzsic_code ON dim_industry(anzsic_code);

-- Program/Service Types (e.g., MBS groups, PBS ATC codes)
CREATE TABLE dim_program (
    program_id SERIAL PRIMARY KEY,
    program_type VARCHAR(50) NOT NULL, -- 'MBS', 'PBS', 'DSS', 'PROCUREMENT', etc.
    program_code VARCHAR(50),
    program_name VARCHAR(500) NOT NULL,
    program_category VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_program_type ON dim_program(program_type);
CREATE INDEX idx_program_code ON dim_program(program_code);

-- Entity Types (Government/Business/Household/Charity)
CREATE TABLE dim_entity_type (
    entity_type_id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL UNIQUE, -- 'COMMONWEALTH', 'STATE', 'LGA', 'LOCAL_BUSINESS', 'EXTERNAL_BUSINESS', 'HOUSEHOLD', 'CHARITY'
    entity_category VARCHAR(50), -- 'GOVERNMENT', 'BUSINESS', 'COMMUNITY'
    is_local BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ENTITY TABLES (for Entity Resolution)
-- =====================================================

-- Master Entity Table (ABN/ACN Registry)
CREATE TABLE entities (
    entity_id SERIAL PRIMARY KEY,
    abn VARCHAR(11),
    acn VARCHAR(9),
    entity_name VARCHAR(500) NOT NULL,
    entity_type_id INTEGER REFERENCES dim_entity_type(entity_type_id),
    trading_name VARCHAR(500),
    legal_name VARCHAR(500),
    main_business_location VARCHAR(200),
    postcode VARCHAR(4),
    state VARCHAR(3),
    is_local BOOLEAN, -- Based on geo matching
    geo_id INTEGER REFERENCES dim_geography(geo_id),
    primary_anzsic VARCHAR(10) REFERENCES dim_industry(anzsic_code),
    status VARCHAR(50), -- 'ACTIVE', 'CANCELLED', etc.
    gst_registered BOOLEAN,
    entity_source VARCHAR(50), -- 'ABN_LOOKUP', 'ASIC', 'ACNC', 'MANUAL'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_abn ON entities(abn);
CREATE INDEX idx_acn ON entities(acn);
CREATE INDEX idx_entity_name ON entities(entity_name);
CREATE INDEX idx_is_local ON entities(is_local);
CREATE INDEX idx_postcode ON entities(postcode);

-- Address Geocoding (G-NAF)
CREATE TABLE addresses (
    address_id SERIAL PRIMARY KEY,
    gnaf_pid VARCHAR(50) UNIQUE,
    address_string VARCHAR(500) NOT NULL,
    street_number VARCHAR(20),
    street_name VARCHAR(200),
    suburb VARCHAR(100),
    postcode VARCHAR(4),
    state VARCHAR(3),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    location GEOMETRY(POINT, 4326),
    geo_id INTEGER REFERENCES dim_geography(geo_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_address_postcode ON addresses(postcode);
CREATE INDEX idx_address_location ON addresses USING GIST(location);

-- =====================================================
-- FACT TABLES (Economic Flows)
-- =====================================================

-- Main Economic Flow Table
CREATE TABLE fact_economic_flows (
    flow_id BIGSERIAL PRIMARY KEY,
    date_id INTEGER REFERENCES dim_date(date_id),

    -- Geographic dimensions
    from_geo_id INTEGER REFERENCES dim_geography(geo_id),
    to_geo_id INTEGER REFERENCES dim_geography(geo_id),

    -- Entity dimensions (who paid, who received)
    payer_entity_id INTEGER REFERENCES entities(entity_id),
    payee_entity_id INTEGER REFERENCES entities(entity_id),
    payer_type_id INTEGER REFERENCES dim_entity_type(entity_type_id),
    payee_type_id INTEGER REFERENCES dim_entity_type(entity_type_id),

    -- Classification dimensions
    industry_id INTEGER REFERENCES dim_industry(industry_id),
    program_id INTEGER REFERENCES dim_program(program_id),

    -- Flow characteristics
    amount DECIMAL(15, 2) NOT NULL,
    count INTEGER DEFAULT 1,
    flow_direction VARCHAR(20), -- 'INFLOW', 'OUTFLOW', 'INTERNAL'
    is_leakage BOOLEAN, -- TRUE if money left local economy

    -- Source metadata
    source_system VARCHAR(100) NOT NULL, -- 'MBS', 'PBS', 'AUSTENDER', etc.
    source_record_id VARCHAR(200),
    confidence_score DECIMAL(3, 2), -- 0.00 to 1.00

    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_flow_date ON fact_economic_flows(date_id);
CREATE INDEX idx_flow_from_geo ON fact_economic_flows(from_geo_id);
CREATE INDEX idx_flow_to_geo ON fact_economic_flows(to_geo_id);
CREATE INDEX idx_flow_direction ON fact_economic_flows(flow_direction);
CREATE INDEX idx_flow_leakage ON fact_economic_flows(is_leakage);
CREATE INDEX idx_flow_source ON fact_economic_flows(source_system);

-- =====================================================
-- SOURCE-SPECIFIC STAGING TABLES
-- =====================================================

-- MBS (Medicare Benefits Schedule) Data
CREATE TABLE staging_mbs (
    id SERIAL PRIMARY KEY,
    service_date DATE,
    lga_code VARCHAR(20),
    mbs_item_code VARCHAR(20),
    service_group VARCHAR(200),
    service_description TEXT,
    service_count INTEGER,
    benefits_paid DECIMAL(15, 2),
    source_file VARCHAR(500),
    fetch_timestamp TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- PBS (Pharmaceutical Benefits Scheme) Data
CREATE TABLE staging_pbs (
    id SERIAL PRIMARY KEY,
    service_date DATE,
    lga_code VARCHAR(20),
    atc_code VARCHAR(20),
    drug_name VARCHAR(200),
    prescription_count INTEGER,
    benefits_paid DECIMAL(15, 2),
    source_file VARCHAR(500),
    fetch_timestamp TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- AusTender (Commonwealth Procurement)
CREATE TABLE staging_austender (
    id SERIAL PRIMARY KEY,
    cn_id VARCHAR(50) UNIQUE, -- Contract Notice ID
    publish_date DATE,
    contract_value DECIMAL(15, 2),
    supplier_abn VARCHAR(11),
    supplier_name VARCHAR(500),
    supplier_postcode VARCHAR(4),
    buyer_name VARCHAR(500),
    contract_description TEXT,
    source_url VARCHAR(500),
    fetch_timestamp TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- Queensland Government Procurement
CREATE TABLE staging_qld_procurement (
    id SERIAL PRIMARY KEY,
    contract_id VARCHAR(100),
    publish_date DATE,
    contract_value DECIMAL(15, 2),
    supplier_name VARCHAR(500),
    supplier_location VARCHAR(200),
    agency_name VARCHAR(500),
    category VARCHAR(200),
    description TEXT,
    source_dataset VARCHAR(100), -- 'FPP' or 'AWARDED'
    fetch_timestamp TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- DSS Payment Demographics
CREATE TABLE staging_dss_payments (
    id SERIAL PRIMARY KEY,
    quarter_date DATE,
    geo_code VARCHAR(20),
    geo_type VARCHAR(20), -- 'LGA' or 'SA2'
    payment_type VARCHAR(100), -- 'JobSeeker', 'Age Pension', etc.
    recipient_count INTEGER,
    total_amount DECIMAL(15, 2),
    source_file VARCHAR(500),
    fetch_timestamp TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- ABS Business Counts (CABEE)
CREATE TABLE staging_abs_businesses (
    id SERIAL PRIMARY KEY,
    reference_date DATE,
    lga_code VARCHAR(20),
    anzsic_code VARCHAR(10),
    business_count INTEGER,
    source_file VARCHAR(500),
    fetch_timestamp TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- ATO Taxation Statistics
CREATE TABLE staging_ato_taxstats (
    id SERIAL PRIMARY KEY,
    financial_year VARCHAR(10),
    postcode VARCHAR(4),
    individuals_count INTEGER,
    total_income DECIMAL(15, 2),
    median_income DECIMAL(15, 2),
    total_deductions DECIMAL(15, 2),
    source_file VARCHAR(500),
    fetch_timestamp TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- BITRE Aviation Data
CREATE TABLE staging_bitre_aviation (
    id SERIAL PRIMARY KEY,
    month_date DATE,
    airport_code VARCHAR(10),
    airport_name VARCHAR(200),
    passenger_count INTEGER,
    aircraft_movements INTEGER,
    route_type VARCHAR(50), -- 'DOMESTIC', 'INTERNATIONAL', 'CHARTER'
    source_file VARCHAR(500),
    fetch_timestamp TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- ACNC Charity Register
CREATE TABLE staging_acnc_charities (
    id SERIAL PRIMARY KEY,
    abn VARCHAR(11),
    charity_name VARCHAR(500),
    charity_type VARCHAR(200),
    operating_state VARCHAR(3),
    postcode VARCHAR(4),
    total_revenue DECIMAL(15, 2),
    total_expenses DECIMAL(15, 2),
    reporting_year INTEGER,
    source_file VARCHAR(500),
    fetch_timestamp TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- =====================================================
-- LEAKAGE ANALYSIS VIEWS
-- =====================================================

-- View: Total Leakages by Category
CREATE VIEW vw_leakages_by_category AS
SELECT
    d.year,
    d.quarter,
    p.program_type,
    i.division_title AS industry,
    SUM(f.amount) AS total_leakage,
    COUNT(f.flow_id) AS transaction_count
FROM fact_economic_flows f
JOIN dim_date d ON f.date_id = d.date_id
LEFT JOIN dim_program p ON f.program_id = p.program_id
LEFT JOIN dim_industry i ON f.industry_id = i.industry_id
WHERE f.is_leakage = TRUE
GROUP BY d.year, d.quarter, p.program_type, i.division_title;

-- View: Local vs External Spending
CREATE VIEW vw_local_vs_external AS
SELECT
    d.year,
    d.quarter,
    et.entity_type,
    SUM(CASE WHEN f.is_leakage = FALSE THEN f.amount ELSE 0 END) AS local_spending,
    SUM(CASE WHEN f.is_leakage = TRUE THEN f.amount ELSE 0 END) AS external_spending,
    COUNT(CASE WHEN f.is_leakage = FALSE THEN 1 END) AS local_transactions,
    COUNT(CASE WHEN f.is_leakage = TRUE THEN 1 END) AS external_transactions
FROM fact_economic_flows f
JOIN dim_date d ON f.date_id = d.date_id
LEFT JOIN dim_entity_type et ON f.payee_type_id = et.entity_type_id
GROUP BY d.year, d.quarter, et.entity_type;

-- View: Service Capacity Gaps (High demand, low local supply)
CREATE VIEW vw_service_gaps AS
SELECT
    i.anzsic_code,
    i.anzsic_title,
    SUM(f.amount) AS external_spending,
    COUNT(DISTINCT pe.entity_id) AS local_provider_count,
    SUM(f.amount) / NULLIF(COUNT(DISTINCT pe.entity_id), 0) AS spending_per_provider
FROM fact_economic_flows f
JOIN dim_industry i ON f.industry_id = i.industry_id
LEFT JOIN entities pe ON pe.is_local = TRUE AND pe.primary_anzsic = i.anzsic_code
WHERE f.is_leakage = TRUE
GROUP BY i.anzsic_code, i.anzsic_title
ORDER BY external_spending DESC;

-- =====================================================
-- AUDIT & PROVENANCE TABLES
-- =====================================================

-- Data Source Provenance
CREATE TABLE data_provenance (
    provenance_id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_url VARCHAR(500),
    fetch_timestamp TIMESTAMP NOT NULL,
    record_count INTEGER,
    file_hash VARCHAR(64), -- SHA-256
    licence VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Validation Test Results
CREATE TABLE validation_results (
    validation_id SERIAL PRIMARY KEY,
    test_name VARCHAR(200) NOT NULL,
    test_type VARCHAR(50), -- 'SCHEMA', 'RANGE', 'CONSISTENCY', 'GEOGRAPHY'
    test_date TIMESTAMP NOT NULL,
    passed BOOLEAN NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Change Log for ASGS Updates
CREATE TABLE asgs_change_log (
    change_id SERIAL PRIMARY KEY,
    change_date DATE NOT NULL,
    old_asgs_edition VARCHAR(10),
    new_asgs_edition VARCHAR(10),
    affected_areas TEXT[],
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INITIAL DATA - Mount Isa Geography
-- =====================================================

INSERT INTO dim_geography (geo_type, geo_code, geo_name, state, asgs_edition)
VALUES
    ('LGA', 'LGA35300', 'Mount Isa (C)', 'QLD', '2021'),
    ('POSTCODE', '4825', 'Mount Isa', 'QLD', '2021');

-- Entity Types
INSERT INTO dim_entity_type (entity_type, entity_category, is_local) VALUES
    ('COMMONWEALTH', 'GOVERNMENT', FALSE),
    ('STATE_QLD', 'GOVERNMENT', FALSE),
    ('LGA_MOUNT_ISA', 'GOVERNMENT', TRUE),
    ('LOCAL_BUSINESS', 'BUSINESS', TRUE),
    ('EXTERNAL_BUSINESS', 'BUSINESS', FALSE),
    ('LOCAL_HOUSEHOLD', 'HOUSEHOLD', TRUE),
    ('LOCAL_CHARITY', 'COMMUNITY', TRUE),
    ('EXTERNAL_CHARITY', 'COMMUNITY', FALSE);

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Function to determine if entity is local based on geography
CREATE OR REPLACE FUNCTION is_entity_local(p_postcode VARCHAR, p_geo_id INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if postcode matches Mount Isa or if geo_id is within Mount Isa LGA
    RETURN (p_postcode = '4825' OR
            p_geo_id IN (SELECT geo_id FROM dim_geography WHERE geo_code IN ('LGA35300', '4825')));
END;
$$ LANGUAGE plpgsql;

-- Function to classify flow direction
CREATE OR REPLACE FUNCTION classify_flow_direction(from_local BOOLEAN, to_local BOOLEAN)
RETURNS VARCHAR AS $$
BEGIN
    IF from_local AND to_local THEN
        RETURN 'INTERNAL';
    ELSIF from_local AND NOT to_local THEN
        RETURN 'OUTFLOW';
    ELSIF NOT from_local AND to_local THEN
        RETURN 'INFLOW';
    ELSE
        RETURN 'EXTERNAL';
    END IF;
END;
$$ LANGUAGE plpgsql;
