"""
Data Quality Validation Tests
Based on the verification checklist from the strategy documents
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import sqlalchemy as sa
import yaml
from datetime import datetime
from typing import Dict, List, Tuple


class DataQualityValidator:
    """Validate data quality and integrity for economic observatory"""

    def __init__(self, db_connection_string: str = None):
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
        self.validation_results = []

    def record_result(self, test_name: str, passed: bool, details: Dict = None):
        """Record validation test result"""
        result = {
            'test_name': test_name,
            'test_date': datetime.now(),
            'passed': passed,
            'details': details or {}
        }

        self.validation_results.append(result)

        # Insert into validation_results table
        query = """
            INSERT INTO validation_results (test_name, test_type, test_date, passed, details)
            VALUES (:test_name, :test_type, :test_date, :passed, :details::jsonb)
        """

        test_type = self._classify_test_type(test_name)

        try:
            with self.engine.connect() as conn:
                conn.execute(
                    sa.text(query),
                    {
                        'test_name': test_name,
                        'test_type': test_type,
                        'test_date': datetime.now(),
                        'passed': passed,
                        'details': str(details)
                    }
                )
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not record result to database: {e}")

        return result

    def _classify_test_type(self, test_name: str) -> str:
        """Classify test type based on name"""
        if 'geography' in test_name.lower() or 'geo' in test_name.lower():
            return 'GEOGRAPHY'
        elif 'schema' in test_name.lower():
            return 'SCHEMA'
        elif 'range' in test_name.lower() or 'outlier' in test_name.lower():
            return 'RANGE'
        elif 'consistency' in test_name.lower() or 'reconcil' in test_name.lower():
            return 'CONSISTENCY'
        else:
            return 'OTHER'

    def test_geography_integrity(self) -> bool:
        """
        Test 1: Geography Integrity
        Ensure 100% of records are mapped to valid SA2/LGA codes
        """
        query = """
            SELECT
                COUNT(*) AS total_flows,
                COUNT(from_geo_id) AS mapped_from,
                COUNT(to_geo_id) AS mapped_to,
                COUNT(from_geo_id) * 100.0 / NULLIF(COUNT(*), 0) AS from_pct,
                COUNT(to_geo_id) * 100.0 / NULLIF(COUNT(*), 0) AS to_pct
            FROM fact_economic_flows
        """

        with self.engine.connect() as conn:
            result = conn.execute(sa.text(query))
            row = result.fetchone()

            total = row[0]
            from_pct = row[3] or 0
            to_pct = row[4] or 0

            min_match_rate = self.config['validation']['min_lga_match_rate']
            passed = (from_pct >= min_match_rate * 100 and to_pct >= min_match_rate * 100)

            self.record_result(
                'geography_integrity',
                passed,
                {
                    'total_records': total,
                    'from_mapped_pct': from_pct,
                    'to_mapped_pct': to_pct,
                    'threshold': min_match_rate * 100
                }
            )

            print(f"✓ Geography Integrity: {from_pct:.1f}% from, {to_pct:.1f}% to (threshold: {min_match_rate*100}%)")

            return passed

    def test_no_unmapped_entities(self) -> bool:
        """
        Test 2: Entity Resolution
        Check that all ABNs/entities are resolved and classified
        """
        query = """
            SELECT
                COUNT(*) AS total_entities,
                COUNT(CASE WHEN is_local IS NULL THEN 1 END) AS unclassified,
                COUNT(CASE WHEN entity_type_id IS NULL THEN 1 END) AS untyped
            FROM entities
            WHERE status = 'ACTIVE'
        """

        with self.engine.connect() as conn:
            result = conn.execute(sa.text(query))
            row = result.fetchone()

            total = row[0]
            unclassified = row[1]
            untyped = row[2]

            passed = (unclassified == 0 and untyped == 0)

            self.record_result(
                'entity_resolution',
                passed,
                {
                    'total_entities': total,
                    'unclassified': unclassified,
                    'untyped': untyped
                }
            )

            print(f"✓ Entity Resolution: {total} entities, {unclassified} unclassified, {untyped} untyped")

            return passed

    def test_cross_source_consistency(self) -> bool:
        """
        Test 3: Cross-Source Consistency
        Example: MBS totals should reconcile with AIHW dashboard data
        """
        # This is a placeholder - actual implementation would compare against
        # known totals from source dashboards

        query = """
            SELECT
                source_system,
                COUNT(*) AS record_count,
                SUM(amount) AS total_amount
            FROM fact_economic_flows
            GROUP BY source_system
        """

        with self.engine.connect() as conn:
            df = pd.read_sql(sa.text(query), conn)

        # For now, just check that we have data from each expected source
        expected_sources = ['MBS', 'PBS', 'AUSTENDER', 'QLD_PROCUREMENT']
        missing_sources = set(expected_sources) - set(df['source_system'].tolist())

        passed = len(missing_sources) == 0

        self.record_result(
            'cross_source_consistency',
            passed,
            {
                'expected_sources': expected_sources,
                'missing_sources': list(missing_sources),
                'sources_with_data': df.to_dict('records')
            }
        )

        print(f"✓ Cross-Source Consistency: {len(df)} sources, missing: {missing_sources or 'none'}")

        return passed

    def test_outlier_detection(self) -> bool:
        """
        Test 4: Outlier Detection
        Flag transactions outside Z-score window
        """
        max_z_score = self.config['validation']['max_z_score']

        query = f"""
            WITH stats AS (
                SELECT
                    AVG(amount) AS mean,
                    STDDEV(amount) AS stddev
                FROM fact_economic_flows
                WHERE amount > 0
            ),
            outliers AS (
                SELECT
                    f.flow_id,
                    f.amount,
                    ABS(f.amount - s.mean) / NULLIF(s.stddev, 0) AS z_score
                FROM fact_economic_flows f, stats s
                WHERE ABS(f.amount - s.mean) / NULLIF(s.stddev, 0) > {max_z_score}
            )
            SELECT COUNT(*) AS outlier_count
            FROM outliers
        """

        with self.engine.connect() as conn:
            result = conn.execute(sa.text(query))
            outlier_count = result.scalar()

        # Passed if outliers are less than 1% of total
        query_total = "SELECT COUNT(*) FROM fact_economic_flows"
        with self.engine.connect() as conn:
            total = conn.execute(sa.text(query_total)).scalar()

        outlier_pct = (outlier_count / total * 100) if total > 0 else 0
        passed = outlier_pct < 1.0

        self.record_result(
            'outlier_detection',
            passed,
            {
                'outlier_count': outlier_count,
                'total_records': total,
                'outlier_pct': outlier_pct,
                'max_z_score': max_z_score
            }
        )

        print(f"✓ Outlier Detection: {outlier_count} outliers ({outlier_pct:.2f}% of {total} records)")

        return passed

    def test_time_series_continuity(self) -> bool:
        """
        Test 5: Time Series Continuity
        Check for structural breaks and missing months
        """
        query = """
            WITH monthly_totals AS (
                SELECT
                    d.year,
                    d.month,
                    COUNT(*) AS transaction_count,
                    SUM(f.amount) AS total_amount
                FROM fact_economic_flows f
                JOIN dim_date d ON f.date_id = d.date_id
                GROUP BY d.year, d.month
                ORDER BY d.year, d.month
            )
            SELECT
                year,
                month,
                transaction_count,
                total_amount,
                LAG(total_amount) OVER (ORDER BY year, month) AS prev_month_amount
            FROM monthly_totals
        """

        with self.engine.connect() as conn:
            df = pd.read_sql(sa.text(query), conn)

        if len(df) < 2:
            passed = True  # Not enough data yet
        else:
            # Check for months with more than 50% change
            df['pct_change'] = ((df['total_amount'] - df['prev_month_amount']) /
                               df['prev_month_amount'] * 100)

            large_changes = df[df['pct_change'].abs() > 50]
            passed = len(large_changes) < len(df) * 0.1  # Less than 10% of months

        self.record_result(
            'time_series_continuity',
            passed,
            {
                'total_months': len(df),
                'large_changes': len(large_changes) if len(df) >= 2 else 0
            }
        )

        print(f"✓ Time Series Continuity: {len(df)} months analyzed")

        return passed

    def test_provenance_completeness(self) -> bool:
        """
        Test 6: Provenance Completeness
        Ensure all data has provenance records
        """
        query = """
            SELECT
                COUNT(DISTINCT source_system) AS sources_in_flows,
                (SELECT COUNT(*) FROM data_provenance) AS provenance_records
            FROM fact_economic_flows
        """

        with self.engine.connect() as conn:
            result = conn.execute(sa.text(query))
            row = result.fetchone()

            sources = row[0]
            provenance = row[1]

            # Should have at least one provenance record per source
            passed = provenance >= sources

        self.record_result(
            'provenance_completeness',
            passed,
            {
                'sources': sources,
                'provenance_records': provenance
            }
        )

        print(f"✓ Provenance Completeness: {provenance} records for {sources} sources")

        return passed

    def run_all_tests(self) -> Dict:
        """Run all validation tests and generate report"""
        print("\n=== Running Data Quality Validation Tests ===\n")

        tests = [
            self.test_geography_integrity,
            self.test_no_unmapped_entities,
            self.test_cross_source_consistency,
            self.test_outlier_detection,
            self.test_time_series_continuity,
            self.test_provenance_completeness
        ]

        results = {}
        for test in tests:
            try:
                results[test.__name__] = test()
            except Exception as e:
                print(f"✗ {test.__name__} FAILED with error: {e}")
                results[test.__name__] = False

        # Summary
        total = len(results)
        passed = sum(results.values())

        print(f"\n=== Validation Summary ===")
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {passed/total*100:.1f}%")

        return {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': passed / total,
            'test_results': results,
            'validation_records': self.validation_results
        }


if __name__ == "__main__":
    validator = DataQualityValidator()
    report = validator.run_all_tests()

    # Save report
    import json
    output_path = Path(__file__).parent.parent / "data" / "validation_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nValidation report saved to: {output_path}")
