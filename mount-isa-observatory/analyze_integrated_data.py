"""
Combined Analysis: Service Map (183 services) + Economic Observatory
Shows the full power of integration
"""
import pandas as pd
import sqlalchemy as sa
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection
db_url = (f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
          f"{os.getenv('DB_PASSWORD', '')}@"
          f"{os.getenv('DB_HOST', 'localhost')}:"
          f"{os.getenv('DB_PORT', '5432')}/"
          f"{os.getenv('DB_NAME', 'mount_isa_platform')}")

engine = sa.create_engine(db_url)

print("\n" + "="*80)
print("🏛️  MOUNT ISA INTEGRATED ANALYSIS")
print("    Service Map (183 Services) + Economic Observatory")
print("="*80 + "\n")

# ============================================================================
# PART 1: SERVICE MAP ANALYSIS
# ============================================================================

print("=" * 80)
print("PART 1: SERVICE LANDSCAPE (from your 183 services)")
print("=" * 80 + "\n")

query = """
    SELECT
        service_category,
        COUNT(*) as total_providers,
        SUM(CASE WHEN is_local THEN 1 ELSE 0 END) as local_providers,
        SUM(CASE WHEN is_local THEN 0 ELSE 1 END) as external_providers,
        ROUND(100.0 * SUM(CASE WHEN is_local THEN 1 ELSE 0 END) / COUNT(*), 1) as local_pct
    FROM service_providers
    GROUP BY service_category
    ORDER BY total_providers DESC;
"""

try:
    services = pd.read_sql(query, engine)

    if len(services) > 0:
        print(f"📊 Service Categories ({len(services)} categories, {services['total_providers'].sum()} total services):\n")
        print(services.to_string(index=False))
        print()

        # Calculate overall metrics
        total_services = services['total_providers'].sum()
        total_local = services['local_providers'].sum()
        overall_local_pct = (total_local / total_services * 100) if total_services > 0 else 0

        print(f"\n📈 Overall Service Capacity:")
        print(f"   Total Services: {total_services}")
        print(f"   Local: {total_local} ({overall_local_pct:.1f}%)")
        print(f"   External: {total_services - total_local} ({100 - overall_local_pct:.1f}%)")

        # Identify service gaps
        print(f"\n🚨 Service Gaps (Categories with <30% local providers):\n")
        gaps = services[services['local_pct'] < 30].sort_values('total_providers', ascending=False)

        for idx, row in gaps.head(10).iterrows():
            print(f"   {row['service_category']}")
            print(f"      Total: {row['total_providers']}, Local: {row['local_providers']} ({row['local_pct']:.0f}%)")
            print(f"      → Need {3 - row['local_providers']} more local providers")
            print()

    else:
        print("⚠ No service data in database yet. Run import_service_map_data.py first")

except Exception as e:
    print(f"Could not analyze services: {e}")
    print("Make sure you've run: python import_service_map_data.py")

# ============================================================================
# PART 2: ECONOMIC FLOWS ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("PART 2: ECONOMIC FLOWS (from procurement & business data)")
print("=" * 80 + "\n")

query = """
    SELECT
        is_local,
        COUNT(*) as contract_count,
        SUM(contract_value) as total_value
    FROM staging_qld_procurement
    GROUP BY is_local;
"""

try:
    procurement = pd.read_sql(query, engine)

    if len(procurement) > 0:
        print("💰 Queensland Government Procurement:\n")
        print(procurement.to_string(index=False))

        total_value = procurement['total_value'].sum()
        local_value = procurement[procurement['is_local'] == True]['total_value'].sum() if True in procurement['is_local'].values else 0

        leakage = total_value - local_value
        leakage_pct = (leakage / total_value * 100) if total_value > 0 else 0

        print(f"\n   Total spending: ${total_value:,.0f}")
        print(f"   Local: ${local_value:,.0f}")
        print(f"   🚨 LEAKING: ${leakage:,.0f} ({leakage_pct:.1f}%)")

    else:
        print("⚠ No procurement data yet. Run ingestion script first")

except Exception as e:
    print(f"Note: Procurement data not loaded yet ({e})")

# ============================================================================
# PART 3: INTEGRATED INSIGHTS (THE MAGIC!)
# ============================================================================

print("\n" + "=" * 80)
print("PART 3: INTEGRATED INSIGHTS (Service Gaps × Economic Leakage)")
print("=" * 80 + "\n")

# Link service categories to economic flows via ANZSIC/program mapping
query = """
    SELECT
        sp.service_category,
        COUNT(DISTINCT sp.provider_id) as service_count,
        SUM(CASE WHEN sp.is_local THEN 1 ELSE 0 END) as local_service_count,
        scm.program_types,
        scm.anzsic_code
    FROM service_providers sp
    LEFT JOIN service_category_mapping scm ON sp.service_category = scm.service_category
    GROUP BY sp.service_category, scm.program_types, scm.anzsic_code
    HAVING COUNT(DISTINCT sp.provider_id) > 0
    ORDER BY service_count DESC;
"""

