-- ============================================================================
-- BENCHMARK & OUTCOMES DATA SCHEMA
-- ============================================================================
-- Stores performance benchmarks, cost-effectiveness data, and outcome metrics
-- from sources like Productivity Commission, academic research, evaluations
--
-- Use case:
-- - Compare Mount Isa programs to state/national averages
-- - Track cost-effectiveness ($ per outcome)
-- - Evidence base for policy decisions
-- - Show what works (evidence-based practice)
--
-- Run after: supabase_schema.sql
-- ============================================================================

-- ============================================================================
-- BENCHMARK DATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS benchmark_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- What is being measured
    metric_name VARCHAR(200) NOT NULL,
    metric_category VARCHAR(100),  -- 'cost', 'outcome', 'service_delivery', 'population'

    -- The value
    metric_value NUMERIC,
    metric_unit VARCHAR(50),  -- 'dollars', 'percentage', 'days', 'count', 'rate'

    -- Context
    jurisdiction VARCHAR(100),  -- 'Queensland', 'National', 'Mount Isa', 'NSW', etc.
    demographic_group VARCHAR(100),  -- 'Indigenous', 'All youth', 'Serious repeat offenders'
    time_period VARCHAR(50),  -- '2023-24', 'Q2 2024', '2020-2025'

    -- Source
    source_type VARCHAR(100),  -- 'Productivity Commission RoGS', 'Academic Study', 'Government Report'
    source_document_id UUID REFERENCES documents(id),
    source_url TEXT,
    collection_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Quality
    data_quality VARCHAR(50),  -- 'high', 'medium', 'low', 'estimated'
    notes TEXT,

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_benchmark_metric_name ON benchmark_data(metric_name);
CREATE INDEX idx_benchmark_jurisdiction ON benchmark_data(jurisdiction);
CREATE INDEX idx_benchmark_category ON benchmark_data(metric_category);
CREATE INDEX idx_benchmark_time_period ON benchmark_data(time_period);

-- Comments
COMMENT ON TABLE benchmark_data IS 'Performance benchmarks and outcome metrics from government reports, research, and evaluations';
COMMENT ON COLUMN benchmark_data.metric_name IS 'Name of the metric (e.g., "Average cost per day in detention", "Youth recidivism rate")';
COMMENT ON COLUMN benchmark_data.jurisdiction IS 'Geographic or administrative area (state, region, community)';
COMMENT ON COLUMN benchmark_data.demographic_group IS 'Population subgroup for the metric';

-- ============================================================================
-- COST EFFECTIVENESS DATA
-- ============================================================================

