-- ============================================================================
-- MOUNT ISA ECONOMIC OBSERVATORY - Supabase Schema
-- ============================================================================
-- Comprehensive database schema for tracking funding flows from announcement
-- to allocation to payment to outcome
--
-- Design Principles:
-- 1. Track complete money flow: announcement → budget → payment → outcome
-- 2. Maintain data provenance (source documents, confidence scores)
-- 3. Enable cross-community comparisons (Mount Isa, Doomadgee, etc.)
-- 4. Support visualization (Sankey diagrams, timelines, maps)
-- 5. Allow for data uncertainty (confidence scoring, verification status)
--
-- Created: 2025-11-14
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable PostGIS for geographic data
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- REFERENCE TABLES: Core entities and classifications
-- ============================================================================

-- Locations: Communities where programs operate
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    state VARCHAR(3) NOT NULL,
    lga VARCHAR(100), -- Local Government Area
    indigenous_region VARCHAR(100),
    population INTEGER,
    remoteness_category VARCHAR(50), -- Very Remote, Remote, Outer Regional, etc.
    coordinates GEOGRAPHY(POINT, 4326), -- PostGIS point for mapping
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, state)
);

-- Organizations: All entities involved in funding (government, NGOs, businesses)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    abn VARCHAR(11),
    acn VARCHAR(9),
    organization_type VARCHAR(50) NOT NULL, -- Government, NGO, Indigenous Corporation, Business, etc.
    sector VARCHAR(50), -- Youth Justice, Health, Education, etc.
    indigenous_controlled BOOLEAN DEFAULT FALSE,
    primary_location_id UUID REFERENCES locations(id),
    contact_email VARCHAR(100),
    contact_phone VARCHAR(20),
    website_url TEXT,
    description TEXT,

    -- Financial data (from ACNC, annual reports)
    annual_revenue DECIMAL(15,2),
    annual_revenue_year INTEGER,
    employee_count INTEGER,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(abn)
);

-- Programs: Specific initiatives and services
CREATE TABLE programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    program_type VARCHAR(50) NOT NULL, -- On-Country, Co-responder, Diversionary, etc.
    sector VARCHAR(50) NOT NULL, -- Youth Justice, Education, Health, etc.
    description TEXT,
    target_cohort TEXT, -- Young people, families, etc.
    delivery_model TEXT, -- Residential, outreach, case management, etc.

    -- Program scope
    is_statewide BOOLEAN DEFAULT FALSE,
    target_locations UUID[], -- Array of location IDs

    -- Metadata
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active', -- active, completed, planned
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document sources: All source materials
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_type VARCHAR(50) NOT NULL, -- Media Statement, Budget Paper, Annual Report, Contract, etc.
    title TEXT NOT NULL,
    publication_date DATE,
    source_url TEXT,
    source_file_path TEXT,
    document_identifier VARCHAR(100), -- Statement ID, contract number, etc.

    -- Content
    full_text TEXT,
    summary TEXT,
    key_findings TEXT[],

    -- Provenance
    publisher_org_id UUID REFERENCES organizations(id),
    author TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(document_type, document_identifier)
);

-- ============================================================================
-- FUNDING FLOW TABLES: Track money from announcement to outcome
-- ============================================================================

-- Stage 1: Funding Announcements (from media statements, press releases)
CREATE TABLE funding_announcements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- What was announced
    program_id UUID REFERENCES programs(id),
    recipient_org_id UUID REFERENCES organizations(id),
    funding_body_id UUID REFERENCES organizations(id) NOT NULL, -- Who's providing the money

    amount_announced DECIMAL(15,2) NOT NULL,
    amount_currency VARCHAR(3) DEFAULT 'AUD',
    funding_period_start DATE,
    funding_period_end DATE,
    funding_period_description VARCHAR(100), -- "Over 3 years", "2023-24", etc.

    -- Context
    announcement_date DATE NOT NULL,
    announced_by VARCHAR(100), -- Minister name
    announcement_context TEXT, -- Political/policy context

    -- Classification
    funding_type VARCHAR(50), -- Capital, Operating, Grant, etc.
    conditions TEXT, -- Any conditions attached to funding

    -- Geographic scope
    target_locations UUID[], -- Array of location IDs
    is_mount_isa_specific BOOLEAN DEFAULT FALSE,
    mount_isa_allocation DECIMAL(15,2), -- If statewide, what portion goes to Mount Isa

    -- Provenance
    source_document_id UUID REFERENCES documents(id) NOT NULL,
    confidence_score INTEGER CHECK (confidence_score BETWEEN 1 AND 5), -- 1=low, 5=high
    verification_status VARCHAR(20) DEFAULT 'unverified', -- unverified, verified, disputed
    verified_by VARCHAR(100),
    verified_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Stage 2: Budget Allocations (from budget papers, portfolio budgets)
