"""
Continuous Data Updater for Mount Isa Economic Observatory
Runs on schedule to keep all data sources fresh
"""
import schedule
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json
import os

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / 'scripts'
LOG_FILE = BASE_DIR / 'data' / 'update_log.json'

def log_update(source, status, message, records=0):
    """Log update activity"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'source': source,
        'status': status,
        'message': message,
        'records': records
    }

    # Load existing log
    logs = []
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)

    # Add new entry
    logs.append(log_entry)

    # Keep only last 100 entries
    logs = logs[-100:]

    # Save log
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

    # Print to console
    status_icon = "✅" if status == "success" else "⚠️" if status == "warning" else "❌"
    print(f"{status_icon} [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {source}: {message}")

def update_export_databases():
    """Export latest data from databases"""
    print("\n" + "="*80)
    print(f"🔄 UPDATING DATABASE EXPORTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / 'export_all_databases.py')],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            log_update('database_exports', 'success', 'Successfully exported all databases')
        else:
            log_update('database_exports', 'error', f'Export failed: {result.stderr[:200]}')

    except subprocess.TimeoutExpired:
        log_update('database_exports', 'error', 'Export timed out after 5 minutes')
    except Exception as e:
        log_update('database_exports', 'error', f'Export error: {str(e)}')

def update_acnc_charities():
    """Update ACNC charity data"""
    print("\n" + "="*80)
    print(f"🔄 UPDATING ACNC CHARITIES - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / 'scrape_acnc_charities.py')],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            # Parse output to get number of records
            output = result.stdout
            if 'charities operating in Mount Isa' in output:
                # Extract number from output
                import re
                match = re.search(r'Found (\d+) charities', output)
                if match:
                    count = int(match.group(1))
                    log_update('acnc_charities', 'success', f'Updated ACNC data', records=count)
                else:
                    log_update('acnc_charities', 'success', 'Updated ACNC data')
            else:
                log_update('acnc_charities', 'warning', 'ACNC scrape completed with warnings')
        else:
            log_update('acnc_charities', 'error', f'ACNC scrape failed: {result.stderr[:200]}')

    except subprocess.TimeoutExpired:
        log_update('acnc_charities', 'error', 'ACNC scrape timed out after 5 minutes')
    except Exception as e:
        log_update('acnc_charities', 'error', f'ACNC scrape error: {str(e)}')

def update_grantconnect():
    """Update GrantConnect data"""
    print("\n" + "="*80)
    print(f"🔄 UPDATING GRANTCONNECT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / 'scrape_grantconnect.py')],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            log_update('grantconnect', 'success', 'Updated GrantConnect data')
        else:
            log_update('grantconnect', 'error', f'GrantConnect scrape failed: {result.stderr[:200]}')

    except subprocess.TimeoutExpired:
        log_update('grantconnect', 'error', 'GrantConnect scrape timed out')
    except Exception as e:
        log_update('grantconnect', 'error', f'GrantConnect error: {str(e)}')

def full_update():
    """Run all updates"""
    print("\n" + "="*80)
    print(f"🚀 STARTING FULL DATA UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    update_export_databases()
    update_acnc_charities()
    update_grantconnect()

    print("\n" + "="*80)
    print(f"✅ FULL UPDATE COMPLETE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

def setup_schedule():
    """Set up update schedule"""
    # Export databases every 6 hours
    schedule.every(6).hours.do(update_export_databases)

    # Update ACNC daily at 2 AM
    schedule.every().day.at("02:00").do(update_acnc_charities)

    # Update GrantConnect daily at 3 AM
    schedule.every().day.at("03:00").do(update_grantconnect)

    # Full update weekly on Sunday at 1 AM
    schedule.every().sunday.at("01:00").do(full_update)

    print("\n" + "="*80)
    print("⏰ UPDATE SCHEDULE CONFIGURED")
    print("="*80)
    print("\nScheduled updates:")
    print("  • Database exports: Every 6 hours")
    print("  • ACNC charities: Daily at 2:00 AM")
    print("  • GrantConnect: Daily at 3:00 AM")
    print("  • Full update: Weekly on Sunday at 1:00 AM")
    print("\n" + "="*80 + "\n")

def run_continuous():
    """Run continuous update loop"""
    setup_schedule()

    print("🔄 Starting continuous update service...")
    print("Press Ctrl+C to stop\n")

    # Run initial update
    print("Running initial update...\n")
    full_update()

    # Run scheduled updates
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Mount Isa Economic Observatory Data Updater')
    parser.add_argument('--once', action='store_true', help='Run update once and exit')
    parser.add_argument('--databases', action='store_true', help='Update databases only')
    parser.add_argument('--acnc', action='store_true', help='Update ACNC only')
    parser.add_argument('--grants', action='store_true', help='Update GrantConnect only')

    args = parser.parse_args()

    try:
        if args.databases:
            update_export_databases()
        elif args.acnc:
            update_acnc_charities()
        elif args.grants:
            update_grantconnect()
        elif args.once:
            full_update()
        else:
            run_continuous()

    except KeyboardInterrupt:
        print("\n\n⏹️  Update service stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
