import json
import random

cities_with_states = {
    "Munnar": "Kerala", "Alleppey": "Kerala", "Varkala": "Kerala", "Kochi": "Kerala",
    "Jaipur": "Rajasthan", "Amritsar": "Punjab", "Rishikesh": "Uttarakhand",
    "Manali": "Himachal Pradesh", "Old Goa": "Goa", "Mumbai": "Maharashtra",
    "Madurai": "Tamil Nadu", "Ooty": "Tamil Nadu", "Hampi": "Karnataka", "Madikeri": "Karnataka"
}

hotel_types = ["Luxury Hotel", "Boutique Hotel", "Guest House", "Homestay", "Resort", "Budget Hotel"]

def generate_accommodation_data(output_file, items_per_city=5):
    accommodations = []
    for city, state in cities_with_states.items():
        for i in range(items_per_city):
            h_type = random.choice(hotel_types)
            base_price = random.randint(1500, 15000) if "Luxury" in h_type or "Resort" in h_type else random.randint(500, 3000)
            
            accommodations.append({
                "hotel_id": f"hot_{city[:3].lower()}_{i:02d}",
                "name": f"{city} {h_type} {i+1}",
                "city": city,
                "state": state,
                "type": h_type,
                "avg_price_per_night": base_price,
                "rating": round(random.uniform(3.5, 4.9), 1),
                "amenities": random.sample(["WiFi", "Pool", "Breakfast", "Parking", "AC", "Gym"], k=random.randint(2, 4)),
                "group_friendly": True if h_type in ["Resort", "Guest House", "Homestay"] else random.choice([True, False])
            })
    
    with open(output_file, 'w') as f:
        json.dump(accommodations, f, indent=4)
    print(f"Generated {len(accommodations)} accommodation entries in {output_file}")

if __name__ == "__main__":
    generate_accommodation_data("data/accommodation_india.json")
