# datainsightx/cli.py

import argparse
import pandas as pd
import sys
from datainsightx.quality import missing_value_report
from datainsightx.visualize import visualize_overview

def main():
    parser = argparse.ArgumentParser(
        prog="datainsightx",
        description="📊 DataInsightX: A tool for data quality checks and automated visualization"
    )

    parser.add_argument(
        "command",
        choices=["analyze", "quality", "visualize"],
        help="Command to run: analyze (all), quality (text report), visualize (HTML dashboard)"
    )

    parser.add_argument(
        "file",
        help="Path to CSV file to analyze"
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Path to save HTML dashboard (default: datainsightx_report.html)",
        default="datainsightx_report.html"
    )

    args = parser.parse_args()

    # Load the CSV
    try:
        df = pd.read_csv(args.file)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)

    # Execute based on command
    if args.command == "quality":
        print("🔍 Running data quality checks...\n")
        report = missing_value_report(df)
        if report.empty:
            print("✅ No missing values found!")
        else:
            print(report)
        print("\n✅ Quality check complete.")

    elif args.command == "visualize":
        print("📊 Generating dashboard...\n")
        visualize_overview(df, output_html=args.output)
        print(f"✅ Dashboard saved as {args.output}")

    elif args.command == "analyze":
        print("🚀 Running full analysis (quality + visualization)...\n")
        report = missing_value_report(df)
        print("==== DATA QUALITY REPORT ====")
        if report.empty:
            print("✅ No missing values found!\n")
        else:
            print(report)
            print()
        visualize_overview(df, output_html=args.output)
        print(f"✅ Full report ready: {args.output}")
