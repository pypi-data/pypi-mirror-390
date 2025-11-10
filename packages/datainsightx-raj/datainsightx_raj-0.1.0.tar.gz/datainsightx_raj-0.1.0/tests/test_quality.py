import pandas as pd
from datainsightx.quality import missing_value_report

def test_missing_value_report():
    # Load the test dataset
    df = pd.read_csv("tests/sample_data/sales_data.csv")

    # Run the function
    report = missing_value_report(df)

    # Check if expected columns exist
    assert "Missing Values" in report.columns, "Report should contain 'Missing Values' column"
    assert "Percentage" in report.columns, "Report should contain 'Percentage' column"

    # Discount column should have 1 missing value
    assert "Discount" in report.index, "Discount column should be in the report"
    missing_value = int(report.loc["Discount", "Missing Values"])
    assert missing_value == 1, f"Expected 1 missing value in Discount column, got {missing_value}"

    # Percentage should be between 0 and 100
    percent = report.loc["Discount", "Percentage"]
    assert 0 <= percent <= 100, f"Percentage should be within 0-100 range, got {percent}"
