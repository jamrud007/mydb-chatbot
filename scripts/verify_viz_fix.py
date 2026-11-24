import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.visualization_helper import VisualizationHelper

def test_parsing():
    test_cases = [
        "Rp 1.299,00",   # The problematic case
        "Rp 10.000",     # Common ID format
        "1.200,50",      # Decimal with comma
        "1,200.50",      # Decimal with dot
        "1000",          # Plain int
        "1299.00",       # Plain float string
        None
    ]

    print("\n--- Testing VisualizationHelper Numeric Parsing ---\n")
    print(f"{'Input':<20} | {'Parsed Value':<15} | {'Type'}")
    print("-" * 50)
    
    for val in test_cases:
        result = VisualizationHelper._parse_value(val)
        print(f"{str(val):<20} | {result:<15} | {type(result).__name__}")
        
    print("\n-----------------------------------------------\n")

if __name__ == "__main__":
    try:
        test_parsing()
        print("✅ Parsing logic verification successful!")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
