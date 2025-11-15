// Queensland Communities Funding Data
const communitiesData = [
    {
        name: 'Mount Isa',
        totalFunding: 53380030,
        programs: 7,
        population: 18500,
        perCapita: 2885,
        isHighlight: true,
        programs_detail: [
            { name: 'On-Country Programs', amount: 26450000, type: 'On-Country' },
            { name: 'Co-Responder Team', amount: 20000000, type: 'Co-Responder' },
            { name: 'Stronger Communities', amount: 7000000, type: 'Community Programs' },
            { name: 'Community Grants', amount: 430000, type: 'Grants' }
        ]
    },
    {
        name: 'Gold Coast',
        totalFunding: 30800000,
        programs: 3,
        population: 679100,
        perCapita: 45,
        programs_detail: [
            { name: 'Crime Prevention School - Men of Business', amount: 10000000, type: 'Crime Prevention' },
            { name: 'Staying on Track - Life Without Barriers', amount: 20000000, type: 'Staying on Track' },
            { name: 'Kickstarter Early Intervention', amount: 800000, type: 'Kickstarter' }
        ]
    },
    {
        name: 'Townsville',
        totalFunding: 28000000,
        programs: 3,
        population: 180820,
        perCapita: 155,
        programs_detail: [
            { name: 'Crime Prevention School - Lighthouse', amount: 12500000, type: 'Crime Prevention' },
            { name: 'Staying on Track', amount: 15000000, type: 'Staying on Track' },
            { name: 'Kickstarter', amount: 500000, type: 'Kickstarter' }
        ]
    },
    {
        name: 'Cairns',
        totalFunding: 26200000,
        programs: 3,
        population: 153075,
        perCapita: 171,
        programs_detail: [
            { name: 'Youth Justice School - Ohana for Youth', amount: 20000000, type: 'Youth Justice School' },
            { name: 'Kickstarter - 6 Programs', amount: 1200000, type: 'Kickstarter' },
            { name: 'FNQ On-Country', amount: 5000000, type: 'On-Country' }
        ]
    },
    {
        name: 'Logan',
        totalFunding: 20900000,
        programs: 2,
        population: 326615,
        perCapita: 64,
        programs_detail: [
            { name: 'Youth Justice School', amount: 20000000, type: 'Youth Justice School' },
            { name: 'Kickstarter', amount: 900000, type: 'Kickstarter' }
        ]
    },
    {
        name: 'Ipswich',
        totalFunding: 18900000,
        programs: 3,
        population: 220000,
        perCapita: 86,
        programs_detail: [
            { name: 'Crime Prevention School', amount: 12500000, type: 'Crime Prevention' },
            { name: 'Regional Reset - Kokoda', amount: 5500000, type: 'Regional Reset' },
            { name: 'Kickstarter', amount: 900000, type: 'Kickstarter' }
        ]
    },
    {
        name: 'Rockhampton',
        totalFunding: 18000000,
        programs: 2,
        population: 79967,
        perCapita: 225,
        programs_detail: [
            { name: 'Crime Prevention School', amount: 12500000, type: 'Crime Prevention' },
            { name: 'Regional Reset', amount: 5500000, type: 'Regional Reset' }
        ]
    },
    {
        name: 'Torres Strait',
        totalFunding: 3777000,
        programs: 2,
        population: 4514,
        perCapita: 837,
        programs_detail: [
            { name: 'Youth Programs', amount: 3000000, type: 'Youth Programs' },
            { name: 'Existing Programs', amount: 777000, type: 'Community Programs' }
        ]
    },
    {
        name: 'Palm Island',
        totalFunding: 2735005,
        programs: 2,
        population: 2455,
        perCapita: 1114,
        programs_detail: [
            { name: 'Tourism Development', amount: 2000000, type: 'Economic Development' },
            { name: 'Existing Programs', amount: 735005, type: 'Community Programs' }
        ]
    }
];

// Sort by total funding (descending)
const rankedCommunities = [...communitiesData].sort((a, b) => b.totalFunding - a.totalFunding);

// Sort by per capita (descending)
const perCapitaRanked = [...communitiesData].sort((a, b) => b.perCapita - a.perCapita);

