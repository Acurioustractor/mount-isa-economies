"""
Leakage Analysis Tool
Identifies where money is leaving the local economy and opportunities for import replacement
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import sqlalchemy as sa
from typing import Dict, List, Tuple
import yaml


class LeakageAnalyzer:
    """Analyze economic leakages and identify import replacement opportunities"""

    def __init__(self, db_connection_string: str = None):
        """
        Initialize analyzer

        Args:
            db_connection_string: SQLAlchemy connection string
        """
        # Load config
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Setup database connection
        if db_connection_string is None:
            db_config = self.config['database']
            db_connection_string = (
                f"postgresql://{db_config['user']}:{db_config['password']}@"
                f"{db_config['host']}:{db_config['port']}/{db_config['name']}"
            )

        self.engine = sa.create_engine(db_connection_string)

    def calculate_total_leakage(self, year: int = None) -> float:
        """
        Calculate total economic leakage for a given year

        Args:
            year: Year to analyze (default: current year)

        Returns:
            Total leakage amount in dollars
        """
        query = """
            SELECT SUM(amount) AS total_leakage
            FROM fact_economic_flows f
            JOIN dim_date d ON f.date_id = d.date_id
            WHERE f.is_leakage = TRUE
              AND d.year = COALESCE(:year, EXTRACT(YEAR FROM CURRENT_DATE))
        """

        with self.engine.connect() as conn:
            result = conn.execute(sa.text(query), {'year': year})
            return result.scalar() or 0.0

    def identify_top_leakages(self, limit: int = 20) -> pd.DataFrame:
        """
        Identify top categories where money is leaking out

        Args:
            limit: Number of top categories to return

        Returns:
            DataFrame with leakage categories ranked by amount
        """
        query = """
            SELECT
                i.division_title AS industry_division,
                i.anzsic_title AS industry,
                p.program_type,
                SUM(f.amount) AS total_leakage,
                COUNT(f.flow_id) AS transaction_count,
                AVG(f.amount) AS avg_transaction_amount
            FROM fact_economic_flows f
            LEFT JOIN dim_industry i ON f.industry_id = i.industry_id
            LEFT JOIN dim_program p ON f.program_id = p.program_id
            JOIN dim_date d ON f.date_id = d.date_id
            WHERE f.is_leakage = TRUE
              AND d.year = EXTRACT(YEAR FROM CURRENT_DATE)
            GROUP BY i.division_title, i.anzsic_title, p.program_type
            ORDER BY total_leakage DESC
            LIMIT :limit
        """

        with self.engine.connect() as conn:
            df = pd.read_sql(sa.text(query), conn, params={'limit': limit})

        return df

    def identify_service_gaps(self, min_spending: float = 100000) -> pd.DataFrame:
        """
        Identify service gaps: high external spending with low local capacity

        Args:
            min_spending: Minimum annual external spending to consider

        Returns:
            DataFrame with service gaps ranked by opportunity
        """
        query = """
            SELECT
                i.anzsic_code,
                i.anzsic_title AS industry,
                i.division_title AS industry_division,
                SUM(f.amount) AS external_spending,
                COUNT(DISTINCT pe.entity_id) AS local_provider_count,
                SUM(f.amount) / NULLIF(COUNT(DISTINCT pe.entity_id), 0) AS spending_per_provider,
                COUNT(f.flow_id) AS external_transaction_count
            FROM fact_economic_flows f
            JOIN dim_industry i ON f.industry_id = i.industry_id
            LEFT JOIN entities pe ON pe.is_local = TRUE
                                   AND pe.primary_anzsic = i.anzsic_code
                                   AND pe.status = 'ACTIVE'
            JOIN dim_date d ON f.date_id = d.date_id
            WHERE f.is_leakage = TRUE
              AND d.year = EXTRACT(YEAR FROM CURRENT_DATE)
            GROUP BY i.anzsic_code, i.anzsic_title, i.division_title
            HAVING SUM(f.amount) >= :min_spending
            ORDER BY spending_per_provider DESC, external_spending DESC
        """

        with self.engine.connect() as conn:
            df = pd.read_sql(sa.text(query), conn, params={'min_spending': min_spending})

        # Calculate opportunity score
        # Higher score = bigger opportunity for local replacement
        df['opportunity_score'] = (
            df['external_spending'] /
            (df['local_provider_count'] + 1)  # Add 1 to avoid division by zero
        )

        df = df.sort_values('opportunity_score', ascending=False)

        return df

    def analyze_local_vs_external_trend(self, months: int = 24) -> pd.DataFrame:
        """
        Analyze trend of local vs external spending over time

        Args:
            months: Number of months to analyze

        Returns:
            DataFrame with monthly local vs external spending
        """
        query = """
            SELECT
                d.year,
                d.month,
                d.date,
                SUM(CASE WHEN f.is_leakage = FALSE THEN f.amount ELSE 0 END) AS local_spending,
                SUM(CASE WHEN f.is_leakage = TRUE THEN f.amount ELSE 0 END) AS external_spending,
                SUM(f.amount) AS total_spending,
                SUM(CASE WHEN f.is_leakage = FALSE THEN f.amount ELSE 0 END) /
                NULLIF(SUM(f.amount), 0) * 100 AS local_percentage
            FROM fact_economic_flows f
            JOIN dim_date d ON f.date_id = d.date_id
            WHERE d.date >= CURRENT_DATE - INTERVAL ':months months'
            GROUP BY d.year, d.month, d.date
            ORDER BY d.date
        """

        with self.engine.connect() as conn:
            df = pd.read_sql(sa.text(query), conn, params={'months': months})

        return df

    def estimate_local_multiplier(self, spending_amount: float = 1000000) -> Dict:
        """
        Estimate the local multiplier effect

        Based on research showing local businesses recirculate ~48% vs chains ~14%

        Args:
            spending_amount: Amount to analyze (default $1M)

        Returns:
            Dict with multiplier estimates
        """
        LOCAL_MULTIPLIER = 0.48
        EXTERNAL_MULTIPLIER = 0.14

        # Calculate rounds of spending
        def calculate_total_impact(initial: float, multiplier: float, rounds: int = 5) -> float:
            total = 0
            current = initial
            for _ in range(rounds):
                current *= multiplier
                total += current
            return total

        local_impact = spending_amount + calculate_total_impact(spending_amount, LOCAL_MULTIPLIER)
        external_impact = spending_amount + calculate_total_impact(spending_amount, EXTERNAL_MULTIPLIER)

        return {
            'initial_spending': spending_amount,
            'local_total_impact': local_impact,
            'external_total_impact': external_impact,
            'difference': local_impact - external_impact,
            'local_multiplier': local_impact / spending_amount,
            'external_multiplier': external_impact / spending_amount
        }

    def calculate_localization_target(self, target_percentage: float = 10) -> Dict:
        """
        Calculate what a X% localization would mean in dollar terms

        Args:
            target_percentage: Target percentage increase in localization

        Returns:
            Dict with target metrics
        """
        # Get current state
        query_current = """
            SELECT
                SUM(amount) AS total_spending,
                SUM(CASE WHEN is_leakage = FALSE THEN amount ELSE 0 END) AS current_local,
                SUM(CASE WHEN is_leakage = TRUE THEN amount ELSE 0 END) AS current_external,
                SUM(CASE WHEN is_leakage = FALSE THEN amount ELSE 0 END) /
                NULLIF(SUM(amount), 0) * 100 AS current_local_pct
            FROM fact_economic_flows f
            JOIN dim_date d ON f.date_id = d.date_id
            WHERE d.year = EXTRACT(YEAR FROM CURRENT_DATE)
        """

        with self.engine.connect() as conn:
            result = conn.execute(sa.text(query_current))
            row = result.fetchone()

            total_spending = float(row[0] or 0)
            current_local = float(row[1] or 0)
            current_external = float(row[2] or 0)
            current_local_pct = float(row[3] or 0)

        # Calculate targets
        target_local_pct = current_local_pct + target_percentage
        target_local_amount = total_spending * (target_local_pct / 100)
        amount_to_localize = target_local_amount - current_local

        # Estimate jobs created (rough estimate: $100k per job)
        estimated_jobs = amount_to_localize / 100000

        return {
            'total_spending': total_spending,
            'current_local_amount': current_local,
            'current_local_pct': current_local_pct,
            'target_local_pct': target_local_pct,
            'target_local_amount': target_local_amount,
            'amount_to_localize': amount_to_localize,
            'estimated_jobs_created': estimated_jobs
        }

    def generate_leakage_report(self, output_path: str = None) -> Dict:
        """
        Generate comprehensive leakage analysis report

        Args:
            output_path: Optional path to save report

        Returns:
            Dict with all analysis results
        """
        print("Generating Mount Isa Economic Leakage Report...")

        report = {
            'generated_at': pd.Timestamp.now().isoformat(),
            'total_leakage': self.calculate_total_leakage(),
            'top_leakages': self.identify_top_leakages().to_dict('records'),
            'service_gaps': self.identify_service_gaps().to_dict('records'),
            'localization_target': self.calculate_localization_target(),
            'multiplier_analysis': self.estimate_local_multiplier()
        }

        if output_path:
            import json
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"Report saved to: {output_path}")

        return report


if __name__ == "__main__":
    # Example usage
    analyzer = LeakageAnalyzer()

    print("\n=== Mount Isa Economic Leakage Analysis ===\n")

    print(f"Total Annual Leakage: ${analyzer.calculate_total_leakage():,.2f}")

    print("\nTop 10 Leakage Categories:")
    top_leakages = analyzer.identify_top_leakages(10)
    print(top_leakages.to_string())

    print("\nTop 10 Service Gaps (Opportunities):")
    gaps = analyzer.identify_service_gaps()
    print(gaps.head(10).to_string())

    print("\n10% Localization Target:")
    target = analyzer.calculate_localization_target(10)
    print(f"  Current Local: ${target['current_local_amount']:,.2f} ({target['current_local_pct']:.1f}%)")
    print(f"  Target Local: ${target['target_local_amount']:,.2f} ({target['target_local_pct']:.1f}%)")
    print(f"  Amount to Localize: ${target['amount_to_localize']:,.2f}")
    print(f"  Estimated Jobs Created: {target['estimated_jobs_created']:.0f}")
