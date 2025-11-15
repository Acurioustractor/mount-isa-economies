"""
Comprehensive Data Source Integration for Mount Isa Economic Observatory
Focuses on Youth Justice, Grants, and Community Organizations
"""

# ==============================================================================
# PRIORITY DATA SOURCES - Youth Justice & Grants Focus
# ==============================================================================

DATA_SOURCES = {

    # =========================================================================
    # 1. GRANTS & FUNDING (Track Every Dollar Coming In)
    # =========================================================================

    "qld_youth_justice_grants": {
        "name": "Queensland Youth Justice Grant Programs",
        "priority": "CRITICAL",
        "update_frequency": "Quarterly",
        "sources": [
            {
                "program": "On Country Program",
                "total_funding": 2_250_000,  # $2.25M over 3 years
                "location": "Mount Isa",
                "recipients": ["Kalkadoon Elders", "Local Indigenous Organizations"],
                "url": "https://statements.qld.gov.au/statements/89527"
            },
            {
                "program": "Back to Community (Save the Children)",
                "amount": 300_000,
                "focus": "Youth detention reintegration",
                "beneficiaries": "Mount Isa, Doomadgee, Mornington Island youth",
                "url": "https://statements.qld.gov.au/statements/97577"
            },
            {
                "program": "Proud Warrior Project (QLD Youth Services)",
                "amount": 128_592,
                "focus": "Indigenous youth at risk, school disengagement",
                "location": "Mount Isa"
            },
            {
                "program": "Specialist Youth Violence Prevention (SYVP)",
                "focus": "Young men 13-18, intimate partner violence prevention",
                "partner": "Natjul Indigenous Performing Arts",
                "location": "Mount Isa & Doomadgee"
            }
        ],
        "data_collection": {
            "method": "Web scraping + manual tracking",
            "endpoints": [
                "https://www.youthjustice.qld.gov.au/partnerships/grants/",
                "https://statements.qld.gov.au/",
                "https://www.grants.services.qld.gov.au/"
            ],
            "fields_to_track": [
                "grant_name",
                "recipient_organization",
                "amount",
                "start_date",
                "end_date",
                "objectives",
                "location",
                "outcomes_reported",
                "is_indigenous_led"
            ]
        }
    },

    "grantconnect": {
        "name": "GrantConnect (Commonwealth Grants)",
        "priority": "HIGH",
        "api": "https://www.grants.gov.au/",
        "description": "Federal grants to Mount Isa organizations",
        "search_filters": {
            "location": ["Mount Isa", "4825", "North West Queensland"],
            "categories": [
                "Indigenous Affairs",
                "Community Development",
                "Youth Services",
                "Justice Programs",
                "Health Services",
                "Education & Training"
            ]
        },
        "data_collection": {
            "method": "Web scraping (no public API)",
            "url": "https://www.grants.gov.au/",
            "frequency": "Monthly"
        }
    },

    "qld_grants_finder": {
        "name": "Queensland Government Grants Finder",
        "priority": "HIGH",
        "url": "https://www.grants.services.qld.gov.au/",
        "programs": [
            "Community-based Crime Action grants (up to $75k)",
            "Kickstarter program (up to $300k)",
            "Targeted Responses to Youth Crime (up to $300k)",
            "Indigenous Economic Development grants",
            "First Nations Justice Program grants"
        ],
        "data_collection": {
            "method": "Web scraping + API (if available)",
            "frequency": "Weekly"
        }
    },

    # =========================================================================
    # 2. CHARITY & NON-PROFIT DATA
    # =========================================================================

    "acnc": {
        "name": "Australian Charities and Not-for-profits Commission",
        "priority": "CRITICAL",
        "description": "60,000+ registered charities with financial data",
        "api": "Open data downloads + Charity Data Hub",
        "url": "https://www.acnc.gov.au/tools/other-resources/charity-data-hub",
        "data_available": {
            "charity_register": "All registered charities",
            "annual_information_statements": "Financial data, programs, locations",
            "charity_data_cube": "Interactive analytics"
        },
        "mount_isa_filters": {
            "location": ["Mount Isa", "4825", "North West Queensland"],
            "service_types": [
                "Youth Services",
                "Indigenous Services",
                "Justice & Legal Services",
                "Community Development",
                "Family & Children Services",
                "Mental Health",
                "Disability Services"
            ]
        },
        "data_collection": {
            "method": "Bulk download CSV + API queries",
            "url": "https://data.gov.au/data/dataset/acnc-register",
            "frequency": "Monthly",
            "fields": [
                "charity_name",
                "abn",
                "charity_type",
                "operating_location",
                "total_revenue",
                "total_expenses",
                "programs_description",
                "beneficiaries",
                "staff_count",
                "volunteer_count"
            ]
        }
    },

    "oric": {
        "name": "Office of the Registrar of Indigenous Corporations",
        "priority": "CRITICAL",
        "description": "Indigenous corporations financial data",
        "url": "https://www.oric.gov.au/",
        "data_available": {
            "public_register": "All registered Indigenous corporations",
            "financial_reports": "Annual reports for larger corporations",
            "contact_details": "Office locations, key contacts"
        },
        "mount_isa_search": {
            "keywords": ["Kalkadoon", "Mount Isa", "North West Queensland"],
            "types": ["Community corporations", "Land councils", "Art centers"]
        },
        "data_collection": {
            "method": "Web scraping (no public API)",
            "frequency": "Quarterly"
        }
    },

    # =========================================================================
    # 3. QUEENSLAND GOVERNMENT DATA
    # =========================================================================

    "qld_open_data": {
        "name": "Queensland Open Data Portal",
        "priority": "HIGH",
        "api": "CKAN API",
        "url": "https://www.data.qld.gov.au/",
        "key_datasets": [
            {
                "name": "Regional Economic Profiles",
                "dataset_id": "regional-economic-profiles-for-agriculture-queensland-series",
                "relevance": "Mount Isa economic baseline"
            },
            {
                "name": "Youth Justice Statistics",
                "search": "youth justice detention Queensland",
                "relevance": "Track detention rates, reoffending"
            },
            {
                "name": "Department of Youth Justice Service Locations",
                "relevance": "Map government youth justice services"
            },
            {
                "name": "Queensland Government Contracts",
                "dataset_id": "queensland-government-awarded-contracts",
                "relevance": "Track procurement to local orgs"
            },
            {
                "name": "Queensland Health Facilities",
                "relevance": "Mental health, youth health services"
            }
        ],
        "data_collection": {
            "method": "CKAN API (already implemented!)",
            "library": "ckanapi",
            "frequency": "Weekly"
        }
    },

    "qld_productivity_commission": {
        "name": "Queensland Productivity Commission Data",
        "priority": "MEDIUM",
        "note": "Now part of Queensland Treasury - Office of Productivity",
        "url": "https://www.qpc.qld.gov.au/",
        "data_available": {
            "reports": "Regional productivity analysis",
            "consultancies": "Economic research commissioned",
            "submissions": "Stakeholder input on economic issues"
        },
        "mount_isa_relevance": {
            "regional_reports": "North West Queensland economic analysis",
            "remote_communities": "Research on remote economic development"
        },
        "data_collection": {
            "method": "PDF report extraction + dataset downloads",
            "frequency": "Quarterly"
        }
    },

    # =========================================================================
    # 4. YOUTH JUSTICE SPECIFIC
    # =========================================================================

    "youth_justice_qld": {
        "name": "Department of Youth Justice and Victim Support",
        "priority": "CRITICAL",
        "url": "https://www.youthjustice.qld.gov.au/",
        "data_available": {
            "service_locations": "Youth justice centers, community programs",
            "grant_programs": "Funded initiatives (as above)",
            "partnerships": "Community organizations working in youth justice",
            "statistics": "Youth detention rates, reoffending, demographics"
        },
        "mount_isa_programs": {
            "On_Country": "$2.25M - Kalkadoon Elder-led",
            "SYVP": "Violence prevention - Natjul Arts partnership",
            "Proud_Warrior": "$128k - QLD Youth Services",
            "Back_to_Community": "$300k - Save the Children"
        },
        "data_collection": {
            "method": "Web scraping + manual tracking of announcements",
            "frequency": "Monthly",
            "track": [
                "new_grants_announced",
                "program_outcomes",
                "service_provider_changes",
                "youth_in_detention_from_mount_isa"
            ]
        }
    },

    "australian_institute_criminology": {
        "name": "Australian Institute of Criminology",
        "priority": "MEDIUM",
        "url": "https://www.aic.gov.au/",
        "data_available": {
            "youth_justice_statistics": "National & state-level data",
            "research_reports": "Evidence-based interventions",
            "program_evaluations": "What works in youth justice"
        },
        "data_collection": {
            "method": "Research paper extraction + datasets",
            "frequency": "Quarterly"
        }
    },

    # =========================================================================
    # 5. YOUR EXISTING SERVICE MAP DATA
    # =========================================================================

    "mount_isa_service_map": {
        "name": "Your Service Map Database (183+ services, 127+ interviews)",
        "priority": "CRITICAL - YOU ALREADY HAVE THIS!",
        "database": "PostgreSQL",
        "github": "https://github.com/Acurioustractor/mount-isa-service-map",
        "data_available": {
            "services": "183+ mapped services across health, youth, justice, Indigenous",
            "community_interviews": "127+ interviews with AI sentiment analysis",
            "service_gaps": "Identified gaps from community voice",
            "confidence_scores": "Service data quality metrics"
        },
        "export_needed": {
            "method": "PostgreSQL export to CSV",
            "commands": [
                "pg_dump mount_isa_services --table=services --data-only --format=csv > services.csv",
                "pg_dump mount_isa_services --table=community_interviews --data-only --format=csv > interviews.csv"
            ]
        },
        "integration_priority": "WEEK 1 - Export and load into Economic Observatory"
    },

    # =========================================================================
    # 6. ADDITIONAL VALUABLE SOURCES
    # =========================================================================

    "abs_census": {
        "name": "ABS Census Data for Mount Isa (LGA35300)",
        "priority": "HIGH",
        "url": "https://www.abs.gov.au/census",
        "data_available": {
            "population": "Demographics by age, Indigenous status",
            "income": "Household income distribution",
            "employment": "Labor force status, industries",
            "housing": "Tenure, affordability",
            "education": "Qualifications, school attendance"
        },
        "api": "ABS SDMX API (beta)",
        "data_collection": {
            "method": "API queries + CSV downloads",
            "frequency": "Annual (Census every 5 years)"
        }
    },

    "closing_the_gap": {
        "name": "Closing the Gap Data",
        "priority": "HIGH",
        "url": "https://www.closingthegap.gov.au/",
        "data_available": {
            "targets": "Progress on 17 socioeconomic targets",
            "regional_data": "Some data available by LGA",
            "justice_target": "Target 11 - Youth detention rates"
        },
        "mount_isa_relevance": {
            "indigenous_population": "~20% of Mount Isa",
            "justice_outcomes": "Track progress on detention reduction",
            "health_outcomes": "Linked to service access"
        }
    },

    "family_responsibilities_commission": {
        "name": "Family Responsibilities Commission (if applicable)",
        "priority": "MEDIUM",
        "note": "Operates in some QLD Indigenous communities",
        "check": "Does FRC operate in Mount Isa or nearby?",
        "data": "Community wellbeing reports if available"
    }
}

