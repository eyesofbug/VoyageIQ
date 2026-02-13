import random
import json
import os
import pandas as pd
import numpy as np
import math

# Data Loading Helpers using Pandas
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_data():
    attractions_df = pd.read_json(os.path.join(DATA_DIR, "attractions_india.json"))
    hotels_df = pd.read_json(os.path.join(DATA_DIR, "hotel_prices_by_city.json"))
    vehicles_df = pd.read_json(os.path.join(DATA_DIR, "transport_vehicles.json"))
    seasonality_df = pd.read_csv(os.path.join(DATA_DIR, "tourism_seasonality.csv"))
    return attractions_df, hotels_df, vehicles_df, seasonality_df

ATTRACTIONS, HOTELS, VEHICLES, SEASONALITY = load_data()

GROUP_INTELLIGENCE_SPECS = {
    "Solo": {"density": 4, "time_mult": 1.0, "pref_boost": {}},
    "Couple": {"density": 3, "time_mult": 1.1, "pref_boost": {"Scenic": 1.5, "Relaxation": 1.5}},
    "Friends": {"density": 4, "time_mult": 1.0, "pref_boost": {"Adventure": 1.5, "Nightlife": 1.5}},
    "Family": {"density": 3, "time_mult": 1.3, "pref_boost": {"Culture": 1.5, "Leisure": 1.5}},
    "College Group": {"density": 4, "time_mult": 1.1, "pref_boost": {"Adventure": 1.5, "Budget": 1.5}}
}

# --- GEOGRAPHIC ROUTING LOGIC ---
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def haversine_travel_time(lat1, lon1, lat2, lon2):
    dist = calculate_haversine_distance(lat1, lon1, lat2, lon2)
    # 30 km/h avg city speed, plus 15m traffic buffer
    transit_mins = (dist / 30) * 60
    return transit_mins + 15

TIME_SLOTS = [
    "09:00 AM - 11:30 AM", 
    "11:45 AM - 01:00 PM", 
    "02:45 PM - 05:00 PM", 
    "05:30 PM - 07:30 PM"
]

def get_seasonal_multiplier(destination, month):
    city_match = ATTRACTIONS[ATTRACTIONS['city'] == destination]
    if city_match.empty:
        city_match = ATTRACTIONS[ATTRACTIONS['state'] == destination]
    
    if city_match.empty: return 1.0
        
    state = city_match.iloc[0]['state']
    state_row = SEASONALITY[SEASONALITY['state'] == state]
    if state_row.empty: return 1.0
        
    row = state_row.iloc[0]
    # New format: state,peak_months,off_months,peak_multiplier,off_multiplier
    peak = str(row['peak_months']).split(',')
    off = str(row['off_months']).split(',')
    
    # Handle both short and long month names
    curr_month_short = month[:3]
    
    if any(m.strip().startswith(curr_month_short) for m in peak): 
        return float(row['peak_multiplier'])
    elif any(m.strip().startswith(curr_month_short) for m in off): 
        return float(row['off_multiplier'])
    return 1.0

