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

    print(f"\n📂 Loading services from: {DATA_DIR}")
    print(f"   Directory exists: {DATA_DIR.exists()}")

    if DATA_DIR.exists():
        print(f"   Files in directory:")
        for f in DATA_DIR.glob('*.csv'):
            print(f"     • {f.name}")
    print()

    # Load Mount Isa services
    mi_services_file = DATA_DIR / 'services_export.csv'
    print(f"🔍 Looking for Mount Isa services: {mi_services_file}")
    print(f"   Exists: {mi_services_file.exists()}")

    if mi_services_file.exists():
        try:
            df = pd.read_csv(mi_services_file)
            print(f"   ✅ Loaded {len(df)} Mount Isa services")
            print(f"   Columns: {list(df.columns)}")

            for idx, row in df.iterrows():
                all_services.append({
                    'id': f'mi_{idx}',
                    'name': str(row.get('name', 'Unknown')),
                    'category': str(row.get('category_id', 'General')),
                    'description': str(row.get('description', '')) if pd.notna(row.get('description')) else '',
                    'location': str(row.get('suburb', '')) if pd.notna(row.get('suburb')) else '',
                    'suburb': str(row.get('suburb', '')) if pd.notna(row.get('suburb')) else '',
                    'state': str(row.get('state', '')) if pd.notna(row.get('state')) else '',
                    'postcode': str(row.get('postcode', '')) if pd.notna(row.get('postcode')) else '',
                    'phone': str(row.get('phone', '')) if pd.notna(row.get('phone')) else '',
                    'email': str(row.get('email', '')) if pd.notna(row.get('email')) else '',
                    'website': str(row.get('website', '')) if pd.notna(row.get('website')) else '',
                    'source': 'mount_isa_service_map',
                    'latitude': float(row.get('latitude')) if pd.notna(row.get('latitude')) else None,
                    'longitude': float(row.get('longitude')) if pd.notna(row.get('longitude')) else None
                })
        except Exception as e:
            print(f"   ❌ Error loading Mount Isa services: {e}")
    else:
        print(f"   ⚠️  File not found")

    # Load youth justice services
    yj_services_file = DATA_DIR / 'youth_justice_services_export.csv'
    print(f"\n🔍 Looking for Youth Justice services: {yj_services_file}")
    print(f"   Exists: {yj_services_file.exists()}")

    if yj_services_file.exists():
        try:
            df = pd.read_csv(yj_services_file)
            print(f"   ✅ Loaded {len(df)} Youth Justice services")
            print(f"   Columns: {list(df.columns)[:10]}...")  # Show first 10 columns

            for idx, row in df.iterrows():
                all_services.append({
                    'id': f'yj_{idx}',
                    'name': str(row.get('name', 'Unknown')),
                    'category': str(row.get('taxonomy_term', 'Youth Services')) if pd.notna(row.get('taxonomy_term')) else 'Youth Services',
                    'description': str(row.get('description', '')) if pd.notna(row.get('description')) else '',
                    'location': str(row.get('suburb', '')) if pd.notna(row.get('suburb')) else '',
                    'suburb': str(row.get('suburb', '')) if pd.notna(row.get('suburb')) else '',
                    'state': str(row.get('state', '')) if pd.notna(row.get('state')) else '',
                    'postcode': str(row.get('postal_code', '')) if pd.notna(row.get('postal_code')) else '',
                    'phone': str(row.get('phone', '')) if pd.notna(row.get('phone')) else '',
                    'email': str(row.get('email', '')) if pd.notna(row.get('email')) else '',
                    'website': str(row.get('website', '')) if pd.notna(row.get('website')) else '',
                    'source': 'youth_justice_services',
                    'latitude': float(row.get('latitude')) if pd.notna(row.get('latitude')) else None,
                    'longitude': float(row.get('longitude')) if pd.notna(row.get('longitude')) else None
                })
        except Exception as e:
            print(f"   ❌ Error loading Youth Justice services: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"   ⚠️  File not found")

    print(f"\n✅ Total services loaded: {len(all_services)}\n")

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
    # Use port from environment or default to 8080
    port = int(os.getenv('PORT', 8080))

    print(f"Dashboard available at: http://localhost:{port}")
    print("\nAPI Endpoints:")
    print("  • GET  /api/services - Get all services (with filtering)")
    print("  • GET  /api/organizations - Get all organizations")
    print("  • GET  /api/stats - Get statistics")
    print("  • GET  /api/data-sources - Get data source info")
    print("  • POST /api/update - Trigger data update")
    print("\n" + "="*80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=port)