# ==============================================================================
# INTEGRATION WORKFLOW
# ==============================================================================

INTEGRATION_WORKFLOW = {

    "week_1": {
        "priority": "Get Your Existing Data Into Observatory",
        "tasks": [
            {
                "task": "Export service map database",
                "method": "Connect to PostgreSQL, export CSVs",
                "output": "services.csv, interviews.csv, service_gaps.csv"
            },
            {
                "task": "Import into Economic Observatory",
                "script": "import_service_map_data.py",
                "tables": ["service_providers", "community_interviews"]
            },
            {
                "task": "Match services to ACNC charity register",
                "method": "ABN matching + name fuzzy matching",
                "get_financials": "Link to ACNC revenue/expense data"
            }
        ]
    },

    "week_2": {
        "priority": "Track All Youth Justice Money",
        "tasks": [
            {
                "task": "Scrape Queensland Youth Justice grants",
                "sources": [
                    "https://www.youthjustice.qld.gov.au/partnerships/grants/",
                    "https://statements.qld.gov.au/"
                ],
                "output": "youth_justice_grants.csv"
            },
            {
                "task": "Download ACNC charity data",
                "method": "Bulk CSV download from data.gov.au",
                "filter": "Mount Isa + youth justice categories",
                "output": "acnc_mount_isa_charities.csv"
            },
            {
                "task": "Create grants tracking table",
                "fields": [
                    "grant_name",
                    "amount",
                    "recipient_abn",
                    "start_date",
                    "end_date",
                    "focus_area",
                    "is_indigenous_led",
                    "outcomes"
                ]
            }
        ]
    },

    "week_3": {
        "priority": "Build Complete Service + Funding Picture",
        "tasks": [
            {
                "task": "Link services to funding sources",
                "logic": "Match organization ABN to grant recipients",
                "output": "service_funding_links table"
            },
            {
                "task": "Calculate total youth justice investment",
                "components": [
                    "State grants (On Country, Proud Warrior, etc.)",
                    "Commonwealth grants (GrantConnect)",
                    "ACNC charity revenue (youth justice orgs)",
                    "Government service delivery (detention centers, case workers)"
                ],
                "estimate": "$10M+ annually in Mount Isa region"
            },
            {
                "task": "Identify service delivery gaps vs funding",
                "analysis": "Where is money going vs where community needs are?",
                "output": "justice_investment_gaps.csv"
            }
        ]
    },

    "week_4": {
        "priority": "Create Justice-Focused Dashboard",
        "visualizations": [
            {
                "name": "Youth Justice Money Flows",
                "type": "Sankey diagram",
                "shows": "Government → Orgs → Young People"
            },
            {
                "name": "Service Gaps vs Investment",
                "type": "Heatmap",
                "shows": "Which needs have funding, which don't"
            },
            {
                "name": "Indigenous-Led vs External",
                "type": "Pie chart",
                "shows": "% of youth justice $ going to Indigenous orgs"
            },
            {
                "name": "Outcomes Tracker",
                "type": "Time series",
                "shows": "Youth detention rates, reoffending, wellbeing"
            }
        ]
    }
}