def calculate_detailed_budget(user_budget, travel_type, days, month, activity_count, group_type="Solo", destination="Kerala"):
    hotel_row = HOTELS[HOTELS['city'] == destination]
    if hotel_row.empty:
        city_df = ATTRACTIONS[ATTRACTIONS['city'] == destination]
        if not city_df.empty:
            state = city_df.iloc[0]['state']
            hotel_row = HOTELS[HOTELS['city'] == state]

    price_col = f"{travel_type.lower()}_per_night"
    base_hotel_price = hotel_row.iloc[0][price_col] if not hotel_row.empty else 5000
    
    multiplier = get_seasonal_multiplier(destination, month)
    hotel_total = base_hotel_price * days * multiplier
    
    food_total = 1500 * days if travel_type != "Budget" else 800 * days
    transport_total = 2500 * days if travel_type != "Budget" else 1000 * days
    
    if group_type == "Couple": hotel_total *= 1.2
    elif group_type == "Friends": hotel_total *= 0.8
    elif group_type == "Family": transport_total *= 1.4
    elif group_type == "College Group": hotel_total *= 0.7
    
    city_acts = ATTRACTIONS[ATTRACTIONS['city'] == destination]
    avg_act_cost = city_acts['avg_cost_per_person'].mean() if not city_acts.empty else 1000
    activity_total = activity_count * avg_act_cost * multiplier
    
    subtotal = hotel_total + food_total + transport_total + activity_total
    buffer = subtotal * 0.10
    total_estimated = subtotal + buffer
    
    score = 100 if user_budget >= total_estimated else int((user_budget / total_estimated) * 100)
    color = "green" if score >= 90 else "blue" if score >= 80 else "orange" if score >= 60 else "red"
        
    return {
        "total_estimated": int(total_estimated),
        "score": score,
        "status": "Optimal" if score >= 90 else "Review Required",
        "color": color,
        "optimization_applied": score < 80,
        "breakdown": {
            "Accommodation": int(hotel_total),
            "Food & Dining": int(food_total),
            "Local Transport": int(transport_total),
            "Activities": int(activity_total),
            "Safety Buffer (10%)": int(buffer)
        }
    }

def calculate_college_group_costs(students, staff, drivers, days, travel_type, month, activity_count, user_budget, destination="Kerala"):
    total_participants = students + staff + drivers
    multiplier = get_seasonal_multiplier(destination, month)
    
    hotel_row = HOTELS[HOTELS['city'] == destination]
    price_col = f"{travel_type.lower()}_per_night"
    base_hotel_price = hotel_row.iloc[0][price_col] if not hotel_row.empty else 3000
    staff_hotel_price = base_hotel_price * 1.25 
    
    base_hotel_price *= multiplier
    staff_hotel_price *= multiplier
    
    student_rooms = (students + 3) // 4 
    staff_rooms = (staff + 1) // 2 
    accommodation_cost = (student_rooms * base_hotel_price * days) + (staff_rooms * staff_hotel_price * days)
    
    v_type = "Bus" if total_participants > 25 else "Tempo Traveler"
    v_data = VEHICLES[VEHICLES['vehicle'] == v_type].iloc[0]
    vehicles = (total_participants + (v_data['capacity']-1)) // v_data['capacity']
    transport_cost = vehicles * v_data['base_cost_per_day'] * days
    
    per_person_food = (1200 if travel_type != "Budget" else 700) * multiplier
    food_cost = total_participants * per_person_food * days
    
    city_acts = ATTRACTIONS[ATTRACTIONS['city'] == destination]
    avg_act_fee = city_acts['avg_cost_per_person'].mean() if not city_acts.empty else 1000
    activity_cost = total_participants * avg_act_fee * activity_count * multiplier
    
    if total_participants > 20: activity_cost *= 0.85
        
    subtotal = accommodation_cost + transport_cost + food_cost + activity_cost
    buffer = subtotal * 0.10
    total_estimated = subtotal + buffer
    
    per_student_cost = total_estimated / students if students > 0 else 0
    total_staff_cost = (staff_rooms * staff_hotel_price * days) + (staff * per_person_food * days) + (staff * (avg_act_fee * activity_count))
    
    score = 100 if user_budget >= per_student_cost else int((user_budget / per_student_cost) * 100)
    color = "green" if score >= 90 else "red" if score < 60 else "orange"

    return {
        "total_estimated": int(total_estimated),
        "per_student_cost": int(per_student_cost),
        "total_staff_cost": int(total_staff_cost),
        "score": score,
        "status": "Budget OK" if score >= 90 else "Over Limit",
        "color": color,
        "total_participants": total_participants,
        "vehicles": f"{vehicles}x {v_type}",
        "optimization_applied": score < 80,
        "breakdown": {
            "Accommodation": int(accommodation_cost),
            "Transport": int(transport_cost),
            "Food": int(food_cost),
            "Activities": int(activity_cost),
            "Safety Buffer (10%)": int(buffer)
        }
    }

