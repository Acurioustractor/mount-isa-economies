-- ============================================================================
-- CREATE FUNDING NETWORK VIEW (Standalone)
-- ============================================================================
-- This creates just the v_funding_network view needed for network analysis
-- Run this if you want to test network analysis without adding full advanced schema
--
-- For complete advanced analytics, use schema_advanced_analytics.sql instead
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
GROUP BY funder.id, funder.name, funder.organization_type,
         recipient.id, recipient.name, recipient.organization_type;

COMMENT ON VIEW v_funding_network IS 'Network of funding relationships - reveals patterns of who funds whom repeatedly';

-- Test the view
SELECT
    funder_name,
    recipient_name,
    funding_count,
    total_funding_m,
    programs_funded
FROM v_funding_network
ORDER BY total_funding_m DESC
LIMIT 10;

-- Done! Now you can run: python scripts/advanced_network_analysis.py
