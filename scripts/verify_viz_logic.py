
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.visualization_helper import VisualizationHelper

def print_result(name, config):
    print(f"\n--- Test: {name} ---")
    if config.get('can_visualize'):
        print(f"Type: {config['chart_type']}")
        print(f"Reason: {config.get('reason')}")
        if config.get('is_mixed_scale'):
            print("Mixed Scale Detected")
    else:
        print(f"Failed: {config.get('reason')}")

def run_tests():
    print("Testing Visualization Logic...")

    # Case 1: Trend (Line Chart)
    # Data: Monthly sales
    results_trend = [
        {'month': '2023-01', 'sales': 100},
        {'month': '2023-02', 'sales': 120},
        {'month': '2023-03', 'sales': 150},
    ]
    cols_trend = ['month', 'sales']
    print_result("Trend (Time Series)", VisualizationHelper.analyze_for_visualization(results_trend, cols_trend, "sales trend"))

    # Case 2: Comparison (Bar Chart)
    # Data: Top categories
    results_bar = [
        {'category': 'Electronics', 'revenue': 5000},
        {'category': 'Books', 'revenue': 3000},
        {'category': 'Clothing', 'revenue': 2000},
    ]
    cols_bar = ['category', 'revenue']
    print_result("Comparison (Category)", VisualizationHelper.analyze_for_visualization(results_bar, cols_bar, "top categories"))

    # Case 3: Composition (Pie Chart)
    # Data: Order Status (few categories)
    results_pie = [
        {'status': 'delivered', 'count': 800},
        {'status': 'shipped', 'count': 100},
        {'status': 'canceled', 'count': 50},
    ]
    cols_pie = ['status', 'count']
    print_result("Composition (Pie)", VisualizationHelper.analyze_for_visualization(results_pie, cols_pie, "composition of status"))

    # Case 4: Relationship (Scatter)
    # Data: Price vs Rating (No dimensions, just metrics)
    results_scatter = [
        {'price': 100, 'rating': 4.5},
        {'price': 50, 'rating': 3.0},
        {'price': 200, 'rating': 5.0},
    ]
    # Note: In real query results, these might be aggregated rows, but let's test the "No Dim + 2 Metrics" rule
    cols_scatter = ['price', 'rating']
    print_result("Relationship (Scatter)", VisualizationHelper.analyze_for_visualization(results_scatter, cols_scatter, "correlation price rating"))

    # Case 5: Mixed Scales (Bar + Tooltip)
    # Data: Revenue (Millions) vs Rating (1-5)
    results_mixed = [
        {'product': 'A', 'revenue': 1000000, 'rating': 4.5},
        {'product': 'B', 'revenue': 500000, 'rating': 3.8},
    ]
    cols_mixed = ['product', 'revenue', 'rating']
    print_result("Mixed Scales (Bar+Tooltip)", VisualizationHelper.analyze_for_visualization(results_mixed, cols_mixed, "revenue and rating"))

if __name__ == "__main__":
    run_tests()
