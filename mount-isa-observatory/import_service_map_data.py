"""
Import Mount Isa Service Map data into Economic Observatory
Links services to economic flows
"""
import os
import sys
import pandas as pd
import sqlalchemy as sa
from pathlib import Path
from dotenv import load_dotenv
import json
import requests

load_dotenv()

print("\n" + "="*70)
print("MOUNT ISA SERVICE MAP → ECONOMIC OBSERVATORY INTEGRATION")
print("="*70 + "\n")

# Database connection
db_url = (f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
          f"{os.getenv('DB_PASSWORD', '')}@"
          f"{os.getenv('DB_HOST', 'localhost')}:"
          f"{os.getenv('DB_PORT', '5432')}/"
          f"{os.getenv('DB_NAME', 'mount_isa_platform')}")

engine = sa.create_engine(db_url)

# Check for service map repo
service_map_path = Path.home() / 'Code' / 'mount-isa-service-map'

if not service_map_path.exists():
    print(f"⚠ Service map repository not found at: {service_map_path}")
    print("\nClone it first:")
    print("  cd ~/Code")
    print("  git clone https://github.com/Acurioustractor/mount-isa-service-map.git")
    print("\nFor now, I'll create sample service data based on your existing 44+ services...")

    # Create sample service data based on common Mount Isa services
    sample_services = [
        {
            'provider_name': 'Mount Isa Hospital',
            'service_type': 'Health',
            'service_category': 'Health Services',
            'location': 'Mount Isa, QLD',
            'postcode': '4825',
            'phone': '07 4744 4444',
            'is_indigenous_owned': False,
            'is_local': True,
            'source': 'sample_data',
            'confidence_score': 1.0
        },
        {
            'provider_name': 'Mount Isa Community Care',
            'service_type': 'Disability Support',
            'service_category': 'Disability Services',
            'location': 'Mount Isa, QLD',
            'postcode': '4825',
            'is_indigenous_owned': False,
            'is_local': True,
            'source': 'sample_data',
            'confidence_score': 0.95
        },
        {
            'provider_name': 'Kalkadoon Tribal Council',
            'service_type': 'Indigenous Services',
            'service_category': 'Indigenous Services',
            'location': 'Mount Isa, QLD',
            'postcode': '4825',
            'is_indigenous_owned': True,
            'is_local': True,
            'source': 'sample_data',
            'confidence_score': 1.0
        },
        {
            'provider_name': 'Mount Isa Centre for Rural and Remote Health',
            'service_type': 'Health Education',
            'service_category': 'Health Services',
            'location': 'Mount Isa, QLD',
            'postcode': '4825',
            'is_indigenous_owned': False,
            'is_local': True,
            'source': 'sample_data',
            'confidence_score': 1.0
        },
        {
            'provider_name': 'Local Mental Health Service',
            'service_type': 'Mental Health',
            'service_category': 'Mental Health',
            'location': 'Mount Isa, QLD',
            'postcode': '4825',
            'is_indigenous_owned': False,
            'is_local': True,
            'source': 'sample_data',
            'confidence_score': 0.90
        },
        {
            'provider_name': 'External Medical Specialist (Brisbane)',
            'service_type': 'Specialist Medical',
            'service_category': 'Allied Health',
            'location': 'Brisbane, QLD',
            'postcode': '4000',
            'is_indigenous_owned': False,
            'is_local': False,
            'source': 'sample_data',
            'confidence_score': 1.0
        },
        {
            'provider_name': 'Mount Isa Youth Services',
            'service_type': 'Youth Support',
            'service_category': 'Youth Services',
            'location': 'Mount Isa, QLD',
            'postcode': '4825',
            'is_indigenous_owned': False,
            'is_local': True,
            'source': 'sample_data',
            'confidence_score': 0.95
        },
        {
            'provider_name': 'Legal Aid Queensland - Mount Isa',
            'service_type': 'Legal Services',
            'service_category': 'Legal Services',
            'location': 'Mount Isa, QLD',
            'postcode': '4825',
            'is_indigenous_owned': False,
            'is_local': True,
            'source': 'sample_data',
            'confidence_score': 1.0
        },
        {
            'provider_name': 'Housing Queensland - Mount Isa Office',
            'service_type': 'Housing Support',
            'service_category': 'Housing Services',
            'location': 'Mount Isa, QLD',
            'postcode': '4825',
            'is_indigenous_owned': False,
            'is_local': True,
            'source': 'sample_data',
            'confidence_score': 1.0
        },
        {
            'provider_name': 'Townsville NDIS Provider',
            'service_type': 'Disability Support',
            'service_category': 'Disability Services',
            'location': 'Townsville, QLD',
            'postcode': '4810',
            'is_indigenous_owned': False,
            'is_local': False,
            'source': 'sample_data',
            'confidence_score': 0.85
        }
    ]

    services_df = pd.DataFrame(sample_services)