def generate_itinerary(destination, interests, pace, days, group_type="Solo"):
    pool = ATTRACTIONS[ATTRACTIONS['city'] == destination]
    if pool.empty: pool = ATTRACTIONS[ATTRACTIONS['state'] == destination]
    if pool.empty: return []

    if interests:
        mask = pool['tags'].apply(lambda tags: any(i in tags for i in interests))
        filtered = pool[mask]
        if not filtered.empty: pool = filtered

    pool = pool.sort_values('popularity_score', ascending=False)
    base_density = GROUP_INTELLIGENCE_SPECS.get(group_type, {}).get("density", 3)
    target_count = base_density if pace == "Fast" else max(1, base_density - 1)
    
    itinerary = []
    areas = list(pool['area'].unique())
    random.shuffle(areas)
    
    used_activities = set()
    
    # Pre-shuffle the pool slightly to avoid always picking the same top-popularity items
    pool = pool.sample(frac=1).sort_values('popularity_score', ascending=False)
    
    for d in range(1, days + 1):
        if not areas: 
            areas = list(pool['area'].unique())
            random.shuffle(areas)
            
        area = areas.pop(0)
        
        # Filter out already used activities to ensure variety
        available_in_area = pool[(pool['area'] == area) & (~pool['name'].isin(used_activities))]
        
        # If we run out of new items in this area, try other areas for this day
        if len(available_in_area) < target_count:
            unused_in_pool = pool[~pool['name'].isin(used_activities)]
            if not unused_in_pool.empty:
                available_in_area = unused_in_pool
            else:
                available_in_area = pool[pool['area'] == area]
            
        acts_samples = available_in_area.to_dict('records')
        top_candidates = acts_samples[:max(target_count*2, len(acts_samples))] # Get more candidates to route
        
        # --- GEOGRAPHIC ROUTING (TSP - NEAREST NEIGHBOR) ---
        # Pick the most popular one as starting point
        current_selection = []
        if top_candidates:
            # Start with the highest popularity one from top candidates
            first = top_candidates.pop(0)
            current_selection.append(first)
            
            while len(current_selection) < target_count and top_candidates:
                last = current_selection[-1]
                # Find nearest to 'last'
                top_candidates.sort(key=lambda x: calculate_haversine_distance(
                    last['latitude'], last['longitude'], x['latitude'], x['longitude']
                ))
                current_selection.append(top_candidates.pop(0))
        
        acts = current_selection
        
        day_acts = []
        for idx, a in enumerate(acts):
            used_activities.add(a['name'])
            day_acts.append({
                "time": TIME_SLOTS[idx] if idx < len(TIME_SLOTS) else "Evening Flex",
                "activity": a['name'],
                "cost": a['avg_cost_per_person'],
                "duration": a['avg_time_hours'],
                "lat": a['latitude'],
                "lon": a['longitude']
            })
        itinerary.append({"day": d, "area": area, "activities": day_acts})
    return itinerary

