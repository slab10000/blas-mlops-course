"""Validate the loan data contract before any preprocessing or training."""
import os
os.environ.setdefault("GX_ANALYTICS_ENABLED", "False")
import great_expectations as gx
import pandas as pd

EXPECTED_COLUMNS = [
    "age", "annual_income", "months_employed", "loan_amount",
    "account_balance", "employment_type", "home_ownership", "defaulted",
]
# The clean reference data has a $12,000 floor. $1,000 is a conservative
# lab-specific plausibility bound, not a universal applicant eligibility rule.
MIN_ANNUAL_INCOME = 1_000


def build_suite(min_income=MIN_ANNUAL_INCOME):
    suite = gx.ExpectationSuite(name="loan_applications_suite")
    expectations = [
        gx.expectations.ExpectTableColumnsToMatchSet(
            column_set=EXPECTED_COLUMNS, exact_match=True),
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="age", min_value=18, max_value=100),
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="annual_income", min_value=min_income, max_value=1_000_000),
        gx.expectations.ExpectColumnValuesToNotBeNull(column="age"),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="employment_type",
            value_set=["salaried", "self_employed", "unemployed"]),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="home_ownership", value_set=["own", "mortgage", "rent"]),
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="defaulted", value_set=[0, 1]),
    ]
    for expectation in expectations:
        suite.add_expectation(expectation)
    return suite


def validation_result(df, min_income=MIN_ANNUAL_INCOME):
    context = gx.get_context(mode="ephemeral")
    context.enable_analytics(False)
    context.get_config().progress_bars = {"globally": False}
    source = context.data_sources.add_pandas("pandas_source")
    asset = source.add_dataframe_asset(name="loan_applications")
    batch_def = asset.add_batch_definition_whole_dataframe("batch_def")
    batch = batch_def.get_batch(batch_parameters={"dataframe": df})
    return batch.validate(build_suite(min_income), result_format="SUMMARY")


def validate(df: pd.DataFrame, min_income=MIN_ANNUAL_INCOME) -> bool:
    result = validation_result(df, min_income)
    stats = result.statistics
    print(f"Rows: {len(df)} | annual_income minimum: {min_income}")
    print(f"Expectations passed: {stats['successful_expectations']}/"
          f"{stats['evaluated_expectations']}")
    print("DATA VALIDATION PASSED" if result.success else "DATA VALIDATION FAILED")
    for item in result.results:
        if not item.success:
            col = item.expectation_config.kwargs.get("column", "(table)")
            print(f"  - {item.expectation_config.type} failed on column '{col}'"
                  f"; unexpected={item.result.get('unexpected_count', 'n/a')}")
    return bool(result.success)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv")
    parser.add_argument("--min-income", type=float, default=MIN_ANNUAL_INCOME,
                        help="Use 0 only to reproduce the intentionally weak Part 2 check.")
    args = parser.parse_args()
    raise SystemExit(0 if validate(pd.read_csv(args.csv), args.min_income) else 1)
