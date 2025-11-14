"""
Advanced Temporal Analysis - Detect Patterns, Delays, and Anomalies

Analyzes timing patterns in funding to reveal:
- How long each stage takes (announcement → budget → payment)
- Seasonal patterns (when funding is announced, when payments are made)
- Political cycles (election year effects, budget cycle effects)
- Bottlenecks (which stages take longest)
- Anomalies (unusually fast or slow funding)
- Predictions (when will payment likely occur based on historical patterns)

This reveals WHEN things happen, WHY delays occur, and WHAT patterns drive timing.

Usage:
    python scripts/advanced_temporal_analysis.py
    python scripts/advanced_temporal_analysis.py --detect-anomalies
    python scripts/advanced_temporal_analysis.py --predict-timelines
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import json
from collections import defaultdict

# Load environment
load_dotenv()


class TemporalAnalyzer:
    """Analyze temporal patterns in funding lifecycle"""

    def __init__(self):
        """Initialize analyzer"""
        # Check if Supabase is configured
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")

        from supabase import create_client
        self.supabase = create_client(self.supabase_url, self.supabase_key)

        # Output directory
        self.output_dir = Path(__file__).parent.parent / 'analysis' / 'temporal'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze_funding_lifecycle_duration(self) -> pd.DataFrame:
        """
        Analyze how long each stage of funding lifecycle takes

        Returns:
            DataFrame of stage durations
        """
        print("\n" + "=" * 80)
        print("⏱️  FUNDING LIFECYCLE DURATION ANALYSIS")
        print("=" * 80)

        # Get funding flow data
        result = self.supabase.table('v_funding_flow').select('*').execute()
        df = pd.DataFrame(result.data)

        if df.empty:
            print("\n❌ No funding flow data available")
            return pd.DataFrame()

        # Convert dates
        df['announcement_date'] = pd.to_datetime(df['announcement_date'])

        # Calculate time to payment (for announcements with verified payments)
        df_with_payments = df[df['total_paid'] > 0].copy()

        if df_with_payments.empty:
            print("\n⚠️ No verified payments yet - cannot calculate time to payment")
            print("   Run ACNC verification to add actual payment data")
            return pd.DataFrame()

        # Calculate statistics
        print("\n📊 TIME FROM ANNOUNCEMENT TO PAYMENT:\n")

        # For now we don't have payment dates in the view, so let's query actual_payments
        payments_result = self.supabase.table('actual_payments') \
            .select('announcement_id, payment_date') \
            .execute()

        if not payments_result.data:
            print("⚠️ No payment dates available in actual_payments table")
            return pd.DataFrame()

        payments_df = pd.DataFrame(payments_result.data)
        payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])

        # Get announcement dates
        announcements_result = self.supabase.table('funding_announcements') \
            .select('id, announcement_date') \
            .execute()
        announcements_df = pd.DataFrame(announcements_result.data)
        announcements_df['announcement_date'] = pd.to_datetime(announcements_df['announcement_date'])

        # Merge
        timeline_df = payments_df.merge(
            announcements_df,
            left_on='announcement_id',
            right_on='id',
            how='inner'
        )

        # Calculate duration
        timeline_df['days_to_payment'] = (
            timeline_df['payment_date'] - timeline_df['announcement_date']
        ).dt.days

        if timeline_df.empty:
            print("⚠️ No announcement-payment pairs found")
            return pd.DataFrame()

        # Statistics
        avg_days = timeline_df['days_to_payment'].mean()
        median_days = timeline_df['days_to_payment'].median()
        min_days = timeline_df['days_to_payment'].min()
        max_days = timeline_df['days_to_payment'].max()
        std_days = timeline_df['days_to_payment'].std()

        print(f"Average time to payment: {avg_days:.0f} days ({avg_days/30:.1f} months)")
        print(f"Median time to payment: {median_days:.0f} days ({median_days/30:.1f} months)")
        print(f"Fastest payment: {min_days:.0f} days")
        print(f"Slowest payment: {max_days:.0f} days")
        print(f"Standard deviation: {std_days:.0f} days")

        # Distribution
        print("\n📈 DISTRIBUTION:")
        bins = [0, 30, 90, 180, 365, 730, float('inf')]
        labels = ['0-30 days', '1-3 months', '3-6 months', '6-12 months', '1-2 years', '2+ years']

        distribution = pd.cut(timeline_df['days_to_payment'], bins=bins, labels=labels).value_counts().sort_index()

        for period, count in distribution.items():
            pct = (count / len(timeline_df)) * 100
            print(f"  {period}: {count} ({pct:.0f}%)")

        # Save
        timeline_file = self.output_dir / 'funding_timeline_analysis.csv'
        timeline_df.to_csv(timeline_file, index=False)
        print(f"\n✅ Timeline analysis saved: {timeline_file}")

        return timeline_df

    def detect_seasonal_patterns(self) -> Dict:
        """
        Detect seasonal patterns in funding announcements and payments

        Returns:
            Dictionary of seasonal patterns
        """
        print("\n" + "=" * 80)
        print("📅 SEASONAL PATTERN DETECTION")
        print("=" * 80)

        # Get announcements
        result = self.supabase.table('funding_announcements') \
            .select('announcement_date, amount_announced') \
            .execute()

        df = pd.DataFrame(result.data)
        df['announcement_date'] = pd.to_datetime(df['announcement_date'])
        df['month'] = df['announcement_date'].dt.month
        df['quarter'] = df['announcement_date'].dt.quarter
        df['fiscal_year'] = df['announcement_date'].apply(
            lambda x: f"{x.year}-{x.year+1}" if x.month >= 7 else f"{x.year-1}-{x.year}"
        )

        patterns = {}

        # By month
        print("\n📊 ANNOUNCEMENTS BY MONTH:")
        month_counts = df.groupby('month').agg({
            'announcement_date': 'count',
            'amount_announced': 'sum'
        })
        month_counts.columns = ['Count', 'Total Amount']

        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        for month in range(1, 13):
            if month in month_counts.index:
                count = month_counts.loc[month, 'Count']
                amount = month_counts.loc[month, 'Total Amount'] / 1000000
                print(f"  {month_names[month-1]}: {count} announcements (${amount:.1f}M)")
            else:
                print(f"  {month_names[month-1]}: 0 announcements")

        # By quarter
        print("\n📊 ANNOUNCEMENTS BY QUARTER:")
        quarter_counts = df.groupby('quarter').agg({
            'announcement_date': 'count',
            'amount_announced': 'sum'
        })

        for q in range(1, 5):
            if q in quarter_counts.index:
                count = quarter_counts.loc[q, 'announcement_date']
                amount = quarter_counts.loc[q, 'amount_announced'] / 1000000
                print(f"  Q{q}: {count} announcements (${amount:.1f}M)")

        # Budget cycle (Queensland budget is typically May/June)
        print("\n💰 BUDGET CYCLE PATTERN:")
        budget_months = [5, 6, 7]  # May-July (budget and immediate post-budget)
        budget_period = df[df['month'].isin(budget_months)]
        non_budget_period = df[~df['month'].isin(budget_months)]

        budget_pct = len(budget_period) / len(df) * 100
        print(f"  Budget period (May-Jul): {len(budget_period)} announcements ({budget_pct:.0f}%)")
        print(f"  Rest of year: {len(non_budget_period)} announcements ({100-budget_pct:.0f}%)")

        if budget_pct > 40:
            print("\n  ⚠️ PATTERN: Significant clustering around budget period")
            print("     This suggests announcements are tied to budget cycle")
            patterns['budget_cycle_effect'] = 'strong'
        elif budget_pct > 30:
            patterns['budget_cycle_effect'] = 'moderate'
        else:
            patterns['budget_cycle_effect'] = 'weak'

        # Election cycle (Queensland elections typically every 4 years)
        # Would need election dates to analyze properly
        print("\n🗳️  ELECTION CYCLE:")
        print("  (Requires election date data to analyze)")
        print("  TODO: Add election dates to detect pre-election funding spikes")

        patterns['peak_announcement_month'] = df.groupby('month').size().idxmax()
        patterns['peak_announcement_quarter'] = df.groupby('quarter').size().idxmax()

        # Save patterns
        patterns_file = self.output_dir / 'seasonal_patterns.json'
        with open(patterns_file, 'w') as f:
            json.dump(patterns, f, indent=2)

        print(f"\n✅ Seasonal patterns saved: {patterns_file}")

        return patterns

    def detect_anomalies(self) -> pd.DataFrame:
        """
        Detect anomalies - unusually fast or slow funding

        Returns:
            DataFrame of anomalies
        """
        print("\n" + "=" * 80)
        print("🚨 ANOMALY DETECTION")
        print("=" * 80)

        # Get payment timelines
        timeline_df = self.analyze_funding_lifecycle_duration()

        if timeline_df.empty:
            print("\n⚠️ No timeline data available for anomaly detection")
            return pd.DataFrame()

        # Calculate Z-scores
        mean_days = timeline_df['days_to_payment'].mean()
        std_days = timeline_df['days_to_payment'].std()

        timeline_df['z_score'] = (timeline_df['days_to_payment'] - mean_days) / std_days

        # Detect anomalies (|Z| > 2)
        anomalies = timeline_df[abs(timeline_df['z_score']) > 2].copy()

        if anomalies.empty:
            print("\n✅ No anomalies detected - all payments within normal range")
            return pd.DataFrame()

        print(f"\n🚨 Detected {len(anomalies)} anomalies:\n")

        for _, row in anomalies.iterrows():
            if row['z_score'] > 0:
                anomaly_type = "EXTREMELY SLOW"
                symbol = "🐌"
            else:
                anomaly_type = "EXTREMELY FAST"
                symbol = "⚡"

            print(f"{symbol} {anomaly_type}: {row['days_to_payment']:.0f} days (expected: {mean_days:.0f}±{std_days:.0f})")
            print(f"   Announcement ID: {row['announcement_id']}")
            print(f"   Z-score: {row['z_score']:.2f}")
            print()

        # Save anomalies
        anomalies_file = self.output_dir / 'detected_anomalies.csv'
        anomalies.to_csv(anomalies_file, index=False)
        print(f"✅ Anomalies saved: {anomalies_file}")

        # Insights
        print("\n💡 INSIGHTS:")

        if (anomalies['z_score'] > 0).any():
            slow_anomalies = anomalies[anomalies['z_score'] > 0]
            print(f"\n⚠️ {len(slow_anomalies)} payments took significantly longer than average:")
            print("   Investigate:")
            print("   - Were these complex programs requiring more approvals?")
            print("   - Were there political or administrative changes?")
            print("   - Was there resistance or pushback?")

        if (anomalies['z_score'] < 0).any():
            fast_anomalies = anomalies[anomalies['z_score'] < 0]
            print(f"\n✅ {len(fast_anomalies)} payments were significantly faster than average:")
            print("   Investigate:")
            print("   - What enabled rapid processing?")
            print("   - Were these emergency/crisis responses?")
            print("   - Can we replicate these conditions for other funding?")

        return anomalies

    def predict_payment_timeline(self) -> pd.DataFrame:
        """
        Predict when payments will occur for announced but unpaid funding

        Returns:
            DataFrame of predictions
        """
        print("\n" + "=" * 80)
        print("🔮 PAYMENT TIMELINE PREDICTION")
        print("=" * 80)

        # Get announced funding without verified payments
        result = self.supabase.table('v_funding_flow').select('*').execute()
        df = pd.DataFrame(result.data)

        unpaid = df[df['total_paid'] == 0].copy()

        if unpaid.empty:
            print("\n✅ All announced funding has been verified!")
            return pd.DataFrame()

        print(f"\n📊 {len(unpaid)} announcements waiting for verification\n")

        # Get historical average time to payment
        timeline_result = self.supabase.table('actual_payments') \
            .select('announcement_id, payment_date') \
            .execute()

        if not timeline_result.data:
            print("⚠️ No historical payment data - cannot predict")
            print("   Using default assumption: 180 days (6 months)")
            avg_days_to_payment = 180
        else:
            # Calculate average from historical data
            timeline_df = self.analyze_funding_lifecycle_duration()
            if not timeline_df.empty:
                avg_days_to_payment = timeline_df['days_to_payment'].mean()
            else:
                avg_days_to_payment = 180

        # Predict payment dates
        unpaid['announcement_date'] = pd.to_datetime(unpaid['announcement_date'])
        unpaid['days_since_announcement'] = (datetime.now() - unpaid['announcement_date']).dt.days
        unpaid['predicted_payment_date'] = unpaid['announcement_date'] + timedelta(days=avg_days_to_payment)
        unpaid['days_until_predicted_payment'] = (unpaid['predicted_payment_date'] - datetime.now()).dt.days
        unpaid['overdue'] = unpaid['days_until_predicted_payment'] < 0

        # Categorize
        def categorize_status(row):
            if row['overdue']:
                if abs(row['days_until_predicted_payment']) > 365:
                    return 'SEVERELY OVERDUE (1+ year)'
                elif abs(row['days_until_predicted_payment']) > 180:
                    return 'VERY OVERDUE (6+ months)'
                else:
                    return 'OVERDUE'
            elif row['days_until_predicted_payment'] < 30:
                return 'DUE SOON (within 30 days)'
            elif row['days_until_predicted_payment'] < 90:
                return 'DUE SOON (within 3 months)'
            else:
                return 'Not yet due'

        unpaid['status'] = unpaid.apply(categorize_status, axis=1)

        # Print predictions by status
        for status in ['SEVERELY OVERDUE (1+ year)', 'VERY OVERDUE (6+ months)', 'OVERDUE',
                       'DUE SOON (within 30 days)', 'DUE SOON (within 3 months)', 'Not yet due']:
            status_items = unpaid[unpaid['status'] == status]

            if not status_items.empty:
                print(f"\n{status}: {len(status_items)} programs\n")

                for _, row in status_items.head(10).iterrows():
                    symbol = "🚨" if 'OVERDUE' in status else "⏰" if 'SOON' in status else "📅"
                    print(f"{symbol} {row['program_name']}")
                    print(f"   Amount: ${row['amount_announced']/1000000:.1f}M")
                    print(f"   Announced: {row['announcement_date'].strftime('%Y-%m-%d')}")
                    print(f"   Days since: {row['days_since_announcement']}")
                    if row['overdue']:
                        print(f"   ⚠️ OVERDUE by {abs(row['days_until_predicted_payment'])} days")
                    else:
                        print(f"   Predicted payment: {row['predicted_payment_date'].strftime('%Y-%m-%d')}")
                    print()

        # Save predictions
        predictions_file = self.output_dir / 'payment_predictions.csv'
        unpaid[['program_name', 'amount_announced', 'announcement_date',
               'days_since_announcement', 'predicted_payment_date',
               'days_until_predicted_payment', 'status']].to_csv(predictions_file, index=False)

        print(f"\n✅ Predictions saved: {predictions_file}")

        # Summary
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"\nTotal unverified: ${unpaid['amount_announced'].sum()/1000000:.1f}M across {len(unpaid)} programs")
        print(f"Overdue: ${unpaid[unpaid['overdue']]['amount_announced'].sum()/1000000:.1f}M across {len(unpaid[unpaid['overdue']])} programs")
        print(f"\nAverage time to payment (historical): {avg_days_to_payment:.0f} days ({avg_days_to_payment/30:.1f} months)")

        return unpaid

    def generate_temporal_insights_report(self) -> str:
        """
        Generate comprehensive temporal insights report

        Returns:
            Path to report
        """
        print("\n" + "=" * 80)
        print("📝 GENERATING TEMPORAL INSIGHTS REPORT")
        print("=" * 80)

        report = []
        report.append("# Temporal Analysis - When Money Moves")
        report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("\n---\n")

        # Lifecycle duration
        timeline_df = self.analyze_funding_lifecycle_duration()

        if not timeline_df.empty:
            report.append("## ⏱️ Payment Timeline\n")
            avg_days = timeline_df['days_to_payment'].mean()
            median_days = timeline_df['days_to_payment'].median()

            report.append(f"**Average time from announcement to payment**: {avg_days:.0f} days ({avg_days/30:.1f} months)")
            report.append(f"**Median time**: {median_days:.0f} days ({median_days/30:.1f} months)")
            report.append("")

            if avg_days > 365:
                report.append("⚠️ **INSIGHT**: Payments take over a year on average")
                report.append("   - Consider process improvements to accelerate funding flow")
                report.append("   - Long delays may impact program effectiveness")
            elif avg_days > 180:
                report.append("📊 **INSIGHT**: Payments take 6+ months on average")
                report.append("   - This is within normal range for government funding")
                report.append("   - Monitor for delays beyond this timeframe")

            report.append("")

        # Seasonal patterns
        patterns = self.detect_seasonal_patterns()

        if patterns:
            report.append("\n## 📅 Seasonal Patterns\n")

            if patterns.get('budget_cycle_effect') == 'strong':
                report.append("⚠️ **Strong budget cycle effect detected**")
                report.append("   - Announcements cluster around May-July (budget period)")
                report.append("   - **Implication**: Timing advocacy for budget season increases success likelihood")
            elif patterns.get('budget_cycle_effect') == 'moderate':
                report.append("📊 **Moderate budget cycle pattern**")
                report.append("   - Some clustering around budget period")

            report.append("")

        # Anomalies
        anomalies = self.detect_anomalies()

        if not anomalies.empty:
            report.append("\n## 🚨 Detected Anomalies\n")

            slow_anomalies = anomalies[anomalies['z_score'] > 0]
            fast_anomalies = anomalies[anomalies['z_score'] < 0]

            if not slow_anomalies.empty:
                report.append(f"**{len(slow_anomalies)} unusually slow payments** (investigate delays)")
                report.append("")

            if not fast_anomalies.empty:
                report.append(f"**{len(fast_anomalies)} unusually fast payments** (learn from success)")
                report.append("")

        # Predictions
        predictions = self.predict_payment_timeline()

        if not predictions.empty:
            report.append("\n## 🔮 Predictions\n")

            overdue = predictions[predictions['overdue']]

            if not overdue.empty:
                report.append(f"⚠️ **{len(overdue)} programs overdue for verification**")
                report.append(f"   - Total: ${overdue['amount_announced'].sum()/1000000:.1f}M")
                report.append("   - **Action**: Prioritize ACNC checks for these programs")

            report.append("")

        # Implications
        report.append("\n## 💡 Implications for JusticeHub\n")
        report.append("### Story Opportunities")
        report.append("- **Overdue payments**: 'Where's the $24M? It's been X months since announcement'")
        report.append("- **Fast payments**: 'This program got funded in record time - why?'")
        report.append("- **Seasonal patterns**: 'Budget season is here - will Mount Isa get funding?'")
        report.append("")

        report.append("### Advocacy Timing")
        report.append("- Target budget season (May-July) for new funding proposals")
        report.append("- Monitor 6-month mark post-announcement for verification")
        report.append("- Raise alarm if payment exceeds 12 months with no verification")
        report.append("")

        # Save report
        report_file = self.output_dir / 'temporal_analysis_report.md'
        with open(report_file, 'w') as f:
            f.write('\n'.join(report))

        print(f"\n✅ Insights report saved: {report_file}")

        return str(report_file)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze temporal patterns in funding')
    parser.add_argument('--detect-anomalies', action='store_true',
                       help='Detect unusually fast or slow payments')
    parser.add_argument('--predict-timelines', action='store_true',
                       help='Predict when payments will occur')
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("⏱️  ADVANCED TEMPORAL ANALYSIS")
    print("=" * 80)

    try:
        analyzer = TemporalAnalyzer()

        # Core analyses
        analyzer.analyze_funding_lifecycle_duration()
        analyzer.detect_seasonal_patterns()

        # Optional analyses
        if args.detect_anomalies:
            analyzer.detect_anomalies()

        if args.predict_timelines:
            analyzer.predict_payment_timeline()

        # Generate report
        report_path = analyzer.generate_temporal_insights_report()

        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nResults saved to: analysis/temporal/")
        print("\n📊 What you can do now:")
        print("  1. Review insights: temporal_analysis_report.md")
        print("  2. Check predictions: payment_predictions.csv")
        print("  3. Investigate anomalies: detected_anomalies.csv")
        print("  4. Use for JusticeHub: Highlight overdue payments, seasonal patterns")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
