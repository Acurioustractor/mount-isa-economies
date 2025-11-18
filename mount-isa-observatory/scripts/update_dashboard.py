"""
Update dashboard with live data from Supabase
Regenerates the funding-dashboard.js file with current database totals
"""

import os
import json
from collections import defaultdict
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Population data
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
    'Brisbane': 1200000,
}

def connect_to_supabase() -> Client:
    """Connect to Supabase"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    return create_client(url, key)

def get_all_programs(supabase: Client):
    """Fetch all programs"""
    result = supabase.table('documents').select('*').execute()
    return result.data

def analyze_communities(programs):
    """Analyze programs by community"""
    community_data = {}

    for program in programs:
        locations = program.get('locations_mentioned', [])
        funding = program.get('funding_amount_extracted') or 0  # Handle None values
        categories = program.get('categories', [])
        title = program.get('title', 'Unknown')

        for location in locations:
            if location not in community_data:
                community_data[location] = {
                    'name': location,
                    'totalFunding': 0,
                    'programs': 0,
                    'population': POPULATION_DATA.get(location, 0),
                    'programs_detail': [],
                    'categories': set()
                }

            community_data[location]['totalFunding'] += funding
            community_data[location]['programs'] += 1
            community_data[location]['categories'].update(categories)

            # Add program detail
            program_type = 'Other'
            if 'Co-Responder' in categories:
                program_type = 'Co-Responder'
            elif 'On-Country' in categories:
                program_type = 'On-Country'
            elif 'Education' in categories:
                program_type = 'Education'
            elif 'Mental Health' in categories or 'headspace' in categories:
                program_type = 'Mental Health'
            elif 'PCYC' in categories:
                program_type = 'PCYC'
            elif 'Youth Housing' in categories:
                program_type = 'Housing'

            community_data[location]['programs_detail'].append({
                'name': title,
                'amount': funding,
                'type': program_type
            })

    # Calculate per capita
    for location, data in community_data.items():
        if data['population'] > 0:
            data['perCapita'] = int(data['totalFunding'] / data['population'])
        else:
            data['perCapita'] = 0

        # Convert categories set to list
        data['categories'] = list(data['categories'])

        # Mark Mount Isa as highlight
        data['isHighlight'] = (location == 'Mount Isa')

    return community_data

def generate_dashboard_js(community_data):
    """Generate JavaScript file for dashboard"""

    # Convert to list and sort by total funding
    communities_list = sorted(
        community_data.values(),
        key=lambda x: x['totalFunding'],
        reverse=True
    )

    # Take top 15 communities
    top_communities = communities_list[:15]

    # Calculate totals
    total_funding = sum(c['totalFunding'] for c in top_communities)
    total_programs = sum(c['programs'] for c in top_communities)
    avg_per_capita = sum(c['perCapita'] for c in top_communities if c['perCapita'] > 0) / len([c for c in top_communities if c['perCapita'] > 0])

    # Generate JS
    js_content = f"""/**
 * Mount Isa Economic Observatory - Funding Dashboard Data
 * Auto-generated from Supabase database
 * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */

// Communities data with funding totals
const communitiesData = {json.dumps(top_communities, indent=2)};

// Summary statistics
const summaryStats = {{
    totalFunding: {total_funding},
    totalPrograms: {total_programs},
    communitiesTracked: {len(top_communities)},
    averagePerCapita: {int(avg_per_capita)}
}};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {{
    initializeDashboard(communitiesData, summaryStats);
}});

function initializeDashboard(communities, stats) {{
    // Update mega stats
    document.querySelector('.mega-stats .number').textContent = `$$${{(stats.totalFunding / 1000000).toFixed(1)}}M`;

    // Create charts
    createFundingByLocationChart(communities);
    createPerCapitaChart(communities);
    createProgramDistributionChart(communities);
    createCategoryBreakdownChart(communities);
    createTimelineChart(communities);
    createTopProgramsChart(communities);

    // Create community cards
    createCommunityCards(communities);
}}

