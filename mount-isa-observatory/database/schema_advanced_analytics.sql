-- ============================================================================
-- ADVANCED ANALYTICS SCHEMA - GOING DEEPER
-- ============================================================================
-- Beyond descriptive tracking to diagnostic, predictive, and prescriptive analytics
--
-- This schema enables:
-- - Network analysis (who's connected to whom, power structures)
-- - Temporal patterns (how long from announcement to payment, seasonal patterns)
-- - Geographic equity (who's covered, who's left out)
-- - Outcome prediction (what makes programs succeed)
-- - Policy simulation (model "what if" scenarios)
-- - Causal inference (prove what works, not just correlation)
--
-- Run after: supabase_schema.sql, schema_additions_benchmarks.sql
-- ============================================================================

-- ============================================================================
-- NETWORK ANALYSIS - Follow the Money, Find the Power
-- ============================================================================

-- People (decision-makers, influencers, community leaders)
CREATE TABLE IF NOT EXISTS people (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Identity
    full_name VARCHAR(200) NOT NULL,
    preferred_name VARCHAR(100),

    -- Roles (can have multiple)
    current_roles JSONB,  -- [{"role": "Minister", "organization": "QLD Govt", "start_date": "2023-01"}]
    historical_roles JSONB,  -- Track career trajectory

    -- Influence
    decision_making_authority TEXT[],  -- ['funding_approval', 'policy_setting', 'program_design']
    areas_of_influence TEXT[],  -- ['youth_justice', 'indigenous_affairs', 'community_safety']

    -- Connections
    organization_affiliations UUID[],  -- Links to organizations table

    -- Public profile
    photo_url TEXT,
    bio TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Relationships between entities (people, organizations)
CREATE TABLE IF NOT EXISTS relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Who
    entity_a_type VARCHAR(50),  -- 'person', 'organization'
    entity_a_id UUID,
    entity_b_type VARCHAR(50),
    entity_b_id UUID,

    -- What kind of relationship
    relationship_type VARCHAR(100),  -- 'reports_to', 'funds', 'partners_with', 'advises', 'employs'
    relationship_strength VARCHAR(50),  -- 'strong', 'moderate', 'weak'

    -- Context
    context TEXT,  -- Description of relationship
    is_formal BOOLEAN DEFAULT false,  -- Formal agreement vs informal connection

    -- When
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT true,

    -- Evidence
    source_document_id UUID REFERENCES documents(id),
    confidence_score INTEGER CHECK (confidence_score BETWEEN 1 AND 5),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Funding decisions (who approved what, when, why)
CREATE TABLE IF NOT EXISTS funding_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- What was decided
    funding_announcement_id UUID REFERENCES funding_announcements(id),
    decision_type VARCHAR(50),  -- 'approval', 'rejection', 'amendment', 'deferral'

    -- Who decided
    decision_makers UUID[],  -- Array of person IDs
    decision_making_body VARCHAR(200),  -- 'Cabinet', 'Treasury', 'Department', 'Board'

    -- When
    decision_date DATE,
    announcement_delay_days INTEGER,  -- Days between decision and public announcement

    -- Why (stated reasons)
    stated_rationale TEXT,
    policy_alignment TEXT[],  -- Which policies does this support

    -- Context
    political_context TEXT,  -- Election cycle, budget context, public pressure
    competing_priorities TEXT[],  -- What else was being considered

    -- Evidence
    source_document_id UUID REFERENCES documents(id),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for network analysis
CREATE INDEX idx_relationships_entity_a ON relationships(entity_a_type, entity_a_id);
CREATE INDEX idx_relationships_entity_b ON relationships(entity_b_type, entity_b_id);
CREATE INDEX idx_relationships_type ON relationships(relationship_type);
CREATE INDEX idx_relationships_active ON relationships(is_active);
CREATE INDEX idx_people_roles ON people USING gin(current_roles);
CREATE INDEX idx_funding_decisions_announcement ON funding_decisions(funding_announcement_id);

COMMENT ON TABLE people IS 'Decision-makers, influencers, community leaders - track who has power and authority';
COMMENT ON TABLE relationships IS 'Network of connections between people and organizations - reveals power structures';
COMMENT ON TABLE funding_decisions IS 'Who approved what funding, when, and why - accountability at decision level';

-- ============================================================================
-- TEMPORAL ANALYSIS - Patterns Over Time
-- ============================================================================

-- Funding lifecycle events (track every stage with timestamps)
CREATE TABLE IF NOT EXISTS funding_lifecycle_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- What
    funding_announcement_id UUID REFERENCES funding_announcements(id),
    event_type VARCHAR(100),  -- 'announced', 'budgeted', 'contracted', 'first_payment', 'final_payment', 'evaluated'

    -- When
    event_date DATE NOT NULL,
    fiscal_year VARCHAR(10),  -- '2023-24'
    quarter VARCHAR(10),  -- 'Q1', 'Q2', 'Q3', 'Q4'

    -- Context
    days_since_previous_event INTEGER,
    days_since_announcement INTEGER,

    -- Who was involved
    responsible_organization_id UUID REFERENCES organizations(id),
    responsible_person_id UUID REFERENCES people(id),

    -- Evidence
    source_document_id UUID REFERENCES documents(id),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Temporal patterns (detected patterns across funding)
CREATE TABLE IF NOT EXISTS temporal_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Pattern
    pattern_type VARCHAR(100),  -- 'seasonal_announcement', 'budget_cycle', 'election_spike', 'approval_delay'
    pattern_name VARCHAR(200),
    description TEXT,

    -- Evidence
    supporting_examples UUID[],  -- Array of funding_announcement_id
    statistical_significance NUMERIC,

    -- Insights
    average_duration_days NUMERIC,
    median_duration_days NUMERIC,
    range_min_days INTEGER,
    range_max_days INTEGER,

    -- Factors
    influencing_factors JSONB,  -- {"election_year": true, "budget_quarter": "Q2", etc}

    -- Metadata
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lifecycle_events_announcement ON funding_lifecycle_events(funding_announcement_id);
CREATE INDEX idx_lifecycle_events_type ON funding_lifecycle_events(event_type);
CREATE INDEX idx_lifecycle_events_date ON funding_lifecycle_events(event_date);
CREATE INDEX idx_lifecycle_events_fiscal_year ON funding_lifecycle_events(fiscal_year);

COMMENT ON TABLE funding_lifecycle_events IS 'Every stage of funding lifecycle with timestamps - reveals delays and bottlenecks';
COMMENT ON TABLE temporal_patterns IS 'Detected patterns over time - seasonal, political, bureaucratic';

-- ============================================================================
-- GEOGRAPHIC EQUITY ANALYSIS - Who's Covered, Who's Left Out
-- ============================================================================

-- Service coverage (which communities are served by which programs)
CREATE TABLE IF NOT EXISTS service_coverage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- What
    program_id UUID REFERENCES programs(id),

    -- Where
    location_id UUID REFERENCES locations(id),
    coverage_type VARCHAR(50),  -- 'primary_service_area', 'outreach', 'occasional', 'not_served'

    -- How well
    capacity_youth_served INTEGER,  -- How many youth can be served
    current_youth_served INTEGER,  -- How many currently served
    waitlist_count INTEGER,

    -- Access
    physical_access VARCHAR(50),  -- 'on_site', 'nearby', 'remote', 'no_access'
    cultural_access VARCHAR(50),  -- 'culturally_appropriate', 'culturally_responsive', 'mainstream', 'culturally_inappropriate'
    distance_km NUMERIC,
    travel_time_minutes INTEGER,

    -- Gaps
    unmet_need_estimate INTEGER,  -- Estimated youth who need service but don't have access
    gap_severity VARCHAR(50),  -- 'critical', 'high', 'moderate', 'low', 'none'

    -- Evidence
    source_document_id UUID REFERENCES documents(id),
    last_assessed_date DATE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Geographic gaps (where services are needed but don't exist)
CREATE TABLE IF NOT EXISTS geographic_gaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Where
    location_id UUID REFERENCES locations(id),
    gap_description TEXT,

    -- Population
    youth_population INTEGER,
    indigenous_youth_population INTEGER,
    at_risk_youth_estimate INTEGER,
    youth_justice_involved_count INTEGER,

    -- What's missing
    needed_services TEXT[],  -- ['on_country', 'co_responder', 'diversion']
    nearest_service_km NUMERIC,
    nearest_service_program_id UUID REFERENCES programs(id),

    -- Impact of gap
    gap_severity VARCHAR(50),  -- 'critical', 'high', 'moderate', 'low'
    consequences TEXT,  -- What happens because service doesn't exist

    -- Equity dimensions
    indigenous_over_representation_factor NUMERIC,  -- How much higher than population %
    socioeconomic_disadvantage_score NUMERIC,  -- 1-10 scale
    remoteness_category VARCHAR(50),  -- 'very_remote', 'remote', 'outer_regional', 'inner_regional', 'major_city'

    -- Evidence
    source_document_id UUID REFERENCES documents(id),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_service_coverage_program ON service_coverage(program_id);
CREATE INDEX idx_service_coverage_location ON service_coverage(location_id);
CREATE INDEX idx_geographic_gaps_location ON geographic_gaps(location_id);
CREATE INDEX idx_geographic_gaps_severity ON geographic_gaps(gap_severity);

COMMENT ON TABLE service_coverage IS 'Which programs serve which communities - reveals coverage gaps and access barriers';
COMMENT ON TABLE geographic_gaps IS 'Where services are needed but missing - prioritize expansion';

-- ============================================================================
-- PREDICTIVE ANALYTICS - What Will Happen
-- ============================================================================

-- Program characteristics (features that predict success)
CREATE TABLE IF NOT EXISTS program_characteristics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- What
    program_id UUID REFERENCES programs(id),

    -- Design characteristics
    is_culturally_grounded BOOLEAN,
    has_on_country_component BOOLEAN,
    has_family_involvement BOOLEAN,
    has_elder_involvement BOOLEAN,
    has_mental_health_support BOOLEAN,
    has_education_component BOOLEAN,
    has_employment_pathway BOOLEAN,

    -- Delivery model
    delivery_model VARCHAR(100),  -- 'residential', 'outreach', 'hybrid', 'community_based'
    intensity_level VARCHAR(50),  -- 'intensive', 'moderate', 'low'
    duration_weeks_typical INTEGER,

    -- Staffing
    staff_to_youth_ratio NUMERIC,
    staff_indigenous_percentage NUMERIC,
    staff_locally_based_percentage NUMERIC,
    staff_cultural_training BOOLEAN,

    -- Partnership model
    is_community_led BOOLEAN,
    has_government_partnership BOOLEAN,
    has_ngo_partnership BOOLEAN,
    has_traditional_owner_partnership BOOLEAN,

    -- Resources
    funding_per_participant NUMERIC,
    has_dedicated_facility BOOLEAN,
    has_transport_provided BOOLEAN,

    -- Target population
    target_age_min INTEGER,
    target_age_max INTEGER,
    target_indigenous_specific BOOLEAN,
    target_risk_level VARCHAR(50),  -- 'low', 'medium', 'high', 'very_high'

    -- Evidence base
    is_evidence_based BOOLEAN,
    evidence_base_source TEXT,

    -- Metadata
    data_collection_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Outcome predictions (model predictions for programs)
CREATE TABLE IF NOT EXISTS outcome_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- What
    program_id UUID REFERENCES programs(id),
    prediction_type VARCHAR(100),  -- 'recidivism_reduction', 'completion_rate', 'cost_effectiveness'

    -- Prediction
    predicted_value NUMERIC,
    prediction_confidence NUMERIC,  -- 0-1 scale
    confidence_interval_lower NUMERIC,
    confidence_interval_upper NUMERIC,

    -- Model
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    features_used JSONB,  -- Which characteristics were used

    -- Comparison to baseline
    baseline_value NUMERIC,  -- What happens without this program
    predicted_improvement NUMERIC,
    predicted_improvement_percentage NUMERIC,

    -- Actual outcome (for validation)
    actual_value NUMERIC,
    prediction_error NUMERIC,

    -- Metadata
    prediction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    outcome_measurement_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_program_characteristics_program ON program_characteristics(program_id);
CREATE INDEX idx_program_characteristics_culturally_grounded ON program_characteristics(is_culturally_grounded);
CREATE INDEX idx_outcome_predictions_program ON outcome_predictions(program_id);
CREATE INDEX idx_outcome_predictions_type ON outcome_predictions(prediction_type);

COMMENT ON TABLE program_characteristics IS 'Features that predict success - what makes programs work';
COMMENT ON TABLE outcome_predictions IS 'Model predictions vs actual outcomes - validate what works';

-- ============================================================================
-- POLICY SIMULATION - What Should We Do
-- ============================================================================

-- Scenarios (model different policy choices)
CREATE TABLE IF NOT EXISTS policy_scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Scenario
    scenario_name VARCHAR(200) NOT NULL,
    scenario_type VARCHAR(100),  -- 'funding_reallocation', 'program_expansion', 'new_program', 'service_closure'
    description TEXT,

    -- Policy changes
    funding_changes JSONB,  -- {"detention": -5000000, "on_country": +5000000}
    program_changes JSONB,  -- {"new_programs": [...], "expanded_programs": [...], "closed_programs": [...]}
    service_delivery_changes JSONB,

    -- Assumptions
    assumptions TEXT[],
    implementation_timeline TEXT,
    implementation_costs NUMERIC,

    -- Predicted outcomes
    predicted_youth_served_change INTEGER,
    predicted_recidivism_change NUMERIC,  -- Percentage point change
    predicted_cost_change NUMERIC,  -- Annual budget impact
    predicted_detention_reduction INTEGER,  -- Youth diverted from detention

    -- Equity impact
    indigenous_impact_differential NUMERIC,
    geographic_equity_change TEXT,
    community_benefit_assessment TEXT,

    -- Political feasibility
    political_feasibility VARCHAR(50),  -- 'high', 'moderate', 'low'
    stakeholder_support_assessment TEXT,

    -- Evidence base
    evidence_strength VARCHAR(50),  -- 'strong', 'moderate', 'weak', 'speculative'
    comparable_examples TEXT[],  -- Where has this been done before

    -- Metadata
    created_by VARCHAR(100),
    created_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Scenario impacts (detailed modeling of scenario effects)
CREATE TABLE IF NOT EXISTS scenario_impacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Which scenario
    scenario_id UUID REFERENCES policy_scenarios(id),

    -- Impact area
    impact_category VARCHAR(100),  -- 'financial', 'outcomes', 'equity', 'community', 'system'
    impact_metric VARCHAR(200),

    -- Current state
    baseline_value NUMERIC,
    baseline_unit VARCHAR(50),

    -- Projected state
    projected_value NUMERIC,
    change_absolute NUMERIC,
    change_percentage NUMERIC,

    -- Time horizon
    time_horizon_years INTEGER,
    short_term_impact NUMERIC,  -- Year 1
    medium_term_impact NUMERIC,  -- Year 3
    long_term_impact NUMERIC,  -- Year 5+

    -- Confidence
    confidence_level VARCHAR(50),  -- 'high', 'medium', 'low'

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policy_scenarios_type ON policy_scenarios(scenario_type);
CREATE INDEX idx_scenario_impacts_scenario ON scenario_impacts(scenario_id);
CREATE INDEX idx_scenario_impacts_category ON scenario_impacts(impact_category);

COMMENT ON TABLE policy_scenarios IS 'Model different policy choices - what if we reallocate funding, expand programs, etc.';
COMMENT ON TABLE scenario_impacts IS 'Detailed impacts of each scenario - predict financial, outcome, equity effects';

-- ============================================================================
-- CAUSAL INFERENCE - Prove What Works (Not Just Correlation)
-- ============================================================================

-- Comparison groups (for quasi-experimental analysis)
CREATE TABLE IF NOT EXISTS comparison_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Study
    study_name VARCHAR(200),
    study_design VARCHAR(100),  -- 'randomized_control', 'quasi_experimental', 'matched_comparison', 'regression_discontinuity'

    -- Treatment group
    treatment_program_id UUID REFERENCES programs(id),
    treatment_group_size INTEGER,
    treatment_group_characteristics JSONB,

    -- Comparison group
    comparison_type VARCHAR(100),  -- 'no_program', 'alternative_program', 'standard_practice'
    comparison_program_id UUID REFERENCES programs(id),
    comparison_group_size INTEGER,
    comparison_group_characteristics JSONB,

    -- Matching
    matching_method VARCHAR(100),  -- 'propensity_score', 'exact_match', 'demographic_match'
    matching_variables TEXT[],
    balance_assessment TEXT,

    -- Timeframe
    study_start_date DATE,
    study_end_date DATE,
    follow_up_duration_months INTEGER,

    -- Evidence
    source_document_id UUID REFERENCES documents(id),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Causal estimates (treatment effects)
CREATE TABLE IF NOT EXISTS causal_estimates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Study
    comparison_group_id UUID REFERENCES comparison_groups(id),

    -- Outcome
    outcome_name VARCHAR(200),
    outcome_type VARCHAR(100),  -- 'recidivism', 'completion', 'employment', 'reoffending_severity'

    -- Treatment effect
    treatment_group_outcome NUMERIC,
    comparison_group_outcome NUMERIC,
    treatment_effect NUMERIC,  -- Difference
    treatment_effect_percentage NUMERIC,

    -- Statistical significance
    standard_error NUMERIC,
    p_value NUMERIC,
    confidence_interval_95_lower NUMERIC,
    confidence_interval_95_upper NUMERIC,

    -- Effect size
    cohens_d NUMERIC,  -- Standardized effect size
    effect_interpretation VARCHAR(50),  -- 'large', 'medium', 'small', 'negligible'

    -- Robustness
    sensitivity_analysis_results TEXT,
    alternative_specifications JSONB,  -- Results under different model specifications

    -- Causal claim
    causal_inference_strength VARCHAR(50),  -- 'strong', 'moderate', 'weak', 'suggestive'
    threats_to_validity TEXT[],

    -- Metadata
    analysis_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_comparison_groups_treatment ON comparison_groups(treatment_program_id);
CREATE INDEX idx_comparison_groups_comparison ON comparison_groups(comparison_program_id);
CREATE INDEX idx_causal_estimates_comparison ON causal_estimates(comparison_group_id);

COMMENT ON TABLE comparison_groups IS 'Experimental and quasi-experimental study designs - set up for causal inference';
COMMENT ON TABLE causal_estimates IS 'Treatment effects with statistical significance - prove causation not just correlation';

-- ============================================================================
-- ADVANCED VIEWS - Complex Analysis Queries
-- ============================================================================

-- View: Funding Network - Who funds whom
CREATE OR REPLACE VIEW v_funding_network AS
SELECT
    funder.name as funder_name,
    funder.organization_type as funder_type,
    recipient.name as recipient_name,
    recipient.organization_type as recipient_type,
    COUNT(DISTINCT fa.id) as funding_count,
    SUM(fa.amount_announced) / 1000000 as total_funding_m,
    MIN(fa.announcement_date) as first_funding_date,
    MAX(fa.announcement_date) as latest_funding_date,
    ARRAY_AGG(DISTINCT p.name) as programs_funded
FROM funding_announcements fa
JOIN organizations funder ON fa.funding_body_id = funder.id
JOIN organizations recipient ON fa.recipient_org_id = recipient.id
LEFT JOIN programs p ON fa.program_id = p.id
GROUP BY funder.id, funder.name, funder.organization_type, recipient.id, recipient.name, recipient.organization_type;

COMMENT ON VIEW v_funding_network IS 'Network of funding relationships - reveals patterns of who funds whom repeatedly';

-- View: Temporal performance - How long does each stage take
CREATE OR REPLACE VIEW v_temporal_performance AS
WITH event_pairs AS (
    SELECT
        funding_announcement_id,
        event_type as current_event,
        event_date as current_date,
        LAG(event_type) OVER (PARTITION BY funding_announcement_id ORDER BY event_date) as previous_event,
        LAG(event_date) OVER (PARTITION BY funding_announcement_id ORDER BY event_date) as previous_date
    FROM funding_lifecycle_events
)
SELECT
    current_event,
    previous_event,
    AVG(current_date - previous_date) as avg_duration_days,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY current_date - previous_date) as median_duration_days,
    MIN(current_date - previous_date) as min_duration_days,
    MAX(current_date - previous_date) as max_duration_days,
    COUNT(*) as sample_size
FROM event_pairs
WHERE previous_event IS NOT NULL
GROUP BY current_event, previous_event
ORDER BY avg_duration_days DESC;

COMMENT ON VIEW v_temporal_performance IS 'How long each stage of funding lifecycle takes - identify bottlenecks';

-- View: Geographic equity scorecard
CREATE OR REPLACE VIEW v_geographic_equity_scorecard AS
SELECT
    l.name as community_name,
    gg.youth_population,
    gg.indigenous_youth_population,
    gg.indigenous_over_representation_factor,
    gg.remoteness_category,
    gg.socioeconomic_disadvantage_score,
    ARRAY_LENGTH(gg.needed_services, 1) as services_needed_count,
    gg.nearest_service_km,
    gg.gap_severity,
    -- Coverage score (0-100)
    CASE
        WHEN gg.gap_severity = 'critical' THEN 0
        WHEN gg.gap_severity = 'high' THEN 25
        WHEN gg.gap_severity = 'moderate' THEN 50
        WHEN gg.gap_severity = 'low' THEN 75
        ELSE 100
    END as coverage_score,
    -- Equity priority (combine multiple factors)
    (
        COALESCE(gg.indigenous_over_representation_factor, 1) *
        COALESCE(gg.socioeconomic_disadvantage_score, 1) *
        CASE gg.remoteness_category
            WHEN 'very_remote' THEN 2
            WHEN 'remote' THEN 1.5
            WHEN 'outer_regional' THEN 1.2
            ELSE 1
        END
    ) as equity_priority_score
FROM locations l
LEFT JOIN geographic_gaps gg ON l.id = gg.location_id
ORDER BY equity_priority_score DESC NULLS LAST;

COMMENT ON VIEW v_geographic_equity_scorecard IS 'Equity analysis for each community - prioritize based on need, disadvantage, remoteness';

-- View: Program success prediction
CREATE OR REPLACE VIEW v_program_success_prediction AS
SELECT
    p.name as program_name,
    p.program_type,
    pc.is_culturally_grounded,
    pc.has_on_country_component,
    pc.is_community_led,
    pc.staff_indigenous_percentage,
    pc.funding_per_participant,
    op.prediction_type,
    op.predicted_value,
    op.prediction_confidence,
    op.actual_value,
    CASE
        WHEN op.actual_value IS NOT NULL THEN
            ABS(op.predicted_value - op.actual_value) / NULLIF(op.actual_value, 0) * 100
        ELSE NULL
    END as prediction_error_percentage,
    CASE
        WHEN op.actual_value IS NULL THEN 'prediction'
        WHEN ABS(op.predicted_value - op.actual_value) / NULLIF(op.actual_value, 0) < 0.1 THEN 'accurate'
        WHEN ABS(op.predicted_value - op.actual_value) / NULLIF(op.actual_value, 0) < 0.2 THEN 'reasonable'
        ELSE 'inaccurate'
    END as prediction_quality
FROM programs p
JOIN program_characteristics pc ON p.id = pc.program_id
LEFT JOIN outcome_predictions op ON p.id = op.program_id;

COMMENT ON VIEW v_program_success_prediction IS 'Predicted vs actual outcomes - validate what characteristics predict success';

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE (Refresh daily/weekly)
-- ============================================================================

-- Materialized view: Funding patterns by organization
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_organization_funding_patterns AS
SELECT
    o.id as organization_id,
    o.name as organization_name,
    o.organization_type,
    COUNT(DISTINCT fa.id) as total_announcements,
    SUM(fa.amount_announced) / 1000000 as total_announced_m,
    SUM(ap.amount_paid) / 1000000 as total_verified_paid_m,
    (SUM(ap.amount_paid) / NULLIF(SUM(fa.amount_announced), 0) * 100) as verification_rate,
    MIN(fa.announcement_date) as first_funding,
    MAX(fa.announcement_date) as latest_funding,
    EXTRACT(YEAR FROM AGE(MAX(fa.announcement_date), MIN(fa.announcement_date))) as funding_relationship_years,
    COUNT(DISTINCT fa.funding_body_id) as unique_funders,
    COUNT(DISTINCT fa.program_id) as programs_operated
FROM organizations o
LEFT JOIN funding_announcements fa ON o.id = fa.recipient_org_id
LEFT JOIN actual_payments ap ON fa.id = ap.announcement_id
GROUP BY o.id, o.name, o.organization_type;

CREATE UNIQUE INDEX ON mv_organization_funding_patterns(organization_id);

COMMENT ON MATERIALIZED VIEW mv_organization_funding_patterns IS 'Funding patterns by organization - refresh daily to see trends';

-- ============================================================================
-- FUNCTIONS FOR ADVANCED ANALYTICS
-- ============================================================================

-- Function: Calculate equity priority score for a location
CREATE OR REPLACE FUNCTION calculate_equity_priority(
    p_location_id UUID
) RETURNS NUMERIC AS $$
DECLARE
    v_score NUMERIC;
BEGIN
    SELECT
        COALESCE(gg.indigenous_over_representation_factor, 1) *
        COALESCE(gg.socioeconomic_disadvantage_score, 1) *
        CASE gg.remoteness_category
            WHEN 'very_remote' THEN 2
            WHEN 'remote' THEN 1.5
            WHEN 'outer_regional' THEN 1.2
            ELSE 1
        END
    INTO v_score
    FROM geographic_gaps gg
    WHERE gg.location_id = p_location_id;

    RETURN COALESCE(v_score, 0);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_equity_priority IS 'Calculate equity priority score combining Indigenous over-rep, disadvantage, remoteness';

-- Function: Detect temporal anomalies (unusually fast or slow funding)
CREATE OR REPLACE FUNCTION detect_temporal_anomalies()
RETURNS TABLE (
    funding_announcement_id UUID,
    stage_transition VARCHAR,
    duration_days INTEGER,
    expected_duration_days NUMERIC,
    anomaly_type VARCHAR,
    severity VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    WITH stage_durations AS (
        SELECT
            fle.funding_announcement_id,
            fle.event_type || ' -> ' || LEAD(fle.event_type) OVER (PARTITION BY fle.funding_announcement_id ORDER BY fle.event_date) as transition,
            LEAD(fle.event_date) OVER (PARTITION BY fle.funding_announcement_id ORDER BY fle.event_date) - fle.event_date as duration,
            fle.event_type as from_stage,
            LEAD(fle.event_type) OVER (PARTITION BY fle.funding_announcement_id ORDER BY fle.event_date) as to_stage
        FROM funding_lifecycle_events fle
    ),
    expected_durations AS (
        SELECT
            transition,
            AVG(duration) as avg_duration,
            STDDEV(duration) as stddev_duration
        FROM stage_durations
        WHERE duration IS NOT NULL
        GROUP BY transition
    )
    SELECT
        sd.funding_announcement_id,
        sd.transition,
        sd.duration,
        ed.avg_duration,
        CASE
            WHEN sd.duration > ed.avg_duration + 2 * ed.stddev_duration THEN 'extremely_slow'
            WHEN sd.duration > ed.avg_duration + ed.stddev_duration THEN 'slow'
            WHEN sd.duration < ed.avg_duration - 2 * ed.stddev_duration THEN 'extremely_fast'
            WHEN sd.duration < ed.avg_duration - ed.stddev_duration THEN 'fast'
        END as anomaly_type,
        CASE
            WHEN ABS(sd.duration - ed.avg_duration) > 2 * ed.stddev_duration THEN 'high'
            WHEN ABS(sd.duration - ed.avg_duration) > ed.stddev_duration THEN 'medium'
            ELSE 'low'
        END as severity
    FROM stage_durations sd
    JOIN expected_durations ed ON sd.transition = ed.transition
    WHERE sd.duration IS NOT NULL
    AND (
        sd.duration > ed.avg_duration + ed.stddev_duration OR
        sd.duration < ed.avg_duration - ed.stddev_duration
    )
    ORDER BY severity DESC, sd.duration DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION detect_temporal_anomalies IS 'Detect unusually fast or slow funding stages - investigate anomalies';

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE TRIGGER update_people_updated_at BEFORE UPDATE ON people
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relationships_updated_at BEFORE UPDATE ON relationships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_funding_decisions_updated_at BEFORE UPDATE ON funding_decisions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMPLETE
-- ============================================================================

-- You now have advanced analytics capabilities:
-- ✅ Network analysis (follow the money, find the power)
-- ✅ Temporal patterns (detect delays, bottlenecks, anomalies)
-- ✅ Geographic equity (who's covered, who's left out)
-- ✅ Predictive models (what will succeed)
-- ✅ Policy simulation (model "what if")
-- ✅ Causal inference (prove what works)

-- Next: Populate these tables and run advanced queries to reveal system-level insights
