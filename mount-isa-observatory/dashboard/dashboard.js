// Mount Isa Economic Observatory Dashboard
// Loads and displays services with filtering capabilities

let allServices = [];
let filteredServices = [];
let map = null;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadServices();
    initializeMap();
    loadDataSources();
    loadUpdateLog();
});

// Load services from backend API
async function loadServices() {
    try {
        // In production, this would call your API
        // For now, we'll use the exported CSV files
        const response = await fetch('/api/services');

        if (!response.ok) {
            // Fallback: show sample data
            loadSampleServices();
            return;
        }

        const data = await response.json();
        allServices = data.services;

        updateStats(data.stats);
        populateFilters();
        filterServices();

    } catch (error) {
        console.log('API not available, loading sample data');
        loadSampleServices();
    }
}

// Load sample services for demonstration
function loadSampleServices() {
    // This would normally come from your database
    allServices = [
        {
            id: 1,
            name: 'headspace Mount Isa',
            category: 'Youth Mental Health',
            description: 'Free counselling, drug and alcohol support, and physical and sexual health services for ages 12-25',
            location: 'Mount Isa',
            suburb: 'Mount Isa',
            postcode: '4825',
            phone: '(07) 4743 3700',
            website: 'https://headspacemountisa.com.au',
            source: 'mount_isa_service_map',
            latitude: -20.7256,
            longitude: 139.4927
        },
        {
            id: 2,
            name: 'PCYC Mount Isa',
            category: 'Youth Programs',
            description: 'Wide range of programs that give young people purpose, skills, and positive role models',
            location: 'Mount Isa',
            suburb: 'Mount Isa',
            postcode: '4825',
            phone: '(07) 4742 1644',
            website: 'https://pcycqld.org.au/centres/mount-isa/',
            source: 'mount_isa_service_map',
            latitude: -20.7256,
            longitude: 139.4927
        },
        {
            id: 3,
            name: 'Gidgee Healing',
            category: 'Aboriginal Health',
            description: 'Aboriginal Community Controlled Health Service delivering primary health care',
            location: 'Mount Isa',
            suburb: 'Mount Isa',
            postcode: '4825',
            phone: '(07) 4742 2200',
            website: 'https://gidgee.org.au',
            source: 'mount_isa_service_map',
            latitude: -20.7256,
            longitude: 139.4927
        }
    ];

    updateStats({
        total_services: 1121,
        total_organizations: 1044,
        mount_isa_services: 46,
        total_funding: 0
    });

    populateFilters();
    filterServices();
}

// Update statistics cards
function updateStats(stats) {
    document.getElementById('total-services').textContent = stats.total_services.toLocaleString();
    document.getElementById('total-organizations').textContent = stats.total_organizations.toLocaleString();
    document.getElementById('mount-isa-services').textContent = stats.mount_isa_services.toLocaleString();

    const funding = stats.total_funding || 0;
    document.getElementById('total-funding').textContent = funding > 0
        ? `$${(funding / 1000000).toFixed(1)}M`
        : 'Coming soon';
}

// Populate filter dropdowns
function populateFilters() {
    // Get unique categories
    const categories = [...new Set(allServices.map(s => s.category).filter(c => c))];
    const categoryFilter = document.getElementById('category-filter');
    categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        categoryFilter.appendChild(option);
    });

    // Get unique sources
    const sources = [...new Set(allServices.map(s => s.source).filter(s => s))];
    const sourceFilter = document.getElementById('source-filter');
    sources.forEach(src => {
        const option = document.createElement('option');
        option.value = src;
        option.textContent = src.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        sourceFilter.appendChild(option);
    });
}

// Filter services based on current filter values
function filterServices() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const category = document.getElementById('category-filter').value;
    const location = document.getElementById('location-filter').value;
    const source = document.getElementById('source-filter').value;

    filteredServices = allServices.filter(service => {
        // Search filter
        if (searchTerm && !service.name.toLowerCase().includes(searchTerm) &&
            (!service.description || !service.description.toLowerCase().includes(searchTerm))) {
            return false;
        }

        // Category filter
        if (category && service.category !== category) {
            return false;
        }

        // Location filter
        if (location === 'mount-isa' &&
            (!service.suburb || !service.suburb.toLowerCase().includes('mount isa'))) {
            return false;
        }

        // Source filter
        if (source && service.source !== source) {
            return false;
        }

        return true;
    });

    displayServices();
    updateMapMarkers();
}

