# Mount Isa Economic Observatory Dashboard

Interactive front-end for browsing, filtering, and managing your 1,121+ services and economic data.

## 🎯 Features

- **Service Browser**: Filter and search through all services
- **Interactive Map**: Geographic visualization with heat maps
- **Data Source Management**: Add and update data sources
- **Continuous Updates**: Automated data refreshing
- **Real-time Statistics**: Track services, organizations, and funding

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip3 install flask flask-cors pandas schedule
```

### 2. Start the Dashboard

```bash
cd mount-isa-observatory/dashboard
python3 api_server.py
```

### 3. Open in Browser

Visit: **http://localhost:5000**

## 📊 Using the Dashboard

### Service Browser Tab

**Filter Services:**
- Search by name or description
- Filter by category (Youth, Health, Justice, etc.)
- Filter by location (Mount Isa only or all)
- Filter by data source

**View Details:**
- Click any service card to see full details
- See contact information, website, description

### Interactive Map Tab

- See all services plotted on Mount Isa map
- Filtered services automatically update on map
- Click markers for service details
- Future: Heat maps for money flows

### Data Sources Tab

**Connected Sources:**
- Mount Isa Service Map (46 services)
- Youth Justice Services (1,075 services)
- ACNC Charities (pending setup)
- GrantConnect (pending setup)

**Add New Source:**
- Click "Add New Data Source"
- Provide name and URL/path
- System will validate and configure scraper

### Data Updates Tab

**Manual Updates:**
- Click "Run All Updates Now" to refresh all data
- See update log with timestamps
- Track success/failure of each source

**Automated Updates:**
- Database exports: Every 6 hours
- Government sources: Daily at 2-3 AM
- Full refresh: Weekly on Sunday

## 🔄 Continuous Data Updates

### Run Update Service

```bash
# Start continuous update service
python3 continuous_updater.py

# Or run once and exit
python3 continuous_updater.py --once

# Or update specific sources
python3 continuous_updater.py --databases
python3 continuous_updater.py --acnc
python3 continuous_updater.py --grants
```

### Update Schedule

| Data Source | Frequency | Time |
|------------|-----------|------|
| Database exports | Every 6 hours | Continuous |
| ACNC charities | Daily | 2:00 AM |
| GrantConnect | Daily | 3:00 AM |
| Full update | Weekly | Sunday 1:00 AM |

## 📝 Adding New Data Sources

### Step 1: Create Scraper Script

Create `scripts/scrape_your_source.py`:

```python
"""
Scrape [Your Data Source Name]
Description of what this source provides
"""
import requests
import pandas as pd
from pathlib import Path

output_dir = Path(__file__).parent.parent / 'data' / 'raw'
output_dir.mkdir(parents=True, exist_ok=True)

# Your scraping logic here
# ...

# Save to CSV
output_file = output_dir / 'your_source_data.csv'
df.to_csv(output_file, index=False)

print(f"✅ Scraped {len(df)} records from [Your Source]")
```

### Step 2: Add to Update Schedule

Edit `dashboard/continuous_updater.py`:

```python
def update_your_source():
    """Update your new data source"""
    print(f"\n🔄 UPDATING YOUR SOURCE - {datetime.now()}")

    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / 'scrape_your_source.py')],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            log_update('your_source', 'success', 'Updated successfully')
        else:
            log_update('your_source', 'error', 'Update failed')
    except Exception as e:
        log_update('your_source', 'error', str(e))

# Add to schedule
def setup_schedule():
    # ... existing schedules ...
    schedule.every().day.at("04:00").do(update_your_source)
```

### Step 3: Add to API Server

Edit `dashboard/api_server.py`:

```python
def load_services():
    # ... existing code ...

    # Load your new source
    your_file = DATA_DIR / 'your_source_data.csv'
    if your_file.exists():
        df = pd.read_csv(your_file)
        for idx, row in df.iterrows():
            all_services.append({
                'id': f'your_{idx}',
                'name': row.get('name'),
                'category': row.get('category'),
                # ... map your columns ...
                'source': 'your_source_name'
            })
```

### Step 4: Test

```bash
# Test your scraper
python3 scripts/scrape_your_source.py

# Test continuous updater
python3 dashboard/continuous_updater.py --once

# Restart API server
python3 dashboard/api_server.py
```

## 🎨 Customizing the Dashboard

### Change Colors

Edit `dashboard/index.html` CSS:

```css
.header {
    background: linear-gradient(135deg, #YOUR_COLOR1, #YOUR_COLOR2);
}

.stat-card .number {
    color: #YOUR_ACCENT_COLOR;
}
```

### Add New Filters

Edit `dashboard/dashboard.js`:

```javascript
// Add filter to HTML
<select id="your-filter" onchange="filterServices()">
    <option value="">All Your Options</option>
</select>

// Add filter logic
function filterServices() {
    const yourFilter = document.getElementById('your-filter').value;

    filteredServices = allServices.filter(service => {
        // Your filter logic
        if (yourFilter && service.yourField !== yourFilter) {
            return false;
        }
        return true;
    });

    displayServices();
}
```

## 🔐 Production Deployment

### Using a Production Server (Gunicorn)

```bash
pip3 install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### Using systemd for Continuous Updates

Create `/etc/systemd/system/mount-isa-updater.service`:

```ini
[Unit]
Description=Mount Isa Economic Observatory Data Updater
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/mount-isa-observatory/dashboard
ExecStart=/usr/bin/python3 continuous_updater.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable mount-isa-updater
sudo systemctl start mount-isa-updater
sudo systemctl status mount-isa-updater
```

### Environment Variables

Create `.env` file:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mount_isa_platform
DB_USER=your_user
DB_PASSWORD=your_password
FLASK_SECRET_KEY=your_secret_key
```

## 📖 API Documentation

### GET /api/services

Get all services with optional filtering.

**Query Parameters:**
- `search` - Search term for name/description
- `category` - Filter by category
- `location` - Filter by location (use "mount-isa" for Mount Isa only)
- `source` - Filter by data source

**Response:**
```json
{
  "services": [...],
  "stats": {
    "total_services": 1121,
    "total_organizations": 1044,
    "mount_isa_services": 46,
    "total_funding": 0
  },
  "total": 46
}
```

### GET /api/organizations

Get all organizations.

### GET /api/stats

Get overall statistics.

### GET /api/data-sources

Get list of configured data sources and their status.

### POST /api/update

Trigger a manual data update.

## 🐛 Troubleshooting

### Dashboard won't load

```bash
# Check if API server is running
ps aux | grep api_server

# Check for errors
python3 api_server.py
```

### No data showing

```bash
# Check if data files exist
ls -la ../data/exports/

# Re-export databases
python3 ../scripts/export_all_databases.py
```

### Updates failing

```bash
# Check update log
cat ../data/update_log.json

# Test individual scrapers
python3 ../scripts/scrape_acnc_charities.py
```

## 💡 Next Steps

1. **Add Money Flow Visualization**: Integrate economic flow data into map
2. **Advanced Filters**: Add Indigenous-led, cultural safety, funding amount filters
3. **Export Data**: Add CSV/JSON export buttons
4. **Service Gap Analysis**: Visualize identified gaps
5. **Community Feedback**: Add feedback submission form
6. **Grant Tracking**: Show funding flows to organizations

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `data/update_log.json`
3. Test individual components separately