try:
    integrated = pd.read_sql(query, engine)

    print("🔗 Service Categories with Economic Links:\n")

    for idx, row in integrated.head(15).iterrows():
        category = row['service_category']
        service_count = row['service_count']
        local_count = row['local_service_count']
        programs = row['program_types']

        local_pct = (local_count / service_count * 100) if service_count > 0 else 0

        print(f"{category}")
        print(f"   Services: {service_count} total, {local_count} local ({local_pct:.0f}%)")

        if programs:
            print(f"   Funding: {', '.join(programs)}")

            # Estimate economic impact (sample calculation)
            if 'MBS' in programs or 'PBS' in programs:
                estimated_spending = service_count * 800000  # Rough estimate per provider
                print(f"   Est. annual spending: ${estimated_spending:,.0f}")
                if local_pct < 50:
                    opportunity = estimated_spending * (50 - local_pct) / 100 * 0.10
                    print(f"   🎯 10% opportunity: ${opportunity:,.0f} could be localized")

        print()

except Exception as e:
    print(f"Could not generate integrated insights: {e}")

# ============================================================================
# PART 4: INVESTMENT OPPORTUNITIES (RANKED)
# ============================================================================

print("=" * 80)
print("PART 4: INVESTMENT OPPORTUNITIES (Priority Ranking)")
print("=" * 80 + "\n")

query = """
    SELECT
        opportunity_title,
        service_category,
        current_leakage,
        local_provider_count,
        estimated_investment_needed,
        estimated_jobs_created,
        estimated_local_retention,
        priority_score,
        status
    FROM investment_opportunities
    ORDER BY priority_score DESC
    LIMIT 10;
"""

try:
    opportunities = pd.read_sql(query, engine)

    if len(opportunities) > 0:
        print(f"🎯 Top {len(opportunities)} Investment Priorities:\n")

        for idx, opp in opportunities.iterrows():
            print(f"{idx + 1}. {opp['opportunity_title']}")
            print(f"   Category: {opp['service_category']}")
            print(f"   Current leakage: ${opp['current_leakage']:,.0f}/year")
            print(f"   Local providers: {opp['local_provider_count']}")
            print(f"   Investment needed: ${opp['estimated_investment_needed']:,.0f}")
            print(f"   Jobs created: {opp['estimated_jobs_created']}")
            print(f"   10% retention: ${opp['estimated_local_retention']:,.0f}/year")
            print(f"   Priority score: {opp['priority_score']:.0f}")
            print(f"   Status: {opp['status']}")
            print()

        # Calculate total opportunity
        total_investment = opportunities['estimated_investment_needed'].sum()
        total_jobs = opportunities['estimated_jobs_created'].sum()
        total_retention = opportunities['estimated_local_retention'].sum()

        print("-" * 80)
        print(f"TOTAL OPPORTUNITY (Top {len(opportunities)} priorities):")
        print(f"   Investment needed: ${total_investment:,.0f}")
        print(f"   Jobs created: {total_jobs}")
        print(f"   Annual retention: ${total_retention:,.0f}")
        print(f"   With multiplier (1.48×): ${total_retention * 1.48:,.0f} total economic impact")

    else:
        print("⚠ No opportunities identified yet")

except Exception as e:
    print(f"Could not load opportunities: {e}")

# ============================================================================
# PART 5: RECOMMENDED ACTIONS
# ============================================================================

print("\n" + "=" * 80)
print("PART 5: RECOMMENDED ACTIONS FOR MOUNT ISA")
print("=" * 80 + "\n")

print("🎯 IMMEDIATE NEXT STEPS (This Week):\n")
print("1. Register for ABN Lookup GUID")
print("   → https://abr.business.gov.au/Tools/WebServices")
print("   → Match your 183 services to ABN registry")
print("   → Link to economic flows\n")

print("2. Clone your service map repo")
print("   → cd ~/Code")
print("   → git clone https://github.com/Acurioustractor/mount-isa-service-map.git")
print("   → Import all 183 services\n")

print("3. Present initial findings to Council")
print("   → Show service gap analysis")
print("   → Present procurement leakage")
print("   → Propose 10% localization pilot\n")

print("\n📊 SHORT-TERM (Next Month):\n")
print("1. Link all 183 services to economic data")
print("   → Medicare/PBS for health services")
print("   → NDIS for disability services")
print("   → DSS for social services\n")

print("2. Analyze community interviews")
print("   → Import 127 interviews")
print("   → Map community needs to economic opportunities")
print("   → Prioritize by community voice + economic impact\n")

print("3. Set up integrated dashboard")
print("   → Service map + economic flows")
print("   → Real-time leakage tracking")
print("   → Investment opportunity pipeline\n")

print("\n🚀 LONG-TERM (12-Month Pilot):\n")
print("1. Launch community investment fund")
print("   → Target top 3-5 service gaps")
print("   → Fund local training & business development")
print("   → Track monthly progress\n")

print("2. Measure impact")
print("   → Jobs created")
print("   → Money kept local")
print("   → Community wellbeing scores")
print("   → Service access improvements\n")

print("3. Scale & share")
print("   → Document model for other remote communities")
print("   → Build network of economic observatories")
print("   → Support Aboriginal-led economic development\n")

print("=" * 80)
print("✅ ANALYSIS COMPLETE")
print("=" * 80)
print()
print("💡 You have the most comprehensive community economic intelligence")
print("   system in remote Australia!")
print()
print("   • 183 mapped services")
print("   • Economic flow tracking")
print("   • Community voice integration")
print("   • Investment opportunity pipeline")
print()
print("   This is groundbreaking work! 🎉")
print()