# --- BUDGET OPTIMIZATION LOGIC ---
def optimize_budget_swaps(itinerary, user_budget, per_item_limit, destination):
    pool = ATTRACTIONS[ATTRACTIONS['city'] == destination]
    if pool.empty: pool = ATTRACTIONS[ATTRACTIONS['state'] == destination]
    
    swaps = []
    new_itinerary = []
    
    for day in itinerary:
        new_acts = []
        day_swaps = 0
        for act in day['activities']:
            # If it's a meal or under limit, keep it
            if act.get('is_meal') or act.get('cost', 0) <= per_item_limit or day_swaps >= 2:
                new_acts.append(act)
                continue
            
            # Find cheaper alternatives with matching tags
            orig_tags = set(ATTRACTIONS[ATTRACTIONS['name'] == act['activity']].iloc[0]['tags']) if act['activity'] in ATTRACTIONS['name'].values else set()
            
            cheaper = pool[(pool['avg_cost_per_person'] < act['cost']) & (pool['avg_cost_per_person'] <= per_item_limit)]
            if not cheaper.empty and orig_tags:
                # Use a combined score of popularity and tag matching
                cheaper = cheaper.copy()
                cheaper['match_score'] = cheaper['tags'].apply(lambda t: len(set(t) & orig_tags))
                cheaper = cheaper.sort_values(['match_score', 'popularity_score'], ascending=False)
                
                alt = cheaper.iloc[0]
                swaps.append(f"Day {day['day']}: {act['activity']} → {alt['name']} (Saved ₹{int(act['cost']-alt['avg_cost_per_person'])})")
                new_acts.append({
                    "time": act['time'], "activity": alt['name'], "cost": alt['avg_cost_per_person'], 
                    "duration": alt['avg_time_hours'], "optimized": True, "lat": alt['latitude'], "lon": alt['longitude']
                })
                day_swaps += 1
            else:
                new_acts.append(act)
        new_itinerary.append({"day": day['day'], "area": day['area'], "activities": new_acts})
    return new_itinerary, swaps

# --- MEAL SLOT LOGIC ---
def inject_meal_slots(itinerary):
    for day in itinerary:
        area = day['area']
        # Fixed timings to avoid slot 1 and 2 overlaps
        day['activities'].insert(2, { # Insert after Slot 0 and Slot 1
            "time": "01:00 PM - 02:30 PM", "activity": f"🍱 Lunch: Local Food in {area}", "cost": 800, "duration": 1.5, "is_meal": True
        })
        day['activities'].append({
            "time": "08:00 PM - 09:30 PM", "activity": f"🍽️ Dinner: {area} Cuisine Night", "cost": 1200, "duration": 1.5, "is_meal": True
        })
    return itinerary

# --- MULTI-CITY LOGIC ---
def generate_multi_city_itinerary(dest_list, days, interests, pace, group_type):
    itinerary = []
    days_per_city = days // len(dest_list)
    remaining = days % len(dest_list)
    
    # Generic Inter-city speeds: 60 km/h
    current_day = 1
    
    for i, city in enumerate(dest_list):
        d_count = days_per_city + (1 if i < remaining else 0)
        
        # Calculate transition if not first city
        if i > 0:
            prev_city = dest_list[i-1]
            # Try to get coordinates for transit estimation (simulated check)
            # For now we use the first attraction of each city as proxy
            prev_pool = ATTRACTIONS[ATTRACTIONS['city'] == prev_city]
            curr_pool = ATTRACTIONS[ATTRACTIONS['city'] == city]
            
            if not prev_pool.empty and not curr_pool.empty:
                dist = calculate_haversine_distance(
                    prev_pool.iloc[0]['latitude'], prev_pool.iloc[0]['longitude'],
                    curr_pool.iloc[0]['latitude'], curr_pool.iloc[0]['longitude']
                )
                travel_h = round(dist / 60, 1)
                transit_note = f"✈️ Transit: {prev_city} → {city} ({int(dist)}km, ~{travel_h}h)"
            else:
                transit_note = f"🚗 Transit: {prev_city} → {city}"
            
            # Inject transit into the first day of the new city
            city_itin = generate_itinerary(city, interests, pace, d_count, group_type)
            if city_itin:
                city_itin[0]['transit_info'] = transit_note
        else:
            city_itin = generate_itinerary(city, interests, pace, d_count, group_type)

        for d in city_itin:
            d['day'] = current_day
            current_day += 1
        itinerary.extend(city_itin)
        
    return itinerary