function createFundingByLocationChart(communities) {{
    const ctx = document.getElementById('fundingByLocation');
    if (!ctx) return;

    // Sort by funding
    const sorted = [...communities].sort((a, b) => b.totalFunding - a.totalFunding);

    new Chart(ctx, {{
        type: 'bar',
        data: {{
            labels: sorted.map(c => c.name),
            datasets: [{{
                label: 'Total Funding',
                data: sorted.map(c => c.totalFunding),
                backgroundColor: sorted.map(c => c.isHighlight ? '#9333ea' : '#a78bfa'),
                borderColor: sorted.map(c => c.isHighlight ? '#7e22ce' : '#8b5cf6'),
                borderWidth: 2
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ display: false }},
                tooltip: {{
                    callbacks: {{
                        label: function(context) {{
                            return '$' + context.parsed.y.toLocaleString();
                        }}
                    }}
                }}
            }},
            scales: {{
                y: {{
                    beginAtZero: true,
                    ticks: {{
                        callback: function(value) {{
                            return '$' + (value / 1000000).toFixed(0) + 'M';
                        }}
                    }}
                }}
            }}
        }}
    }});
}}

function createPerCapitaChart(communities) {{
    const ctx = document.getElementById('perCapitaChart');
    if (!ctx) return;

    // Filter communities with population data and sort by per capita
    const withPopulation = communities.filter(c => c.perCapita > 0);
    const sorted = [...withPopulation].sort((a, b) => b.perCapita - a.perCapita).slice(0, 10);

    new Chart(ctx, {{
        type: 'horizontalBar',
        data: {{
            labels: sorted.map(c => c.name),
            datasets: [{{
                label: 'Per Capita Funding',
                data: sorted.map(c => c.perCapita),
                backgroundColor: sorted.map(c => c.isHighlight ? '#9333ea' : '#c4b5fd'),
                borderColor: sorted.map(c => c.isHighlight ? '#7e22ce' : '#a78bfa'),
                borderWidth: 2
            }}]
        }},
        options: {{
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ display: false }},
                tooltip: {{
                    callbacks: {{
                        label: function(context) {{
                            return '$' + context.parsed.x.toLocaleString() + ' per person';
                        }}
                    }}
                }}
            }},
            scales: {{
                x: {{
                    beginAtZero: true,
                    ticks: {{
                        callback: function(value) {{
                            return '$' + value.toLocaleString();
                        }}
                    }}
                }}
            }}
        }}
    }});
}}

function createProgramDistributionChart(communities) {{
    const ctx = document.getElementById('programDistribution');
    if (!ctx) return;

    new Chart(ctx, {{
        type: 'doughnut',
        data: {{
            labels: communities.map(c => c.name).slice(0, 8),
            datasets: [{{
                data: communities.map(c => c.programs).slice(0, 8),
                backgroundColor: [
                    '#9333ea', '#a78bfa', '#c4b5fd', '#ddd6fe',
                    '#7c3aed', '#8b5cf6', '#a855f7', '#c084fc'
                ]
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    position: 'right',
                    labels: {{
                        boxWidth: 15,
                        padding: 10
                    }}
                }}
            }}
        }}
    }});
}}

function createCategoryBreakdownChart(communities) {{
    const ctx = document.getElementById('categoryBreakdown');
    if (!ctx) return;

    // Aggregate categories across all communities
    const categoryTotals = {{}};
    communities.forEach(c => {{
        c.programs_detail.forEach(p => {{
            if (!categoryTotals[p.type]) categoryTotals[p.type] = 0;
            categoryTotals[p.type] += p.amount;
        }});
    }});

    const categories = Object.keys(categoryTotals).sort((a, b) => categoryTotals[b] - categoryTotals[a]);

    new Chart(ctx, {{
        type: 'pie',
        data: {{
            labels: categories,
            datasets: [{{
                data: categories.map(c => categoryTotals[c]),
                backgroundColor: [
                    '#9333ea', '#a78bfa', '#c4b5fd', '#ddd6fe',
                    '#7c3aed', '#8b5cf6', '#a855f7', '#c084fc'
                ]
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    position: 'right'
                }},
                tooltip: {{
                    callbacks: {{
                        label: function(context) {{
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': $' + context.parsed.toLocaleString() + ' (' + percentage + '%)';
                        }}
                    }}
                }}
            }}
        }}
    }});
}}

function createTimelineChart(communities) {{
    // Placeholder for timeline chart
    console.log('Timeline chart not yet implemented');
}}