CREATE TABLE budget_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Link to announcement
    announcement_id UUID REFERENCES funding_announcements(id), -- May be null if no prior announcement

    -- Budget details
    program_id UUID REFERENCES programs(id),
    recipient_org_id UUID REFERENCES organizations(id),
    funding_body_id UUID REFERENCES organizations(id) NOT NULL,

    amount_allocated DECIMAL(15,2) NOT NULL,
    financial_year VARCHAR(7) NOT NULL, -- "2023-24"
    budget_line_item VARCHAR(200),
    budget_measure_name TEXT,

    -- Classification
    allocation_type VARCHAR(50), -- New, Continuing, One-off, etc.

    -- Provenance
    source_document_id UUID REFERENCES documents(id) NOT NULL,
    confidence_score INTEGER CHECK (confidence_score BETWEEN 1 AND 5),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Stage 3: Actual Payments (from contracts, financial reports, FOI data)
CREATE TABLE actual_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Link to upstream
    announcement_id UUID REFERENCES funding_announcements(id),
    allocation_id UUID REFERENCES budget_allocations(id),

    -- Payment details
    program_id UUID REFERENCES programs(id),
    payer_org_id UUID REFERENCES organizations(id) NOT NULL,
    payee_org_id UUID REFERENCES organizations(id) NOT NULL,

    amount_paid DECIMAL(15,2) NOT NULL,
    payment_date DATE,
    payment_period_start DATE,
    payment_period_end DATE,
    financial_year VARCHAR(7),

    -- Payment mechanism
    payment_type VARCHAR(50), -- Contract, Grant, Service Agreement, etc.
    contract_number VARCHAR(100),
    purchase_order VARCHAR(100),
    invoice_number VARCHAR(100),

    -- Purpose
    payment_description TEXT,
    service_delivered TEXT,

    -- Provenance
    source_document_id UUID REFERENCES documents(id),
    confidence_score INTEGER CHECK (confidence_score BETWEEN 1 AND 5),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Stage 4: Program Outcomes (from annual reports, evaluation reports)
CREATE TABLE program_outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Link to program and funding
    program_id UUID REFERENCES programs(id) NOT NULL,
    location_id UUID REFERENCES locations(id),
    funding_announcement_id UUID REFERENCES funding_announcements(id),

    -- Outcome measurement
    outcome_category VARCHAR(50) NOT NULL, -- Participation, Offending, Education, Employment, etc.
    metric_name VARCHAR(100) NOT NULL,
    metric_description TEXT,

    -- Values
    metric_value DECIMAL(15,4),
    metric_unit VARCHAR(50), -- Percentage, Count, Rate, etc.
    baseline_value DECIMAL(15,4),
    target_value DECIMAL(15,4),

    -- Time period
    measurement_date DATE,
    measurement_period_start DATE,
    measurement_period_end DATE,

    -- Context
    cohort_size INTEGER, -- Number of participants
    cohort_description TEXT,

    -- Quality
    measurement_method TEXT,
    confidence_level VARCHAR(20), -- High, Medium, Low

    -- Provenance
    source_document_id UUID REFERENCES documents(id),
    reported_by_org_id UUID REFERENCES organizations(id),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- LINKING TABLES: Many-to-many relationships
-- ============================================================================

-- Program locations (many programs can operate in many locations)
CREATE TABLE program_locations (
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,
    start_date DATE,
    end_date DATE,
    PRIMARY KEY (program_id, location_id)
);

-- Program delivery organizations (many organizations can deliver many programs)
CREATE TABLE program_deliverers (
    program_id UUID REFERENCES programs(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50), -- Lead, Partner, Subcontractor, etc.
    start_date DATE,
    end_date DATE,
    PRIMARY KEY (program_id, organization_id)
);

-- ============================================================================
-- INDEXES: Optimize common queries
-- ============================================================================

