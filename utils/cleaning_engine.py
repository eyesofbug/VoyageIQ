import pandas as pd
import json
import os
import numpy as np

# Rule-based logic for tagging
CATEGORY_TAGS = {
    "Beach": ["scenic", "relaxation", "water"],
    "Temple": ["religious", "culture", "architecture"],
    "Hill Station": ["scenic", "nature", "weather"],
    "National Park": ["nature", "wildlife", "adventure"],
    "Waterfall": ["scenic", "nature", "water"],
    "Fort": ["history", "architecture", "culture"],
    "Palace": ["history", "architecture", "luxury"],
    "Museum": ["culture", "history", "education"],
    "Cave": ["history", "architecture", "adventure"],
    "Lake": ["scenic", "relaxation", "water"],
    "Forest Trail": ["nature", "adventure", "eco"],
}

# Rule-based logic for computed fields
CATEGORY_DEFAULTS = {
    "Beach": {"time": 3, "cost": 200, "group": True},
    "Temple": {"time": 1.5, "cost": 100, "group": True},
    "Hill Station": {"time": 24, "cost": 1000, "group": True},
    "National Park": {"time": 4, "cost": 500, "group": True},
    "Waterfall": {"time": 2, "cost": 100, "group": True},
    "Fort": {"time": 3, "cost": 300, "group": True},
    "Palace": {"time": 2, "cost": 500, "group": True},
    "Museum": {"time": 2, "cost": 200, "group": True},
    "Cave": {"time": 2.5, "cost": 150, "group": True},
    "Lake": {"time": 1.5, "cost": 300, "group": True},
    "Forest Trail": {"time": 4, "cost": 200, "group": True},
}

STATE_MAP = {
    "kerala": "Kerala",
    "kerla": "Kerala",
    "tamilnadu": "Tamil Nadu",
    "tamil nadu": "Tamil Nadu",
    "karnataka": "Karnataka",
    "goa": "Goa",
    "maharashtra": "Maharashtra",
    "rajasthan": "Rajasthan",
    "madhya pradesh": "Madhya Pradesh",
    "uttarakhand": "Uttarakhand",
    "himachal pradesh": "Himachal Pradesh",
    "sikkim": "Sikkim",
    "meghalaya": "Meghalaya",
    "jammu and kashmir": "Jammu and Kashmir",
    "j&k": "Jammu and Kashmir",
    "delhi": "Delhi",
}

def normalize_state(state):
    if not isinstance(state, str):
        return "Unknown"
    s = state.lower().strip()
    return STATE_MAP.get(s, state.title().strip())

def process_attractions(input_csv, output_json, max_items=300):
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found.")
        return

    df = pd.read_csv(input_csv)

    # Required columns
    required = ["Place Name", "State", "City", "Latitude", "Longitude", "Category"]
    df = df[required].copy()

    # Normalize
    df["State"] = df["State"].apply(normalize_state)
    df.drop_duplicates(subset=["Place Name", "State", "City"], inplace=True)
    
    # Ensure numeric coords
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors='coerce')
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors='coerce')
    df.dropna(subset=["Latitude", "Longitude"], inplace=True)

    # Conversion & Computed Fields
    processed = []
    for i, row in df.head(max_items).iterrows():
        cat = row["Category"]
        tags = CATEGORY_TAGS.get(cat, ["general"])
        defaults = CATEGORY_DEFAULTS.get(cat, {"time": 2, "cost": 200, "group": True})
        
        # Calculate popularity score (dummy rule: random 60-95 for now, or based on Category)
        pop_score = 80 if cat in ["Temple", "Beach"] else 70
        
        entry = {
            "id": f"ind_{i:03d}",
            "name": row["Place Name"],
            "state": row["State"],
            "city": row["City"],
            "area": row["City"], # Default area to city for now
            "latitude": float(row["Latitude"]),
            "longitude": float(row["Longitude"]),
            "tags": tags,
            "avg_time_hours": defaults["time"],
            "avg_cost_per_person": defaults["cost"],
            "group_friendly": defaults["group"],
            "popularity_score": pop_score
        }
        processed.append(entry)

    with open(output_json, 'w') as f:
        json.dump(processed, f, indent=4)
    
    print(f"Exported {len(processed)} attractions to {output_json}")