// Display filtered services in grid
function displayServices() {
    const grid = document.getElementById('services-grid');
    const loading = document.getElementById('services-loading');

    loading.style.display = 'none';
    grid.style.display = 'grid';
    grid.innerHTML = '';

    if (filteredServices.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #718096;">No services found matching your filters.</p>';
        return;
    }

    filteredServices.forEach(service => {
        const card = document.createElement('div');
        card.className = 'service-card';
        card.onclick = () => showServiceDetails(service);

        card.innerHTML = `
            <div class="service-name">${service.name}</div>
            ${service.category ? `<span class="service-category">${service.category}</span>` : ''}
            ${service.description ? `<div class="service-description">${service.description}</div>` : ''}
            <div class="service-meta">
                ${service.suburb ? `<span><i class="fas fa-map-marker-alt"></i>${service.suburb}</span>` : ''}
                ${service.phone ? `<span><i class="fas fa-phone"></i>${service.phone}</span>` : ''}
            </div>
        `;

        grid.appendChild(card);
    });
}

// Show detailed service information
function showServiceDetails(service) {
    alert(`Service Details:\n\nName: ${service.name}\n` +
          `Category: ${service.category || 'N/A'}\n` +
          `Location: ${service.suburb || 'N/A'}\n` +
          `Phone: ${service.phone || 'N/A'}\n` +
          `Website: ${service.website || 'N/A'}\n\n` +
          `Description: ${service.description || 'No description available'}`);
}

// Initialize Leaflet map
function initializeMap() {
    map = L.map('map').setView([-20.7256, 139.4927], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    updateMapMarkers();
}

// Update map markers based on filtered services
function updateMapMarkers() {
    if (!map) return;

    // Clear existing markers
    map.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });

    // Add markers for filtered services with coordinates
    filteredServices.forEach(service => {
        if (service.latitude && service.longitude) {
            const marker = L.marker([service.latitude, service.longitude])
                .addTo(map)
                .bindPopup(`
                    <strong>${service.name}</strong><br>
                    ${service.category || ''}<br>
                    ${service.phone || ''}<br>
                    ${service.website ? `<a href="${service.website}" target="_blank">Website</a>` : ''}
                `);
        }
    });
}

// Load data sources
function loadDataSources() {
    const list = document.getElementById('data-sources-list');

    const dataSources = [
        {
            name: 'Mount Isa Service Map',
            description: '46 manually mapped services with detailed information',
            status: 'active',
            lastUpdate: 'Today',
            records: 46
        },
        {
            name: 'Youth Justice Services',
            description: '1,075 youth justice and related services across Queensland',
            status: 'active',
            lastUpdate: 'Today',
            records: 1075
        },
        {
            name: 'ACNC Charity Register',
            description: 'Australian charities operating in Mount Isa region',
            status: 'pending',
            lastUpdate: 'Never',
            records: 0
        },
        {
            name: 'GrantConnect',
            description: 'Government grants to Mount Isa organizations',
            status: 'pending',
            lastUpdate: 'Never',
            records: 0
        }
    ];

    list.innerHTML = '';
    dataSources.forEach(source => {
        const card = document.createElement('div');
        card.className = 'data-source';
        card.innerHTML = `
            <div class="info">
                <h3>${source.name}</h3>
                <p>${source.description}</p>
                <p style="margin-top: 0.5rem; font-size: 0.85rem; color: #a0aec0;">
                    ${source.records} records • Last updated: ${source.lastUpdate}
                </p>
            </div>
            <div>
                <span class="status ${source.status}">${source.status.toUpperCase()}</span>
            </div>
        `;
        list.appendChild(card);
    });
}

// Load update log
function loadUpdateLog() {
    const log = document.getElementById('update-log');

    const entries = [
        {
            time: new Date().toISOString(),
            message: 'Successfully exported 46 services from mount_isa_services database',
            type: 'success'
        },
        {
            time: new Date().toISOString(),
            message: 'Successfully exported 1,075 services from youth_justice_services database',
            type: 'success'
        },
        {
            time: new Date().toISOString(),
            message: 'ACNC data source: Connection pending - manual setup required',
            type: 'error'
        }
    ];

    log.innerHTML = '';
    entries.forEach(entry => {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${entry.type}`;
        logEntry.innerHTML = `
            <div class="time">${new Date(entry.time).toLocaleString()}</div>
            <div class="message">${entry.message}</div>
        `;
        log.appendChild(logEntry);
    });
}

// Switch between tabs
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');

    // Refresh map if map tab selected
    if (tabName === 'map' && map) {
        setTimeout(() => map.invalidateSize(), 100);
    }
}

// Add new data source
function addDataSource() {
    const name = prompt('Enter data source name:');
    if (!name) return;

    const url = prompt('Enter data source URL or file path:');
    if (!url) return;

    alert(`Data source "${name}" will be added.\n\nIn production, this would:\n` +
          `1. Validate the data source\n` +
          `2. Create a scraper configuration\n` +
          `3. Schedule automatic updates\n` +
          `4. Import initial data`);
}

// Run all data updates
function runAllUpdates() {
    if (!confirm('Run all data source updates now?\n\nThis will fetch latest data from all configured sources.')) {
        return;
    }

    alert('In production, this would:\n' +
          '1. Run all data source scrapers\n' +
          '2. Import new/updated records\n' +
          '3. Update statistics\n' +
          '4. Refresh the dashboard');
}