function createTopProgramsChart(communities) {{
    const ctx = document.getElementById('topPrograms');
    if (!ctx) return;

    // Collect all programs
    const allPrograms = [];
    communities.forEach(c => {{
        c.programs_detail.forEach(p => {{
            allPrograms.push({{ ...p, community: c.name }});
        }});
    }});

    // Sort by amount and take top 10
    const topPrograms = allPrograms.sort((a, b) => b.amount - a.amount).slice(0, 10);

    new Chart(ctx, {{
        type: 'horizontalBar',
        data: {{
            labels: topPrograms.map(p => p.name.substring(0, 40) + '...'),
            datasets: [{{
                label: 'Funding Amount',
                data: topPrograms.map(p => p.amount),
                backgroundColor: '#a78bfa',
                borderColor: '#8b5cf6',
                borderWidth: 2
            }}]
        }},
        options: {{
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ display: false }},
                tooltip: {{
                    callbacks: {{
                        label: function(context) {{
                            return '$' + context.parsed.x.toLocaleString();
                        }},
                        afterLabel: function(context) {{
                            return topPrograms[context.dataIndex].community;
                        }}
                    }}
                }}
            }},
            scales: {{
                x: {{
                    beginAtZero: true,
                    ticks: {{
                        callback: function(value) {{
                            return '$' + (value / 1000000).toFixed(0) + 'M';
                        }}
                    }}
                }}
            }}
        }}
    }});
}}

function createCommunityCards(communities) {{
    const container = document.getElementById('communityCards');
    if (!container) return;

    container.innerHTML = '';

    communities.slice(0, 12).forEach(community => {{
        const card = document.createElement('div');
        card.className = 'community-card' + (community.isHighlight ? ' highlight' : '');

        card.innerHTML = `
            <h3>${{community.name}}</h3>
            <div class="stat-row">
                <div class="stat">
                    <div class="stat-label">Total Funding</div>
                    <div class="stat-value">$${{(community.totalFunding / 1000000).toFixed(1)}}M</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Per Capita</div>
                    <div class="stat-value">$${{community.perCapita.toLocaleString()}}</div>
                </div>
            </div>
            <div class="stat-row">
                <div class="stat">
                    <div class="stat-label">Programs</div>
                    <div class="stat-value">${{community.programs}}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Population</div>
                    <div class="stat-value">${{community.population.toLocaleString()}}</div>
                </div>
            </div>
        `;

        container.appendChild(card);
    }});
}}
"""

    return js_content

def main():
    """Main update function"""
    print("=" * 80)
    print("🔄 UPDATING DASHBOARD WITH LIVE DATA")
    print("=" * 80)
    print()

    # Connect
    print("Connecting to Supabase...")
    supabase = connect_to_supabase()
    print("✅ Connected")
    print()

    # Fetch programs
    print("Fetching all programs...")
    programs = get_all_programs(supabase)
    print(f"✅ Fetched {len(programs)} programs")
    print()

    # Analyze
    print("Analyzing communities...")
    community_data = analyze_communities(programs)
    print(f"✅ Analyzed {len(community_data)} communities")
    print()

    # Generate JS
    print("Generating dashboard JavaScript...")
    js_content = generate_dashboard_js(community_data)

    # Save
    output_file = 'dashboard/funding-dashboard.js'
    with open(output_file, 'w') as f:
        f.write(js_content)

    print(f"✅ Updated {output_file}")
    print()

    # Print summary
    total_funding = sum(c['totalFunding'] for c in community_data.values())
    total_programs = sum(c['programs'] for c in community_data.values())

    print("=" * 80)
    print("📊 DASHBOARD UPDATE SUMMARY")
    print("=" * 80)
    print()
    print(f"Total Funding: ${total_funding:,.0f}")
    print(f"Total Programs: {total_programs}")
    print(f"Communities: {len(community_data)}")
    print()

    print("Top 5 Communities by Total Funding:")
    sorted_communities = sorted(community_data.values(), key=lambda x: x['totalFunding'], reverse=True)
    for i, c in enumerate(sorted_communities[:5], 1):
        print(f"  {i}. {c['name']}: ${c['totalFunding']:,.0f} ({c['programs']} programs)")
    print()

    print("Top 5 Communities by Per Capita:")
    sorted_per_capita = sorted([c for c in community_data.values() if c['perCapita'] > 0], key=lambda x: x['perCapita'], reverse=True)
    for i, c in enumerate(sorted_per_capita[:5], 1):
        print(f"  {i}. {c['name']}: ${c['perCapita']:,.2f}/person")
    print()

    print("=" * 80)
    print("🎉 DASHBOARD UPDATE COMPLETE!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Open dashboard/funding.html in your browser")
    print("  2. Verify data is displaying correctly")
    print("  3. Share with stakeholders!")
    print()

if __name__ == '__main__':
    from datetime import datetime
    main()