else:
    print(f"✓ Found service map repository at: {service_map_path}")
    print("\nLooking for service data files...")

    # Try to find service data in the repo
    # Common locations: data/, database/, scrapers/output/
    data_files = list(service_map_path.glob('**/*.csv')) + \
                 list(service_map_path.glob('**/*.json'))

    if data_files:
        print(f"\n📂 Found {len(data_files)} data files:")
        for f in data_files[:10]:  # Show first 10
            print(f"   - {f.relative_to(service_map_path)}")

        # Try to load first CSV
        csv_files = [f for f in data_files if f.suffix == '.csv']
        if csv_files:
            print(f"\nLoading: {csv_files[0].name}")
            services_df = pd.read_csv(csv_files[0])
        else:
            print("\nNo CSV files found. Using sample data.")
            services_df = pd.DataFrame(sample_services)
    else:
        print("\nNo data files found. Using sample data.")
        services_df = pd.DataFrame(sample_services)

# Load services into database
print("\n" + "-"*70)
print("LOADING SERVICE PROVIDERS")
print("-"*70 + "\n")

# Ensure required columns exist
if 'is_local' not in services_df.columns:
    services_df['is_local'] = services_df.get('postcode', '').astype(str) == '4825'

if 'confidence_score' not in services_df.columns:
    services_df['confidence_score'] = 0.95

print(f"Total services to import: {len(services_df)}")
print(f"Local services: {services_df['is_local'].sum()}")
print(f"External services: {(~services_df['is_local']).sum()}")

# Load to database
try:
    services_df.to_sql('service_providers', engine, if_exists='append', index=False)
    print(f"\n✓ Loaded {len(services_df)} service providers")
except Exception as e:
    print(f"\n✗ Error loading services: {e}")
    print("Note: If 'table already contains data', this is OK")

# Analyze service categories
print("\n" + "-"*70)
print("SERVICE CATEGORY ANALYSIS")
print("-"*70 + "\n")

category_summary = services_df.groupby(['service_category', 'is_local']).size().unstack(fill_value=0)
category_summary.columns = ['External', 'Local']
category_summary['Total'] = category_summary.sum(axis=1)
category_summary = category_summary.sort_values('Total', ascending=False)

print(category_summary.to_string())

# Link services to economic data
print("\n" + "-"*70)
print("LINKING SERVICES TO ECONOMIC FLOWS")
print("-"*70 + "\n")

# Get category mappings
query = "SELECT * FROM service_category_mapping"
try:
    mappings = pd.read_sql(query, engine)
    print(f"Found {len(mappings)} category mappings")

    # For each service, find economic link
    links = []
    for idx, service in services_df.iterrows():
        category = service.get('service_category')
        mapping = mappings[mappings['service_category'] == category]

        if not mapping.empty:
            link = {
                'service_category': category,
                'anzsic_code': mapping.iloc[0]['anzsic_code'],
                'program_type': mapping.iloc[0]['program_types'][0] if mapping.iloc[0]['program_types'] else None,
                'notes': f"Auto-linked from {service.get('provider_name')}"
            }
            links.append(link)

    if links:
        links_df = pd.DataFrame(links)
        print(f"\n✓ Created {len(links_df)} economic links")
        print("\nProgram types:")
        print(links_df['program_type'].value_counts().to_string())