# ==============================================================================
# PRIORITY ANALYSIS QUESTIONS
# ==============================================================================

ANALYSIS_QUESTIONS = {

    "money_flows": [
        "How much total $ is invested in youth justice in Mount Isa annually?",
        "What % goes to Indigenous-led organizations vs external orgs?",
        "Which organizations are receiving the most funding?",
        "Is funding aligned with community-identified needs (from 127 interviews)?",
        "Where are the funding gaps?"
    ],

    "service_capacity": [
        "How many youth justice services exist? (from your 183 services)",
        "Which are local vs fly-in?",
        "What's the service gap for youth mental health?",
        "Are there enough culturally safe services?",
        "What's the ratio of funding to service capacity?"
    ],

    "justice_outcomes": [
        "Are youth detention rates decreasing?",
        "What's the reoffending rate for Mount Isa youth?",
        "How many young people are served by funded programs?",
        "What outcomes are programs achieving?",
        "Is community wellbeing improving?"
    ],

    "sovereignty_power": [
        "Do Kalkadoon Elders control youth justice decisions?",
        "What % of youth justice workers are local/Indigenous?",
        "Are Traditional Owners co-designing programs?",
        "Is cultural knowledge valued in service delivery?",
        "Do young people have voice in program design?"
    ]
}

# ==============================================================================
# OUTPUT: What You'll Be Able to See
# ==============================================================================

