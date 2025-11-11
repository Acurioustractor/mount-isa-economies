"""
API Server for Mount Isa Economic Observatory Dashboard
Serves data from CSV exports and provides API endpoints for filtering
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
from pathlib import Path
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'exports'

# Cache for loaded data
services_cache = None
organizations_cache = None

def load_services():
    """Load all services from CSV exports"""
    global services_cache

    if services_cache is not None:
        return services_cache

    all_services = []

    # Load Mount Isa services
    mi_services_file = DATA_DIR / 'services_export.csv'
    if mi_services_file.exists():
        df = pd.read_csv(mi_services_file)
        for idx, row in df.iterrows():
            all_services.append({
                'id': f'mi_{idx}',
                'name': row.get('name'),
                'category': row.get('category_id', 'General'),
                'description': row.get('description'),
                'location': row.get('suburb'),
                'suburb': row.get('suburb'),
                'state': row.get('state'),
                'postcode': row.get('postcode'),
                'phone': row.get('phone'),
                'email': row.get('email'),
                'website': row.get('website'),
                'source': 'mount_isa_service_map',
                'latitude': row.get('latitude'),
                'longitude': row.get('longitude')
            })

    # Load youth justice services
    yj_services_file = DATA_DIR / 'youth_justice_services_export.csv'
    if yj_services_file.exists():
        df = pd.read_csv(yj_services_file)
        for idx, row in df.iterrows():
            all_services.append({
                'id': f'yj_{idx}',
                'name': row.get('name'),
                'category': row.get('taxonomy_term', 'Youth Services'),
                'description': row.get('description'),
                'location': row.get('suburb'),
                'suburb': row.get('suburb'),
                'state': row.get('state'),
                'postcode': row.get('postal_code'),
                'phone': row.get('phone'),
                'email': row.get('email'),
                'website': row.get('website'),
                'source': 'youth_justice_services',
                'latitude': row.get('latitude'),
                'longitude': row.get('longitude')
            })

    services_cache = all_services
    return all_services

def load_organizations():
    """Load organizations from CSV exports"""
    global organizations_cache

    if organizations_cache is not None:
        return organizations_cache

    all_orgs = []

    # Load youth justice organizations
    yj_orgs_file = DATA_DIR / 'youth_justice_organizations_export.csv'
    if yj_orgs_file.exists():
        df = pd.read_csv(yj_orgs_file)
        for idx, row in df.iterrows():
            all_orgs.append({
                'id': f'org_{idx}',
                'name': row.get('name'),
                'description': row.get('description'),
                'source': 'youth_justice_services'
            })

    organizations_cache = all_orgs
    return all_orgs

@app.route('/')
def index():
    """Serve the dashboard HTML"""
    return send_from_directory('.', 'index.html')

@app.route('/dashboard.js')
def dashboard_js():
    """Serve the dashboard JavaScript"""
    return send_from_directory('.', 'dashboard.js')

@app.route('/api/services')
def get_services():
    """Get all services with optional filtering"""
    services = load_services()

    # Get filter parameters
    search = request.args.get('search', '').lower()
    category = request.args.get('category')
    location = request.args.get('location')
    source = request.args.get('source')

    # Filter services
    filtered = services

    if search:
        filtered = [s for s in filtered if
                   search in (s.get('name') or '').lower() or
                   search in (s.get('description') or '').lower()]

    if category:
        filtered = [s for s in filtered if s.get('category') == category]

    if location == 'mount-isa':
        filtered = [s for s in filtered if
                   'mount isa' in (s.get('suburb') or '').lower()]

    if source:
        filtered = [s for s in filtered if s.get('source') == source]

    # Calculate statistics
    stats = {
        'total_services': len(services),
        'total_organizations': len(load_organizations()),
        'mount_isa_services': len([s for s in services if
                                   'mount isa' in (s.get('suburb') or '').lower()]),
        'total_funding': 0  # TODO: Calculate from grants data
    }

    return jsonify({
        'services': filtered,
        'stats': stats,
        'total': len(filtered)
    })

@app.route('/api/organizations')
def get_organizations():
    """Get all organizations"""
    organizations = load_organizations()
    return jsonify({
        'organizations': organizations,
        'total': len(organizations)
    })

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    services = load_services()
    organizations = load_organizations()

    mount_isa_services = [s for s in services if
                         'mount isa' in (s.get('suburb') or '').lower()]

    # Get unique categories
    categories = list(set(s.get('category') for s in services if s.get('category')))

    # Get unique sources
    sources = list(set(s.get('source') for s in services if s.get('source')))

    return jsonify({
        'total_services': len(services),
        'total_organizations': len(organizations),
        'mount_isa_services': len(mount_isa_services),
        'total_funding': 0,  # TODO: Calculate from grants
        'categories': categories,
        'sources': sources
    })

@app.route('/api/data-sources')
def get_data_sources():
    """Get list of data sources and their status"""
    sources = []

    # Mount Isa service map
    mi_file = DATA_DIR / 'services_export.csv'
    if mi_file.exists():
        df = pd.read_csv(mi_file)
        sources.append({
            'name': 'Mount Isa Service Map',
            'description': 'Manually mapped services with detailed information',
            'status': 'active',
            'last_update': mi_file.stat().st_mtime,
            'records': len(df)
        })

    # Youth justice services
    yj_file = DATA_DIR / 'youth_justice_services_export.csv'
    if yj_file.exists():
        df = pd.read_csv(yj_file)
        sources.append({
            'name': 'Youth Justice Services',
            'description': 'Youth justice and related services',
            'status': 'active',
            'last_update': yj_file.stat().st_mtime,
            'records': len(df)
        })

    return jsonify({
        'sources': sources,
        'total': len(sources)
    })

@app.route('/api/update', methods=['POST'])
def trigger_update():
    """Trigger a data source update"""
    # TODO: Implement actual update logic
    return jsonify({
        'success': True,
        'message': 'Update triggered successfully'
    })

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 MOUNT ISA ECONOMIC OBSERVATORY API SERVER")
    print("="*80)
    print(f"\nData directory: {DATA_DIR}")
    print("\nStarting server...")
    print("Dashboard available at: http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  • GET  /api/services - Get all services (with filtering)")
    print("  • GET  /api/organizations - Get all organizations")
    print("  • GET  /api/stats - Get statistics")
    print("  • GET  /api/data-sources - Get data source info")
    print("  • POST /api/update - Trigger data update")
    print("\n" + "="*80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