// Color schemes
const communityColors = {
    'Mount Isa': '#667eea',
    'Gold Coast': '#48bb78',
    'Townsville': '#f6ad55',
    'Cairns': '#fc8181',
    'Logan': '#9f7aea',
    'Ipswich': '#4299e1',
    'Rockhampton': '#ed8936',
    'Torres Strait': '#38b2ac',
    'Palm Island': '#d53f8c'
};

const programTypeColors = {
    'Crime Prevention': '#667eea',
    'Youth Justice School': '#48bb78',
    'Staying on Track': '#f6ad55',
    'On-Country': '#fc8181',
    'Regional Reset': '#9f7aea',
    'Kickstarter': '#4299e1',
    'Co-Responder': '#ed8936',
    'Community Programs': '#38b2ac',
    'Grants': '#d53f8c',
    'Economic Development': '#805ad5',
    'Youth Programs': '#319795'
};

// Utility functions
function formatCurrency(amount) {
    if (amount >= 1000000) {
        return '$' + (amount / 1000000).toFixed(1) + 'M';
    } else if (amount >= 1000) {
        return '$' + (amount / 1000).toFixed(0) + 'K';
    }
    return '$' + amount.toLocaleString();
}

function formatNumber(num) {
    return num.toLocaleString();
}

// Populate ranking table
function populateRankingTable() {
    const tbody = document.getElementById('ranking-tbody');
    tbody.innerHTML = '';

    rankedCommunities.forEach((community, index) => {
        const rank = index + 1;
        const row = document.createElement('tr');
        row.className = community.isHighlight ? 'mount-isa' : '';

        row.innerHTML = `
            <td class="rank ${rank === 1 ? 'rank-1' : ''}">${rank}</td>
            <td class="community-name">
                ${community.name}
                ${rank === 1 ? '<span class="badge badge-gold">🏆 #1</span>' : ''}
                ${community.isHighlight && rank !== 1 ? '<span class="badge badge-highlight">Highlighted</span>' : ''}
            </td>
            <td class="amount">${formatCurrency(community.totalFunding)}</td>
            <td class="programs">${community.programs} programs</td>
            <td class="per-capita">${formatCurrency(community.perCapita)}/person</td>
            <td>${formatNumber(community.population)}</td>
        `;

        tbody.appendChild(row);
    });
}

// Chart 1: Total Funding Bar Chart
function createFundingBarChart() {
    const ctx = document.getElementById('fundingBarChart').getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: rankedCommunities.map(c => c.name),
            datasets: [{
                label: 'Total Funding',
                data: rankedCommunities.map(c => c.totalFunding),
                backgroundColor: rankedCommunities.map(c =>
                    c.isHighlight ? communityColors[c.name] : communityColors[c.name] + '99'
                ),
                borderColor: rankedCommunities.map(c => communityColors[c.name]),
                borderWidth: 2,
                borderRadius: 8,
                hoverBackgroundColor: rankedCommunities.map(c => communityColors[c.name])
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            const community = rankedCommunities[context.dataIndex];
                            return [
                                'Total: ' + formatCurrency(context.parsed.y),
                                'Programs: ' + community.programs,
                                'Per Capita: ' + formatCurrency(community.perCapita)
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        },
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 12,
                            weight: function(context) {
                                return rankedCommunities[context.index].isHighlight ? 'bold' : 'normal';
                            }
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Chart 2: Funding Share Pie Chart
function createFundingPieChart() {
    const ctx = document.getElementById('fundingPieChart').getContext('2d');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: rankedCommunities.map(c => c.name),
            datasets: [{
                data: rankedCommunities.map(c => c.totalFunding),
                backgroundColor: rankedCommunities.map(c => communityColors[c.name]),
                borderWidth: 3,
                borderColor: '#fff',
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: 13,
                            weight: function(context) {
                                return rankedCommunities[context.index].isHighlight ? 'bold' : 'normal';
                            }
                        },
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return [
                                context.label + ': ' + formatCurrency(context.parsed),
                                percentage + '% of total'
                            ];
                        }
                    }
                }
            }
        }
    });
}

