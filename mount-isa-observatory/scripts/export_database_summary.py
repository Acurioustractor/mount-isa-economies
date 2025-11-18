"""
Export comprehensive database summary from Supabase
Generates community totals, category breakdowns, and per capita analysis
"""

import os
import json
from collections import defaultdict
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Population data for per capita calculations
POPULATION_DATA = {
    'Mount Isa': 18500,
    'Logan': 326615,
    'Townsville': 180820,
    'Cairns': 153075,
    'Gold Coast': 591473,
    'Ipswich': 229208,
    'Rockhampton': 80665,
    'Toowoomba': 136861,
    'Fraser Coast': 103756,
    'Palm Island': 2700,
    'Brisbane': 1200000,  # Approximate for South Brisbane area
    'Hervey Bay': 55000,  # Part of Fraser Coast
}

def connect_to_supabase() -> Client:
    """Connect to Supabase"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not url or not key:
        raise ValueError("Missing Supabase credentials. Check your .env file.")

    return create_client(url, key)

def get_all_programs(supabase: Client):
    """Fetch all programs from database"""
    try:
        result = supabase.table('documents')\
            .select('*')\
            .execute()
        return result.data
    except Exception as e:
        print(f"Error fetching programs: {e}")
        return []

def analyze_by_community(programs):
    """Analyze funding by community"""
    community_data = defaultdict(lambda: {
        'programs': [],
        'total_funding': 0,
        'program_count': 0,
        'categories': set()
    })

    for program in programs:
        locations = program.get('locations_mentioned', [])
        funding = program.get('funding_amount_extracted') or 0  # Handle None values
        categories = program.get('categories', [])

        if not locations:
            continue

        # Add to each mentioned location
        for location in locations:
            community_data[location]['programs'].append({
                'title': program.get('title', 'Unknown'),
                'amount': funding,
                'categories': categories,
                'date': program.get('published_date'),
                'source': program.get('source_organization', 'Unknown')
            })
            community_data[location]['total_funding'] += funding
            community_data[location]['program_count'] += 1
            community_data[location]['categories'].update(categories)

    return community_data

def analyze_by_category(programs):
    """Analyze funding by category"""
    category_data = defaultdict(lambda: {
        'total_funding': 0,
        'program_count': 0,
        'programs': []
    })

    for program in programs:
        categories = program.get('categories', [])
        funding = program.get('funding_amount_extracted') or 0  # Handle None values

        if not categories:
            categories = ['Uncategorized']

        for category in categories:
            category_data[category]['total_funding'] += funding
            category_data[category]['program_count'] += 1
            category_data[category]['programs'].append(program.get('title', 'Unknown'))

    return category_data

def calculate_per_capita(community_data):
    """Calculate per capita funding"""
    per_capita_data = []

    for community, data in community_data.items():
        population = POPULATION_DATA.get(community, None)
        if population and data['total_funding'] > 0:
            per_capita = data['total_funding'] / population
            per_capita_data.append({
                'community': community,
                'total_funding': data['total_funding'],
                'population': population,
                'per_capita': per_capita,
                'program_count': data['program_count']
            })

    # Sort by per capita (highest first)
    per_capita_data.sort(key=lambda x: x['per_capita'], reverse=True)

    return per_capita_data

def export_json(community_data, category_data, per_capita_data, output_file):
    """Export data as JSON for dashboard"""
    export_data = {
        'generated_at': '2025-11-17',
        'total_programs': sum(d['program_count'] for d in community_data.values()),
        'total_funding': sum(d['total_funding'] for d in community_data.values()),
        'communities': {},
        'categories': {},
        'per_capita_rankings': per_capita_data
    }

    # Convert community data
    for community, data in community_data.items():
        export_data['communities'][community] = {
            'total_funding': data['total_funding'],
            'program_count': data['program_count'],
            'categories': list(data['categories']),
            'programs': data['programs']
        }

    # Convert category data
    for category, data in category_data.items():
        export_data['categories'][category] = {
            'total_funding': data['total_funding'],
            'program_count': data['program_count']
        }

    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)

    return export_data

def print_summary(community_data, category_data, per_capita_data):
    """Print summary to console"""
    print("=" * 80)
    print("📊 QUEENSLAND YOUTH FUNDING DATABASE SUMMARY")
    print("=" * 80)
    print()

    # Overall stats
    total_programs = sum(d['program_count'] for d in community_data.values())
    total_funding = sum(d['total_funding'] for d in community_data.values())

    print(f"Total Programs: {total_programs}")
    print(f"Total Funding: ${total_funding:,.0f}")
    print(f"Communities: {len(community_data)}")
    print(f"Categories: {len(category_data)}")
    print()

    # Top communities by total funding
    print("=" * 80)
    print("🏆 TOP COMMUNITIES BY TOTAL FUNDING")
    print("=" * 80)
    print()
    print(f"{'Rank':<6} {'Community':<20} {'Programs':<10} {'Total Funding':<20}")
    print("-" * 80)

    sorted_communities = sorted(
        community_data.items(),
        key=lambda x: x[1]['total_funding'],
        reverse=True
    )[:10]

    for rank, (community, data) in enumerate(sorted_communities, 1):
        print(f"{rank:<6} {community:<20} {data['program_count']:<10} ${data['total_funding']:>18,.0f}")
    print()

    # Top communities by per capita
    print("=" * 80)
    print("👤 TOP COMMUNITIES BY PER CAPITA FUNDING")
    print("=" * 80)
    print()
    print(f"{'Rank':<6} {'Community':<20} {'Population':<12} {'Per Capita':<15} {'Total':<20}")
    print("-" * 80)

    for rank, data in enumerate(per_capita_data[:10], 1):
        print(f"{rank:<6} {data['community']:<20} {data['population']:<12,} ${data['per_capita']:>13,.2f} ${data['total_funding']:>18,.0f}")
    print()

    # Top categories
    print("=" * 80)
    print("📁 TOP FUNDING CATEGORIES")
    print("=" * 80)
    print()
    print(f"{'Rank':<6} {'Category':<30} {'Programs':<10} {'Total Funding':<20}")
    print("-" * 80)

    sorted_categories = sorted(
        category_data.items(),
        key=lambda x: x[1]['total_funding'],
        reverse=True
    )[:15]

    for rank, (category, data) in enumerate(sorted_categories, 1):
        print(f"{rank:<6} {category:<30} {data['program_count']:<10} ${data['total_funding']:>18,.0f}")
    print()

    # Mount Isa specific analysis
    if 'Mount Isa' in community_data:
        print("=" * 80)
        print("🎯 MOUNT ISA DETAILED ANALYSIS")
        print("=" * 80)
        print()

        mi_data = community_data['Mount Isa']
        mi_total = mi_data['total_funding']
        mi_population = POPULATION_DATA.get('Mount Isa', 18500)
        mi_per_capita = mi_total / mi_population

        print(f"Total Funding: ${mi_total:,.0f}")
        print(f"Programs: {mi_data['program_count']}")
        print(f"Population: {mi_population:,}")
        print(f"Per Capita: ${mi_per_capita:,.2f}")
        print()
        print("Categories:")
        for category in sorted(mi_data['categories']):
            print(f"  - {category}")
        print()

        print("Top Programs:")
        sorted_programs = sorted(mi_data['programs'], key=lambda x: x['amount'], reverse=True)
        for i, program in enumerate(sorted_programs[:10], 1):
            print(f"  {i}. {program['title']}: ${program['amount']:,.0f}")
        print()

def main():
    """Main export function"""
    print("Connecting to Supabase...")
    supabase = connect_to_supabase()
    print("✅ Connected")
    print()

    print("Fetching all programs...")
    programs = get_all_programs(supabase)
    print(f"✅ Fetched {len(programs)} programs")
    print()

    print("Analyzing data...")
    community_data = analyze_by_community(programs)
    category_data = analyze_by_category(programs)
    per_capita_data = calculate_per_capita(community_data)
    print("✅ Analysis complete")
    print()

    # Print summary
    print_summary(community_data, category_data, per_capita_data)

    # Export JSON
    output_file = 'data/funding_summary_export.json'
    export_data = export_json(community_data, category_data, per_capita_data, output_file)
    print(f"✅ Exported to {output_file}")
    print()

    # Export CSV for spreadsheet analysis
    csv_file = 'data/funding_by_community.csv'
    with open(csv_file, 'w') as f:
        f.write("Community,Programs,Total Funding,Population,Per Capita\n")
        for data in per_capita_data:
            f.write(f"{data['community']},{data['program_count']},${data['total_funding']:,.0f},{data['population']},${data['per_capita']:.2f}\n")

    print(f"✅ Exported CSV to {csv_file}")
    print()

    print("=" * 80)
    print("🎉 EXPORT COMPLETE!")
    print("=" * 80)
    print()
    print("Files created:")
    print(f"  - {output_file} (JSON for dashboard)")
    print(f"  - {csv_file} (CSV for spreadsheets)")
    print()

if __name__ == '__main__':
    main()