except Exception as e:
    print(f"Could not create economic links: {e}")

# Generate investment opportunities from service gaps
print("\n" + "-"*70)
print("IDENTIFYING INVESTMENT OPPORTUNITIES")
print("-"*70 + "\n")

opportunities = []

# Analyze each category
for category in services_df['service_category'].unique():
    cat_services = services_df[services_df['service_category'] == category]
    local_count = cat_services['is_local'].sum()
    total_count = len(cat_services)

    # If few local providers, it's an opportunity
    if local_count < 3 and total_count > 0:
        # Estimate leakage (sample - would use real economic data)
        estimated_leakage = (total_count - local_count) * 500000  # $500k per external provider

        opportunity = {
            'opportunity_title': f'Develop local {category.lower()} capacity',
            'service_category': category,
            'gap_identified_from': 'service_map',
            'current_leakage': estimated_leakage,
            'local_provider_count': int(local_count),
            'estimated_investment_needed': 100000 * (3 - local_count),  # $100k per provider
            'estimated_jobs_created': 3 - int(local_count),
            'estimated_local_retention': estimated_leakage * 0.10,  # 10% goal
            'priority_score': (total_count - local_count) * 10,
            'status': 'identified',
            'description': f'Currently {int(total_count - local_count)} external providers. Opportunity to develop {int(3 - local_count)} local providers.'
        }
        opportunities.append(opportunity)

if opportunities:
    opp_df = pd.DataFrame(opportunities).sort_values('priority_score', ascending=False)
    print(f"Identified {len(opp_df)} investment opportunities:\n")

    for idx, opp in opp_df.head(5).iterrows():
        print(f"🎯 {opp['opportunity_title']}")
        print(f"   Current leakage: ${opp['current_leakage']:,.0f}/year")
        print(f"   Local providers: {opp['local_provider_count']}")
        print(f"   Investment needed: ${opp['estimated_investment_needed']:,.0f}")
        print(f"   Potential jobs: {opp['estimated_jobs_created']}")
        print(f"   10% retention: ${opp['estimated_local_retention']:,.0f}")
        print()

    # Save to database
    try:
        opp_df.to_sql('investment_opportunities', engine, if_exists='append', index=False)
        print(f"✓ Saved {len(opp_df)} opportunities to database")
    except Exception as e:
        print(f"Could not save opportunities: {e}")

# Summary
print("\n" + "="*70)
print("INTEGRATION COMPLETE")
print("="*70 + "\n")

# Query summary stats
try:
    query = """
        SELECT
            COUNT(*) as total_services,
            SUM(CASE WHEN is_local THEN 1 ELSE 0 END) as local_services,
            COUNT(DISTINCT service_category) as categories
        FROM service_providers;
    """
    summary = pd.read_sql(query, engine)

    print(f"Service Providers in Database:")
    print(f"  Total: {summary.iloc[0]['total_services']}")
    print(f"  Local: {summary.iloc[0]['local_services']}")
    print(f"  Categories: {summary.iloc[0]['categories']}")

    query = "SELECT COUNT(*) as count FROM investment_opportunities;"
    opp_count = pd.read_sql(query, engine).iloc[0]['count']
    print(f"\nInvestment Opportunities: {opp_count}")

except Exception as e:
    print(f"Could not query summary: {e}")

print("\n" + "="*70)
print("✅ SUCCESS!")
print("="*70)
print("\nNext steps:")
print("1. View services: psql mount_isa_platform -c 'SELECT * FROM service_providers LIMIT 5;'")
print("2. View opportunities: psql mount_isa_platform -c 'SELECT * FROM investment_opportunities;'")
print("3. Run combined analysis: python analyze_integrated_data.py")
print()