-- Funding announcements indexes
CREATE INDEX idx_funding_announcements_program ON funding_announcements(program_id);
CREATE INDEX idx_funding_announcements_recipient ON funding_announcements(recipient_org_id);
CREATE INDEX idx_funding_announcements_funder ON funding_announcements(funding_body_id);
CREATE INDEX idx_funding_announcements_date ON funding_announcements(announcement_date);
CREATE INDEX idx_funding_announcements_mount_isa ON funding_announcements(is_mount_isa_specific);
CREATE INDEX idx_funding_announcements_amount ON funding_announcements(amount_announced);

-- Budget allocations indexes
CREATE INDEX idx_budget_allocations_program ON budget_allocations(program_id);
CREATE INDEX idx_budget_allocations_year ON budget_allocations(financial_year);
CREATE INDEX idx_budget_allocations_announcement ON budget_allocations(announcement_id);

-- Actual payments indexes
CREATE INDEX idx_actual_payments_program ON actual_payments(program_id);
CREATE INDEX idx_actual_payments_payer ON actual_payments(payer_org_id);
CREATE INDEX idx_actual_payments_payee ON actual_payments(payee_org_id);
CREATE INDEX idx_actual_payments_date ON actual_payments(payment_date);
CREATE INDEX idx_actual_payments_year ON actual_payments(financial_year);

-- Program outcomes indexes
CREATE INDEX idx_program_outcomes_program ON program_outcomes(program_id);
CREATE INDEX idx_program_outcomes_location ON program_outcomes(location_id);
CREATE INDEX idx_program_outcomes_category ON program_outcomes(outcome_category);

-- Organizations indexes
CREATE INDEX idx_organizations_type ON organizations(organization_type);
CREATE INDEX idx_organizations_sector ON organizations(sector);
CREATE INDEX idx_organizations_abn ON organizations(abn);
CREATE INDEX idx_organizations_indigenous ON organizations(indigenous_controlled);

-- Documents indexes
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_date ON documents(publication_date);

-- Geographic index
CREATE INDEX idx_locations_coords ON locations USING GIST(coordinates);

-- ============================================================================
-- VIEWS: Simplified access to common queries
-- ============================================================================

-- View: Complete funding flow for each announcement
CREATE VIEW v_funding_flow AS
SELECT
    fa.id as announcement_id,
    fa.announcement_date,
    p.name as program_name,
    p.sector,
    l.name as location_name,

    -- Organizations
    funder.name as funding_body,
    recipient.name as recipient_organization,

    -- Amounts
    fa.amount_announced,
    fa.funding_period_description,
    COALESCE(SUM(ba.amount_allocated), 0) as total_allocated,
    COALESCE(SUM(ap.amount_paid), 0) as total_paid,

    -- Variance analysis
    fa.amount_announced - COALESCE(SUM(ba.amount_allocated), 0) as announcement_vs_allocation_gap,
    COALESCE(SUM(ba.amount_allocated), 0) - COALESCE(SUM(ap.amount_paid), 0) as allocation_vs_payment_gap,

    -- Provenance
    fa.confidence_score,
    fa.verification_status,
    d.title as source_document_title,
    d.source_url

FROM funding_announcements fa
LEFT JOIN programs p ON fa.program_id = p.id
LEFT JOIN organizations funder ON fa.funding_body_id = funder.id
LEFT JOIN organizations recipient ON fa.recipient_org_id = recipient.id
LEFT JOIN documents d ON fa.source_document_id = d.id
LEFT JOIN budget_allocations ba ON fa.id = ba.announcement_id
LEFT JOIN actual_payments ap ON fa.id = ap.announcement_id
LEFT JOIN UNNEST(fa.target_locations) AS loc_id ON TRUE
LEFT JOIN locations l ON l.id = loc_id

GROUP BY
    fa.id, fa.announcement_date, p.name, p.sector, l.name,
    funder.name, recipient.name, fa.amount_announced,
    fa.funding_period_description, fa.confidence_score,
    fa.verification_status, d.title, d.source_url;

-- View: Mount Isa specific funding
CREATE VIEW v_mount_isa_funding AS
SELECT
    fa.announcement_date,
    p.name as program_name,
    p.sector,
    recipient.name as recipient,
    CASE
        WHEN fa.is_mount_isa_specific THEN fa.amount_announced
        ELSE fa.mount_isa_allocation
    END as mount_isa_amount,
    fa.funding_period_description,
    d.title as source,
    d.source_url