DASHBOARD_OUTPUTS = """
With all this data integrated, your dashboard will show:

1. TOTAL YOUTH JUSTICE INVESTMENT: ~$10M+ annually
   - State government: $X
   - Commonwealth: $Y
   - Charity/NFP: $Z
   - Breakdown by program

2. ORGANIZATION MAP
   - 183+ total services
   - XX youth justice specific
   - YY Indigenous-led
   - Financial data for each (from ACNC)

3. MONEY FLOWS
   - Sankey: Govt → Orgs → Programs → Young People
   - Track every dollar
   - Identify leakage ($ going to external orgs)

4. SERVICE GAPS
   - Community needs (from 127 interviews)
   - vs Current services (from service map)
   - vs Funding allocation (from grants data)
   - = Investment opportunities

5. JUSTICE METRICS
   - Youth detention rates
   - Reoffending statistics
   - Service access by demographics
   - Cultural safety scores
   - Community wellbeing trends

6. SOVEREIGNTY INDICATORS
   - % Indigenous-led programs
   - Elder involvement
   - Youth voice in design
   - Local employment
   - Cultural knowledge integration

RESULT: Complete picture of youth justice ecosystem + power to transform it
"""

if __name__ == "__main__":
    print("Mount Isa Youth Justice Data Integration Plan")
    print("=" * 70)
    print("\nPriority Data Sources:")
    for key, source in DATA_SOURCES.items():
        if source.get('priority') in ['CRITICAL', 'HIGH']:
            print(f"\n{source['name']}")
            print(f"  Priority: {source['priority']}")
            if 'amount' in str(source):
                print(f"  💰 Includes funding data")
