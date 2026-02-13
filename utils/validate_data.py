import json
import os
import pandas as pd

def validate_datasets():
    errors = []
    
    # 1. Attractions Validation
    attr_path = "data/attractions_india.json"
    if not os.path.exists(attr_path):
        errors.append("attractions_india.json missing")
    else:
        with open(attr_path, 'r') as f:
            data = json.load(f)
            if len(data) > 300:
                errors.append(f"Attractions count too high: {len(data)}")
            
            # Check structure of first item
            if data:
                required_keys = ["id", "name", "state", "city", "area", "latitude", "longitude", "tags", "avg_time_hours", "avg_cost_per_person", "group_friendly", "popularity_score"]
                first = data[0]
                for key in required_keys:
                    if key not in first:
                        errors.append(f"Missing key in attractions: {key}")
                
                if not isinstance(first["latitude"], (int, float)):
                    errors.append("Latitude is not numeric")
                if not isinstance(first["tags"], list):
                    errors.append("Tags is not a list")

    # 2. Stats Validation
    stats_path = "data/tourism_stats_india.csv"
    if not os.path.exists(stats_path):
        errors.append("tourism_stats_india.csv missing")
    else:
        df = pd.read_csv(stats_path)
        required_cols = ["Year", "Month", "Domestic_Visits", "Foreign_Visits"]
        for col in required_cols:
            if col not in df.columns:
                errors.append(f"Missing column in stats: {col}")

    if not errors:
        print("All datasets validated successfully!")
    else:
        print("Validation errors found:")
        for e in errors:
            print(f"- {e}")

if __name__ == "__main__":
    validate_datasets()