def estimate_risk_factors(destination, month):
    risks = []
    if destination in ["Kerala", "Goa"] and month in ["June", "July", "August"]:
        risks.append({"type": "Weather", "level": "High", "desc": "Monsoon Peak: Heavy rain hazards."})
    if destination == "Dubai" and month in ["June", "July", "August"]:
        risks.append({"type": "Climate", "level": "High", "desc": "Extreme Heat (>45°C). Use caution."})
    if not risks: risks.append({"type": "General", "level": "Low", "desc": "Stability confirmed."})
    return risks

def calculate_risk_score(risks):
    high = len([r for r in risks if r['level'] == 'High'])
    return max(0, 100 - (high * 35))

def calculate_experience_score(itinerary, user_interests, destination, group_type="Solo"):
    if not user_interests: return 100, "Neutral Match", "blue"
    boost = GROUP_INTELLIGENCE_SPECS.get(group_type, {}).get("pref_boost", {})
    seen_tags = set()
    for d in itinerary:
        for a in d['activities']:
            row = ATTRACTIONS[ATTRACTIONS['name'] == a['activity']]
            if not row.empty: seen_tags.update(row.iloc[0]['tags'])
    matches = 0
    for i in user_interests:
        if i in seen_tags: matches += (1.0 * boost.get(i, 1.0))
    score = min(100, int((matches / len(user_interests)) * 100))
    return score, "High Presence" if score > 80 else "Fair Match", "green" if score > 80 else "blue"

def calculate_time_efficiency(itinerary, group_type="Solo"):
    if not itinerary: return 100, "Optimal", "green", 0.0
    mult = GROUP_INTELLIGENCE_SPECS.get(group_type, {}).get("time_mult", 1.0)
    daily_commute = []
    for d in itinerary:
        acts = [a for a in d['activities'] if not a.get('is_meal')]
        if not acts: 
            daily_commute.append(120 * mult)
            continue
        # GEOGRAPHIC ROUTING LOGIC: Haversine distance between acts
        total_trip_mins = 90 # Start/End factor
        for i in range(len(acts)-1):
            total_trip_mins += haversine_travel_time(acts[i]['lat'], acts[i]['lon'], acts[i+1]['lat'], acts[i+1]['lon'])
        daily_commute.append(total_trip_mins * mult)
    avg_h = (sum(daily_commute) / len(daily_commute)) / 60
    score = max(20, 100 - (avg_h * 15))
    return int(score), "Highly Efficient" if avg_h < 3 else "Moderate", "green" if avg_h < 3 else "blue", round(avg_h, 1)

def calculate_overall_score(b_s, e_s, t_s, r_s):
    return int((b_s * 0.3) + (e_s * 0.3) + (t_s * 0.2) + (r_s * 0.2))

def calculate_risk_indicators(budget, budget_data, month, itinerary, avg_h, group_type, pace, students, staff):
    indicators = []
    total = budget_data.get('total_estimated', 0)
    per_student = budget_data.get('per_student_cost', 0)
    if group_type == "College Group":
        if per_student > budget: indicators.append({"icon": "💸", "title": "Budget Breach", "desc": f"Exceeds student limit by ₹{int(per_student-budget):,}."})
    elif total > budget: indicators.append({"icon": "💸", "title": "Budget Breach", "desc": f"Exceeds limit by ₹{int(total-budget):,}."})
    multiplier = get_seasonal_multiplier(itinerary[0]['area'] if itinerary and 'area' in itinerary[0] else "Kerala", month)
    if multiplier > 1.2: indicators.append({"icon": "🏔️", "title": "Peak Season", "desc": "High demand inflation detected."})
    if group_type == "College Group" and students > 0 and (staff/students) < (1/15):
        indicators.append({"icon": "👮", "title": "Safety Warning", "desc": "Staff ratio below 1:15 safety limit."})
    if avg_h > 4.5: indicators.append({"icon": "⌛", "title": "Transit Fatigue", "desc": "Heavy travel overhead according to geo-routing."})
    return indicators