CREATE TABLE IF NOT EXISTS cost_effectiveness (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Program/Intervention
    program_id UUID REFERENCES programs(id),
    intervention_name VARCHAR(200) NOT NULL,
    intervention_type VARCHAR(100),  -- 'prevention', 'diversion', 'rehabilitation', 'detention'

    -- Costs
    total_cost NUMERIC,
    cost_per_participant NUMERIC,
    cost_per_outcome NUMERIC,  -- e.g., cost per recidivism reduction

    -- Outcomes
    outcome_metric VARCHAR(200),  -- 'Recidivism reduction', 'School completion', 'Employment'
    outcome_value NUMERIC,
    outcome_unit VARCHAR(50),  -- 'percentage', 'count', 'rate'

    -- Comparison
    jurisdiction VARCHAR(100),
    comparator_program VARCHAR(200),  -- What it's being compared to
    cost_benefit_ratio NUMERIC,  -- Benefit per dollar spent

    -- Source
    study_name TEXT,
    study_year INTEGER,
    source_document_id UUID REFERENCES documents(id),
    source_url TEXT,

    -- Quality
    evidence_level VARCHAR(50),  -- 'randomized_control', 'quasi_experimental', 'observational', 'case_study'
    sample_size INTEGER,
    confidence_interval VARCHAR(50),

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_cost_effectiveness_program ON cost_effectiveness(program_id);
CREATE INDEX idx_cost_effectiveness_type ON cost_effectiveness(intervention_type);
CREATE INDEX idx_cost_effectiveness_jurisdiction ON cost_effectiveness(jurisdiction);

-- Comments
COMMENT ON TABLE cost_effectiveness IS 'Cost-effectiveness and cost-benefit analysis for youth justice interventions';
COMMENT ON COLUMN cost_effectiveness.cost_benefit_ratio IS 'Benefit per dollar spent (e.g., $7 saved per $1 spent)';
COMMENT ON COLUMN cost_effectiveness.evidence_level IS 'Quality of evidence (RCT is highest)';

-- ============================================================================
-- INTERNATIONAL COMPARISONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS international_comparisons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Country/Region
    country VARCHAR(100) NOT NULL,
    region VARCHAR(200),  -- 'New Zealand', 'British Columbia', 'Nordic countries'

    -- Program/Practice
    practice_name VARCHAR(200) NOT NULL,
    practice_type VARCHAR(100),  -- 'therapeutic_care', 'restorative_justice', 'community_based'
    description TEXT,

    -- Outcomes
    key_outcomes JSONB,  -- {"recidivism_reduction": "65%", "cost_savings": "$50M annually"}
    success_factors TEXT[],  -- Key factors that make it work

    -- Cultural Context
    indigenous_focus BOOLEAN DEFAULT false,
    cultural_framework TEXT,  -- 'Māori justice principles', 'Gladue principles', etc.
    community_involvement TEXT,

    -- Implementation
    year_started INTEGER,
    scale VARCHAR(50),  -- 'pilot', 'regional', 'national'
    population_served INTEGER,
    annual_budget NUMERIC,

    -- Evidence
    evaluation_results TEXT,
    source_documents TEXT[],
    source_url TEXT,

    -- Applicability to Mount Isa
    transferability_notes TEXT,
    adaptation_required TEXT,

    -- Metadata
    added_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_international_country ON international_comparisons(country);
CREATE INDEX idx_international_practice_type ON international_comparisons(practice_type);
CREATE INDEX idx_international_indigenous ON international_comparisons(indigenous_focus);

-- Comments
COMMENT ON TABLE international_comparisons IS 'International best practices and innovative approaches from other countries';
COMMENT ON COLUMN international_comparisons.transferability_notes IS 'Notes on how this could be adapted for Mount Isa context';

-- ============================================================================
-- INDIGENOUS EVIDENCE BASE
-- ============================================================================

CREATE TABLE IF NOT EXISTS indigenous_evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Source
    evidence_type VARCHAR(100),  -- 'research_study', 'practice_framework', 'knowledge_system', 'evaluation'
    title TEXT NOT NULL,
    authors TEXT[],
    organization VARCHAR(200),  -- 'AIATSIS', 'SNAICC', 'Lowitja Institute'

    -- Content
    summary TEXT,
    key_findings TEXT[],
    practice_recommendations TEXT[],

    -- Cultural Framework
    indigenous_group VARCHAR(200),  -- 'Aboriginal and Torres Strait Islander', 'Kalkadoon', etc.
    knowledge_framework TEXT,  -- 'Two-way learning', 'On-Country healing', 'Cultural connection'
    cultural_protocols TEXT,

    -- Application
    sector VARCHAR(100),  -- 'youth_justice', 'education', 'health', 'social_services'
    program_area TEXT[],  -- ['diversion', 'rehabilitation', 'prevention']
    evidence_strength VARCHAR(50),  -- 'strong', 'moderate', 'emerging', 'traditional_knowledge'

    -- Access
    publication_year INTEGER,
    publication_type VARCHAR(100),  -- 'journal_article', 'report', 'framework', 'guideline'
    url TEXT,
    open_access BOOLEAN,

    -- Relevance
    mount_isa_relevance TEXT,
    implementation_considerations TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_indigenous_evidence_type ON indigenous_evidence(evidence_type);
CREATE INDEX idx_indigenous_organization ON indigenous_evidence(organization);
CREATE INDEX idx_indigenous_sector ON indigenous_evidence(sector);
CREATE INDEX idx_indigenous_group ON indigenous_evidence(indigenous_group);

-- Comments
COMMENT ON TABLE indigenous_evidence IS 'Indigenous evidence base, research, frameworks, and traditional knowledge';
COMMENT ON COLUMN indigenous_evidence.evidence_strength IS 'Quality of evidence including recognition of traditional knowledge';

-- ============================================================================
-- VIEWS FOR ANALYSIS
-- ============================================================================

-- View: Productivity Commission Youth Justice Metrics
CREATE OR REPLACE VIEW v_productivity_commission_metrics AS
SELECT
    metric_name,
    jurisdiction,
    metric_value,
    metric_unit,
    time_period,
    demographic_group,
    source_url,
    CASE
        WHEN jurisdiction = 'Queensland' THEN 1
        WHEN jurisdiction = 'National' THEN 2
        ELSE 3
    END as sort_order
FROM benchmark_data
WHERE source_type ILIKE '%Productivity Commission%'
ORDER BY metric_name, sort_order;

COMMENT ON VIEW v_productivity_commission_metrics IS 'All Productivity Commission metrics with Queensland prioritized';

-- View: Cost Comparison (Mount Isa vs Alternatives)
CREATE OR REPLACE VIEW v_cost_comparison AS
SELECT
    p.name as program_name,
    ce.intervention_type,
    ce.cost_per_participant as mount_isa_cost,
    ce.cost_per_outcome,
    ce.outcome_metric,
    ce.outcome_value,
    ce.comparator_program,
    ce.cost_benefit_ratio,
    ce.evidence_level
FROM cost_effectiveness ce
LEFT JOIN programs p ON ce.program_id = p.id
WHERE ce.cost_benefit_ratio IS NOT NULL
ORDER BY ce.cost_benefit_ratio DESC;

COMMENT ON VIEW v_cost_comparison IS 'Cost-effectiveness comparison for Mount Isa programs';

-- View: International Best Practices (Indigenous Focus)
CREATE OR REPLACE VIEW v_international_indigenous_practices AS
SELECT
    country,
    practice_name,
    practice_type,
    cultural_framework,
    key_outcomes,
    success_factors,
    transferability_notes,
    source_url
FROM international_comparisons
WHERE indigenous_focus = true
ORDER BY country, practice_name;

COMMENT ON VIEW v_international_indigenous_practices IS 'International best practices with indigenous cultural grounding';

-- View: Evidence Strength Summary
CREATE OR REPLACE VIEW v_evidence_strength_summary AS
SELECT
    sector,
    evidence_strength,
    COUNT(*) as evidence_count,
    ARRAY_AGG(DISTINCT organization) as contributing_organizations,
    ARRAY_AGG(title) as studies
FROM indigenous_evidence
GROUP BY sector, evidence_strength
ORDER BY sector,
    CASE evidence_strength
        WHEN 'strong' THEN 1
        WHEN 'moderate' THEN 2
        WHEN 'emerging' THEN 3
        WHEN 'traditional_knowledge' THEN 4
        ELSE 5
    END;

COMMENT ON VIEW v_evidence_strength_summary IS 'Summary of evidence strength by sector';

-- View: Complete Evidence Base for Program
CREATE OR REPLACE VIEW v_program_evidence_base AS
SELECT
    p.name as program_name,
    p.program_type,
    -- Outcomes
    po.metric_name as outcome_metric,
    po.metric_value as outcome_value,
    -- Costs
    ce.cost_per_participant,
    ce.cost_benefit_ratio,
    -- Benchmarks
    bd.metric_value as benchmark_value,
    bd.jurisdiction as benchmark_jurisdiction,
    -- Evidence
    ie.title as supporting_evidence,
    ie.evidence_strength
FROM programs p
LEFT JOIN program_outcomes po ON p.id = po.program_id
LEFT JOIN cost_effectiveness ce ON p.id = ce.program_id
LEFT JOIN benchmark_data bd ON bd.metric_name = po.metric_name
LEFT JOIN indigenous_evidence ie ON ie.sector = 'youth_justice'
WHERE p.is_active = true;

COMMENT ON VIEW v_program_evidence_base IS 'Complete evidence base for each program (outcomes, costs, benchmarks, research)';

-- ============================================================================
-- SAMPLE QUERIES FOR JUSTICEHUB STORIES
-- ============================================================================

-- Query 1: Show Mount Isa On-Country program vs National detention costs
-- SELECT * FROM benchmark_data
-- WHERE metric_name ILIKE '%cost per day%'
-- AND (jurisdiction = 'Queensland' OR jurisdiction = 'National')
-- ORDER BY time_period DESC, jurisdiction;

-- Query 2: Cost-benefit of diversion programs
-- SELECT intervention_name, cost_per_participant, cost_benefit_ratio, outcome_metric, outcome_value
-- FROM cost_effectiveness
-- WHERE intervention_type = 'diversion'
-- ORDER BY cost_benefit_ratio DESC;

-- Query 3: International indigenous models
-- SELECT country, practice_name, cultural_framework, key_outcomes->>'recidivism_reduction' as recidivism_impact
-- FROM international_comparisons
-- WHERE indigenous_focus = true
-- ORDER BY country;

-- Query 4: Indigenous evidence for on-country programs
-- SELECT title, organization, key_findings, mount_isa_relevance
-- FROM indigenous_evidence
-- WHERE program_area @> ARRAY['rehabilitation']
-- AND evidence_strength IN ('strong', 'moderate')
-- ORDER BY publication_year DESC;

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_benchmark_data_updated_at BEFORE UPDATE ON benchmark_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cost_effectiveness_updated_at BEFORE UPDATE ON cost_effectiveness
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_international_comparisons_updated_at BEFORE UPDATE ON international_comparisons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_indigenous_evidence_updated_at BEFORE UPDATE ON indigenous_evidence
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- GRANTS (adjust role name as needed)
-- ============================================================================

-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;

-- ============================================================================
-- COMPLETE
-- ============================================================================

-- You now have tables to store:
-- 1. benchmark_data: Productivity Commission metrics, state/national comparisons
-- 2. cost_effectiveness: Cost-benefit analysis, program effectiveness
-- 3. international_comparisons: Best practices from NZ, Canada, Nordic countries, etc.
-- 4. indigenous_evidence: AIATSIS, SNAICC, Lowitja research and frameworks

-- Next steps:
-- 1. Run: python scripts/scrape_productivity_commission.py
-- 2. Add international examples from DATA_SOURCES_EXPANSION.md
-- 3. Compile indigenous evidence base
-- 4. Use views for JusticeHub stories
