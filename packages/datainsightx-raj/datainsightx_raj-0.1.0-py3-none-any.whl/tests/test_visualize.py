import os
import pandas as pd
from datainsightx.visualize import visualize_overview

def test_visualize_overview_creates_file(tmp_path):
    # Temporary path for output file
    output_file = tmp_path / "test_report.html"

    df = pd.read_csv("tests/sample_data/sales_data.csv")

    # Run the visualization
    visualize_overview(df, output_html=str(output_file))

    # Check if the HTML file is created
    assert os.path.exists(output_file), "Visualization HTML file should be created"

    # Check if file is not empty
    assert output_file.stat().st_size > 0, "Visualization HTML file should not be empty"