def process_eco_tourism(input_csv, output_json):
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found.")
        return

    df = pd.read_csv(input_csv)
    
    # Load existing attractions
    if os.path.exists(output_json):
        with open(output_json, 'r') as f:
            attractions = json.load(f)
    else:
        attractions = []

    last_id_num = len(attractions)
    
    new_entries = []
    for i, row in df.iterrows():
        entry = {
            "id": f"eco_{last_id_num + i:03d}",
            "name": row["Name"],
            "state": normalize_state(row["State"]),
            "city": row["District"],
            "area": row["District"],
            "latitude": 0.0, # Dummy coords if not provided
            "longitude": 0.0,
            "tags": ["eco", "nature", "trekking"],
            "avg_time_hours": float(row["Duration"]),
            "avg_cost_per_person": float(row["Entry Fee"]),
            "group_friendly": True,
            "popularity_score": random.randint(60, 75)
        }
        new_entries.append(entry)
    
    attractions.extend(new_entries)
    
    # Enforce total limit of 300
    attractions = attractions[:300]
    
    with open(output_json, 'w') as f:
        json.dump(attractions, f, indent=4)
    
    print(f"Appended {len(new_entries)} eco-tourism items (Total truncated to 300) to {output_json}")

def process_accommodations(input_hotel_json, output_prices_json, max_cities=25):
    if not os.path.exists(input_hotel_json):
        print(f"Error: {input_hotel_json} not found.")
        return

    with open(input_hotel_json, 'r') as f:
        hotels = json.load(f)
    
    df = pd.DataFrame(hotels)
    
    # Group by city and state
    agg_list = []
    for (city, state), group in df.groupby(['city', 'state']):
        prices = sorted(group['avg_price_per_night'].tolist())
        n = len(prices)
        if n == 0: continue
        
        # Split into 3 tiers
        budget_box = prices[:max(1, n//3)]
        luxury_box = prices[min(n-1, 2*n//3):]
        standard_box = prices[max(1, n//3):min(n-1, 2*n//3)] if n > 2 else prices
        
        agg_list.append({
            "city": city,
            "state": state,
            "budget_per_night": int(np.mean(budget_box)),
            "standard_per_night": int(np.mean(standard_box)) if standard_box else int(np.mean(prices)),
            "luxury_per_night": int(np.mean(luxury_box))
        })
    
    # Sort by some metric or just take top 25
    agg_list = agg_list[:max_cities]
    
    with open(output_prices_json, 'w') as f:
        json.dump(agg_list, f, indent=4)
    
    print(f"Exported {len(agg_list)} city price aggregates to {output_prices_json}")

import random # Ensure random is available for popularity_score

def process_seasonality(output_csv):
    # Data based on user request: Peak (1.3-1.5), Off (0.8-0.9), Normal (1.0)
    data = [
        ["state", "peak_months", "off_months", "peak_multiplier", "off_multiplier"],
        ["Kerala", "Dec,Jan,Oct,Nov", "Jun,Jul", 1.4, 0.85],
        ["Goa", "Nov,Dec,Jan,Feb", "Jun,Jul", 1.5, 0.8],
        ["Rajasthan", "Oct,Nov,Dec,Jan,Feb,Mar", "May,Jun", 1.5, 0.8],
        ["Uttarakhand", "May,Jun,Sep,Oct", "Jan,Feb", 1.4, 0.85],
        ["Himachal Pradesh", "May,Jun,Sep,Oct", "Jan,Feb", 1.4, 0.85],
        ["Tamil Nadu", "Apr,May,Jun", "Dec,Jan", 1.3, 0.9],
        ["Karnataka", "Oct,Nov,Dec,Jan", "Jul,Aug", 1.3, 0.9],
        ["Maharashtra", "Oct,Nov,Dec,Jan", "Jun,Jul", 1.3, 0.9],
        ["Sikkim", "Apr,May,Oct,Nov", "Jan,Feb", 1.5, 0.8],
        ["Meghalaya", "Mar,Apr,May,Jun", "Nov,Dec", 1.4, 0.85],
        ["Uttar Pradesh", "Oct,Nov,Dec,Jan,Feb", "May,Jun", 1.4, 0.85],
        ["Delhi", "Oct,Nov,Dec,Jan,Feb", "May,Jun", 1.3, 0.9],
    ]
    
    with open(output_csv, 'w', newline='') as f:
        import csv
        writer = csv.writer(f)
        writer.writerows(data)
    print(f"Exported seasonality data to {output_csv}")

if __name__ == "__main__":
    # Phase 1: Attractions
    process_attractions("data/raw_attractions.csv", "data/attractions_india.json")
    
    # Phase 2: Eco-Tourism
    process_eco_tourism("data/raw_eco_tourism.csv", "data/attractions_india.json")
    
    # Phase 3: Accommodation Aggregation
    process_accommodations("data/accommodation_india.json", "data/hotel_prices_by_city.json")

    # Phase 5: Seasonality
    process_seasonality("data/tourism_seasonality.csv")