// Chart 3: Per Capita Comparison
function createPerCapitaChart() {
    const ctx = document.getElementById('perCapitaChart').getContext('2d');

    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: communitiesData.map(c => ({
                label: c.name,
                data: [{
                    x: c.population,
                    y: c.perCapita,
                    r: Math.sqrt(c.totalFunding) / 1500
                }],
                backgroundColor: communityColors[c.name] + (c.isHighlight ? 'CC' : '80'),
                borderColor: communityColors[c.name],
                borderWidth: c.isHighlight ? 3 : 2
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 12
                        },
                        padding: 12,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const community = communitiesData.find(c => c.name === context.dataset.label);
                            return [
                                community.name,
                                'Per Capita: ' + formatCurrency(community.perCapita),
                                'Population: ' + formatNumber(community.population),
                                'Total: ' + formatCurrency(community.totalFunding)
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'logarithmic',
                    title: {
                        display: true,
                        text: 'Population (log scale)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Per Capita Funding ($)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + formatNumber(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

// Chart 4: Mount Isa Breakdown
function createMountIsaBreakdownChart() {
    const ctx = document.getElementById('mountIsaBreakdownChart').getContext('2d');
    const mountIsa = communitiesData.find(c => c.name === 'Mount Isa');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: mountIsa.programs_detail.map(p => p.name),
            datasets: [{
                data: mountIsa.programs_detail.map(p => p.amount),
                backgroundColor: mountIsa.programs_detail.map(p => programTypeColors[p.type] || '#718096'),
                borderWidth: 3,
                borderColor: '#fff',
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 12
                        },
                        padding: 12,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return [
                                context.label,
                                formatCurrency(context.parsed) + ' (' + percentage + '%)'
                            ];
                        }
                    }
                }
            }
        }
    });
}

// Chart 5: Program Types Stacked Bar
function createProgramTypesChart() {
    const ctx = document.getElementById('programTypesChart').getContext('2d');

    // Get all unique program types
    const programTypes = [...new Set(
        communitiesData.flatMap(c => c.programs_detail.map(p => p.type))
    )];

    // Create datasets for each program type
    const datasets = programTypes.map(type => {
        return {
            label: type,
            data: communitiesData.map(c => {
                const programs = c.programs_detail.filter(p => p.type === type);
                return programs.reduce((sum, p) => sum + p.amount, 0);
            }),
            backgroundColor: programTypeColors[type] || '#718096',
            borderRadius: 5
        };
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: communitiesData.map(c => c.name),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 12
                        },
                        padding: 12,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        footer: function(tooltipItems) {
                            const total = tooltipItems.reduce((sum, item) => sum + item.parsed.y, 0);
                            return 'Total: ' + formatCurrency(total);
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    ticks: {
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    stacked: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        },
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

// Chart 6: Economic Impact
function createEconomicImpactChart() {
    const ctx = document.getElementById('economicImpactChart').getContext('2d');

    const years = ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'];
    const directInvestment = 10700000; // per year
    const multiplierEffect = directInvestment * 2.5;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Direct Investment',
                    data: years.map(() => directInvestment),
                    backgroundColor: '#667eea99',
                    borderColor: '#667eea',
                    borderWidth: 2,
                    borderRadius: 8
                },
                {
                    label: 'Multiplier Effect (LM3 x2.5)',
                    data: years.map(() => multiplierEffect - directInvestment),
                    backgroundColor: '#48bb7899',
                    borderColor: '#48bb78',
                    borderWidth: 2,
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 13
                        },
                        padding: 15
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        footer: function(tooltipItems) {
                            const total = tooltipItems.reduce((sum, item) => sum + item.parsed.y, 0);
                            return 'Total Annual Impact: ' + formatCurrency(total);
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    }
                },
                y: {
                    stacked: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Populate ranking table
    populateRankingTable();

    // Create all charts
    createFundingBarChart();
    createFundingPieChart();
    createPerCapitaChart();
    createMountIsaBreakdownChart();
    createProgramTypesChart();
    createEconomicImpactChart();

    console.log('📊 Queensland Youth Justice Funding Dashboard loaded');
    console.log('💰 Total funding tracked: ' + formatCurrency(communitiesData.reduce((sum, c) => sum + c.totalFunding, 0)));
    console.log('🏆 Mount Isa: ' + formatCurrency(communitiesData.find(c => c.name === 'Mount Isa').totalFunding));
});
