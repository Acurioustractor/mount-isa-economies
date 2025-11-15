"""
Mount Isa Economic Observatory Dashboard Configuration
Defines KPIs, visualizations, and dashboard structure
"""
from typing import Dict, List


class DashboardConfig:
    """Configuration for the Economic Observatory Dashboard"""

    # Key Performance Indicators
    KPIs = {
        'local_retention_rate': {
            'name': 'Local Retention Rate',
            'description': 'Percentage of money that stays within Mount Isa economy',
            'target': 60,  # Target 60% retention (from current baseline + 10%)
            'format': 'percentage',
            'color_threshold': {
                'red': 40,
                'yellow': 50,
                'green': 60
            }
        },
        'leakage_amount': {
            'name': 'Annual Economic Leakage',
            'description': 'Total dollars flowing out of local economy per year',
            'format': 'currency',
            'trend': 'down_is_good'
        },
        'local_business_count': {
            'name': 'Local Business Count',
            'description': 'Number of active local businesses',
            'format': 'number',
            'trend': 'up_is_good'
        },
        'local_jobs_created': {
            'name': 'Local Jobs Created',
            'description': 'New local jobs from import replacement',
            'target': 50,  # Target 50 new local jobs in pilot year
            'format': 'number',
            'trend': 'up_is_good'
        },
        'service_gap_count': {
            'name': 'Service Gaps Identified',
            'description': 'Number of high-demand services with limited local supply',
            'format': 'number'
        }
    }

    # Dashboard Visualizations
    VISUALIZATIONS = [
        {
            'id': 'money_flow_sankey',
            'type': 'sankey',
            'title': 'Economic Flow Map: Where Money Goes',
            'description': 'Sankey diagram showing money flows from sources through local economy',
            'query': '''
                SELECT
                    payer_type.entity_type AS source,
                    payee_type.entity_type AS target,
                    SUM(flow.amount) AS value
                FROM fact_economic_flows flow
                JOIN dim_entity_type payer_type ON flow.payer_type_id = payer_type.entity_type_id
                JOIN dim_entity_type payee_type ON flow.payee_type_id = payee_type.entity_type_id
                JOIN dim_date d ON flow.date_id = d.date_id
                WHERE d.year = EXTRACT(YEAR FROM CURRENT_DATE)
                GROUP BY payer_type.entity_type, payee_type.entity_type
                HAVING SUM(flow.amount) > 0
            ''',
            'config': {
                'node_color': {
                    'LOCAL_BUSINESS': '#2ecc71',
                    'EXTERNAL_BUSINESS': '#e74c3c',
                    'COMMONWEALTH': '#3498db',
                    'STATE_QLD': '#9b59b6',
                    'LOCAL_HOUSEHOLD': '#f39c12'
                }
            }
        },
        {
            'id': 'leakage_treemap',
            'type': 'treemap',
            'title': 'Top Leakages by Category',
            'description': 'Where are we losing the most money to external providers?',
            'query': '''
                SELECT
                    i.division_title AS category,
                    p.program_type AS subcategory,
                    SUM(f.amount) AS value
                FROM fact_economic_flows f
                LEFT JOIN dim_industry i ON f.industry_id = i.industry_id
                LEFT JOIN dim_program p ON f.program_id = p.program_id
                JOIN dim_date d ON f.date_id = d.date_id
                WHERE f.is_leakage = TRUE
                  AND d.year = EXTRACT(YEAR FROM CURRENT_DATE)
                GROUP BY i.division_title, p.program_type
                ORDER BY value DESC
                LIMIT 20
            '''
        },
        {
            'id': 'local_vs_external_trend',
            'type': 'line',
            'title': 'Local vs External Spending Trend',
            'description': 'Tracking progress toward localization goal',
            'query': '''
                SELECT
                    d.date,
                    SUM(CASE WHEN f.is_leakage = FALSE THEN f.amount ELSE 0 END) AS local_spending,
                    SUM(CASE WHEN f.is_leakage = TRUE THEN f.amount ELSE 0 END) AS external_spending,
                    SUM(CASE WHEN f.is_leakage = FALSE THEN f.amount ELSE 0 END) /
                    NULLIF(SUM(f.amount), 0) * 100 AS local_percentage
                FROM fact_economic_flows f
                JOIN dim_date d ON f.date_id = d.date_id
                WHERE d.date >= CURRENT_DATE - INTERVAL '2 years'
                GROUP BY d.date
                ORDER BY d.date
            ''',
            'config': {
                'target_line': 60,  # 10% localization goal
                'y_axis_format': 'currency'
            }
        },
        {
            'id': 'service_gaps_matrix',
            'type': 'heatmap',
            'title': 'Service Capacity Gaps',
            'description': 'Industries with high external spending but low local providers',
            'query': '''
                SELECT
                    i.anzsic_title AS industry,
                    SUM(f.amount) AS external_spending,
                    COUNT(DISTINCT pe.entity_id) AS local_provider_count,
                    SUM(f.amount) / NULLIF(COUNT(DISTINCT pe.entity_id), 0) AS spending_per_provider
                FROM fact_economic_flows f
                JOIN dim_industry i ON f.industry_id = i.industry_id
                LEFT JOIN entities pe ON pe.is_local = TRUE AND pe.primary_anzsic = i.anzsic_code
                WHERE f.is_leakage = TRUE
                GROUP BY i.anzsic_title
                HAVING SUM(f.amount) > 100000
                ORDER BY spending_per_provider DESC
                LIMIT 30
            '''
        },
        {
            'id': 'geographic_flow_map',
            'type': 'choropleth',
            'title': 'Geographic Money Flows',
            'description': 'Map showing where money flows to/from Mount Isa',
            'query': '''
                SELECT
                    geo.geo_name,
                    geo.state,
                    geo.boundary,
                    SUM(CASE WHEN f.flow_direction = 'OUTFLOW' THEN f.amount ELSE 0 END) AS outflow,
                    SUM(CASE WHEN f.flow_direction = 'INFLOW' THEN f.amount ELSE 0 END) AS inflow,
                    SUM(CASE WHEN f.flow_direction = 'OUTFLOW' THEN f.amount ELSE 0 END) -
                    SUM(CASE WHEN f.flow_direction = 'INFLOW' THEN f.amount ELSE 0 END) AS net_flow
                FROM fact_economic_flows f
                LEFT JOIN dim_geography geo ON f.to_geo_id = geo.geo_id
                JOIN dim_date d ON f.date_id = d.date_id
                WHERE d.year = EXTRACT(YEAR FROM CURRENT_DATE)
                  AND geo.geo_code != 'LGA35300'
                GROUP BY geo.geo_name, geo.state, geo.boundary
                HAVING SUM(f.amount) > 0
            '''
        },
        {
            'id': 'program_breakdown',
            'type': 'bar',
            'title': 'Government Program Spending Breakdown',
            'description': 'MBS, PBS, DSS, and other government transfers',
            'query': '''
                SELECT
                    p.program_type,
                    p.program_category,
                    SUM(f.amount) AS total_spending,
                    COUNT(f.flow_id) AS transaction_count
                FROM fact_economic_flows f
                JOIN dim_program p ON f.program_id = p.program_id
                JOIN dim_date d ON f.date_id = d.date_id
                WHERE d.year = EXTRACT(YEAR FROM CURRENT_DATE)
                  AND p.program_type IN ('MBS', 'PBS', 'DSS')
                GROUP BY p.program_type, p.program_category
                ORDER BY total_spending DESC
            '''
        },
        {
            'id': 'pilot_progress',
            'type': 'gauge',
            'title': '10% Localization Pilot Progress',
            'description': 'Progress toward pilot goal',
            'query': '''
                WITH baseline AS (
                    SELECT
                        SUM(CASE WHEN is_leakage = FALSE THEN amount ELSE 0 END) /
                        NULLIF(SUM(amount), 0) * 100 AS baseline_local_pct
                    FROM fact_economic_flows f
                    JOIN dim_date d ON f.date_id = d.date_id
                    WHERE d.date < (SELECT MIN(date) FROM dim_date WHERE date >= CURRENT_DATE - INTERVAL '1 year')
                ),
                current AS (
                    SELECT
                        SUM(CASE WHEN is_leakage = FALSE THEN amount ELSE 0 END) /
                        NULLIF(SUM(amount), 0) * 100 AS current_local_pct
                    FROM fact_economic_flows f
                    JOIN dim_date d ON f.date_id = d.date_id
                    WHERE d.date >= CURRENT_DATE - INTERVAL '1 year'
                )
                SELECT
                    baseline.baseline_local_pct,
                    current.current_local_pct,
                    current.current_local_pct - baseline.baseline_local_pct AS improvement,
                    (current.current_local_pct - baseline.baseline_local_pct) / 10.0 * 100 AS percent_of_goal
                FROM baseline, current
            ''',
            'config': {
                'max': 10,
                'target': 10,
                'unit': 'percentage points'
            }
        }
    ]

    # Dashboard Layout
    LAYOUT = {
        'title': 'Mount Isa Community Economic Observatory',
        'subtitle': 'Tracking money flows and building local wealth',
        'refresh_interval': 86400,  # 24 hours in seconds
        'sections': [
            {
                'title': 'Key Metrics',
                'widgets': [
                    {'kpi': 'local_retention_rate', 'size': 'large'},
                    {'kpi': 'leakage_amount', 'size': 'large'},
                    {'kpi': 'local_business_count', 'size': 'medium'},
                    {'kpi': 'local_jobs_created', 'size': 'medium'}
                ]
            },
            {
                'title': 'Money Flows',
                'widgets': [
                    {'viz': 'money_flow_sankey', 'size': 'full'},
                    {'viz': 'local_vs_external_trend', 'size': 'half'},
                    {'viz': 'geographic_flow_map', 'size': 'half'}
                ]
            },
            {
                'title': 'Opportunities',
                'widgets': [
                    {'viz': 'leakage_treemap', 'size': 'half'},
                    {'viz': 'service_gaps_matrix', 'size': 'half'}
                ]
            },
            {
                'title': 'Pilot Progress',
                'widgets': [
                    {'viz': 'pilot_progress', 'size': 'medium'},
                    {'viz': 'program_breakdown', 'size': 'large'}
                ]
            }
        ]
    }

    @classmethod
    def get_kpi_query(cls, kpi_name: str) -> str:
        """Get SQL query for calculating a specific KPI"""
        queries = {
            'local_retention_rate': '''
                SELECT
                    SUM(CASE WHEN is_leakage = FALSE THEN amount ELSE 0 END) /
                    NULLIF(SUM(amount), 0) * 100 AS value
                FROM fact_economic_flows f
                JOIN dim_date d ON f.date_id = d.date_id
                WHERE d.year = EXTRACT(YEAR FROM CURRENT_DATE)
            ''',
            'leakage_amount': '''
                SELECT SUM(amount) AS value
                FROM fact_economic_flows f
                JOIN dim_date d ON f.date_id = d.date_id
                WHERE is_leakage = TRUE
                  AND d.year = EXTRACT(YEAR FROM CURRENT_DATE)
            ''',
            'local_business_count': '''
                SELECT COUNT(*) AS value
                FROM entities
                WHERE is_local = TRUE
                  AND status = 'ACTIVE'
            ''',
            'local_jobs_created': '''
                -- This would track new jobs from pilot interventions
                -- Implementation would depend on tracking system
                SELECT COUNT(*) AS value
                FROM (
                    SELECT entity_id
                    FROM entities
                    WHERE is_local = TRUE
                      AND created_at >= CURRENT_DATE - INTERVAL '1 year'
                ) new_businesses
            ''',
            'service_gap_count': '''
                SELECT COUNT(*) AS value
                FROM (
                    SELECT i.anzsic_code
                    FROM fact_economic_flows f
                    JOIN dim_industry i ON f.industry_id = i.industry_id
                    LEFT JOIN entities e ON e.is_local = TRUE AND e.primary_anzsic = i.anzsic_code
                    WHERE f.is_leakage = TRUE
                    GROUP BY i.anzsic_code
                    HAVING SUM(f.amount) > 100000
                       AND COUNT(DISTINCT e.entity_id) < 3
                ) gaps
            '''
        }
        return queries.get(kpi_name, '')