FROM funding_announcements fa
LEFT JOIN programs p ON fa.program_id = p.id
LEFT JOIN organizations recipient ON fa.recipient_org_id = recipient.id
LEFT JOIN documents d ON fa.source_document_id = d.id
WHERE fa.is_mount_isa_specific = TRUE
   OR fa.mount_isa_allocation IS NOT NULL
ORDER BY fa.announcement_date DESC;

-- View: Program outcomes summary
CREATE VIEW v_program_outcomes_summary AS
SELECT
    p.name as program_name,
    l.name as location_name,
    po.outcome_category,
    COUNT(*) as metric_count,
    AVG(CASE
        WHEN po.target_value > 0
        THEN (po.metric_value / po.target_value) * 100
        ELSE NULL
    END) as avg_target_achievement_pct
FROM program_outcomes po
JOIN programs p ON po.program_id = p.id
LEFT JOIN locations l ON po.location_id = l.id
GROUP BY p.name, l.name, po.outcome_category;

-- ============================================================================
-- FUNCTIONS: Useful database functions
-- ============================================================================

-- Function: Calculate funding efficiency (outcomes per dollar)
CREATE OR REPLACE FUNCTION calculate_funding_efficiency(
    p_program_id UUID,
    p_location_id UUID DEFAULT NULL
)
RETURNS TABLE (
    total_funding DECIMAL(15,2),
    total_outcomes INTEGER,
    efficiency_score DECIMAL(10,4)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        SUM(fa.amount_announced) as total_funding,
        COUNT(DISTINCT po.id) as total_outcomes,
        COUNT(DISTINCT po.id)::DECIMAL / NULLIF(SUM(fa.amount_announced), 0) * 1000000 as efficiency_score
    FROM funding_announcements fa
    LEFT JOIN program_outcomes po ON fa.program_id = po.program_id
    WHERE fa.program_id = p_program_id
      AND (p_location_id IS NULL OR po.location_id = p_location_id);
END;
$$ LANGUAGE plpgsql;

-- Function: Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update timestamp trigger to all tables
CREATE TRIGGER update_locations_updated_at BEFORE UPDATE ON locations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_programs_updated_at BEFORE UPDATE ON programs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_funding_announcements_updated_at BEFORE UPDATE ON funding_announcements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_budget_allocations_updated_at BEFORE UPDATE ON budget_allocations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_actual_payments_updated_at BEFORE UPDATE ON actual_payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_program_outcomes_updated_at BEFORE UPDATE ON program_outcomes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS): Enable when ready for multi-tenant access
-- ============================================================================

-- Placeholder for RLS policies (enable when building public dashboard)
-- ALTER TABLE funding_announcements ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Public read access" ON funding_announcements FOR SELECT USING (true);

-- ============================================================================
-- INITIAL SEED DATA
-- ============================================================================

-- Insert Mount Isa location
INSERT INTO locations (name, state, lga, remoteness_category, population, coordinates)
VALUES (
    'Mount Isa',
    'QLD',
    'Mount Isa City Council',
    'Very Remote',
    18342,
    ST_SetSRID(ST_MakePoint(139.4927, -20.7256), 4326)
) ON CONFLICT (name, state) DO NOTHING;

-- Insert Queensland Government organization
INSERT INTO organizations (name, organization_type, sector)
VALUES (
    'Queensland Government',
    'Government',
    'Government'
) ON CONFLICT (abn) DO NOTHING;

-- Insert Department of Youth Justice
INSERT INTO organizations (name, organization_type, sector)
VALUES (
    'Department of Youth Justice, Employment, Small Business and Training',
    'Government',
    'Youth Justice'
) ON CONFLICT (abn) DO NOTHING;

-- Insert Queensland Police Service
INSERT INTO organizations (name, abn, organization_type, sector)
VALUES (
    'Queensland Police Service',
    NULL,
    'Government',
    'Police'
) ON CONFLICT (abn) DO NOTHING;

-- ============================================================================
-- NOTES
-- ============================================================================
--
-- Next steps:
-- 1. Run this schema in Supabase SQL editor
-- 2. Load CSV data using Python scripts
-- 3. Build visualizations using the views
-- 4. Add RLS policies for public access
-- 5. Integrate with Next.js frontend
--
-- Data quality notes:
-- - confidence_score: Use 5 for verified payments, 4 for official budgets,
--   3 for media statements, 2 for estimates, 1 for unverified claims
-- - verification_status: Update as data is cross-referenced with multiple sources
-- - Always link to source_document_id for provenance
--
-- ============================================================================
