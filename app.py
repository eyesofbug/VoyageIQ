import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from utils.analysis import (
    calculate_detailed_budget, 
    estimate_risk_factors, 
    generate_itinerary, 
    calculate_experience_score, 
    calculate_time_efficiency,
    calculate_risk_score,
    calculate_overall_score,
    calculate_risk_indicators,
    calculate_college_group_costs,
    optimize_budget_swaps,
    inject_meal_slots,
    generate_multi_city_itinerary,
    ATTRACTIONS
)

# Page configuration
st.set_page_config(page_title="VoyageIQ – AI Travel Analyzer", page_icon="✈️", layout="wide")

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Get available cities from dataset
available_cities = sorted(ATTRACTIONS['city'].unique().tolist())
default_city = "Munnar" if "Munnar" in available_cities else available_cities[0]

# Sidebar UI
with st.sidebar:
    st.title("Settings")
    st.markdown("---")
    
    is_multi_city = st.toggle("Multi-City Strategy", value=False)
    if is_multi_city:
        dest_a = st.selectbox("Destination A", available_cities, index=available_cities.index(default_city))
        dest_b = st.selectbox("Destination B", available_cities, index=(available_cities.index(default_city) + 1) % len(available_cities))
        destinations = [dest_a, dest_b]
        primary_dest = dest_a
    else:
        primary_dest = st.selectbox("Destination", available_cities, index=available_cities.index(default_city))
        destinations = [primary_dest]

    days = st.slider("Number of Days", 1, 14 if is_multi_city else 7, 3)
    budget = st.number_input("Your Budget (₹)", min_value=1000, value=50000, step=5000)
    group_type = st.selectbox("Group Type", ["Solo", "Couple", "Friends", "Family", "College Group"])
    
    students, staff, drivers = 0, 0, 0
    if group_type == "College Group":
        st.markdown("##### 📦 Group Logistics")
        students = st.number_input("Number of Students", min_value=1, value=30)
        staff = st.number_input("Number of Staff", min_value=1, value=2)
        drivers = st.number_input("Number of Drivers", min_value=0, value=1)
        st.markdown("---")

    travel_type = st.radio("Travel Type", ["Budget", "Standard", "Luxury"])
    interests = st.multiselect("Interests", ["Adventure", "Culture", "Relaxation", "Shopping", "Religious", "Scenic"], default=["Scenic", "Relaxation"])
    pace = st.select_slider("Travel Pace", options=["Relaxed", "Moderate", "Fast"], value="Moderate")
    month = st.selectbox("Travel Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    
    btn_calculate = st.button("Generate Strategy", use_container_width=True)

# Main Content
st.markdown(f"""
    <div style='display: flex; align-items: center; gap: 1rem;'>
        <h1 style='margin:0;'>🌍 VoyageIQ Dashboard</h1>
        <span style='background: #00D2FF; color: #0F172A; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.8rem; font-weight: 700;'>MEGA-LOGIC v2.0</span>
    </div>
    <p style='color: #94A3B8; margin-top: 0.5rem;'><b>AI Strategy for {' & '.join(destinations)} | {group_type} Mode</b></p>
""", unsafe_allow_html=True)

if btn_calculate:
    try:
        # 1. Processing Itinerary
        if is_multi_city:
            itinerary = generate_multi_city_itinerary(destinations, days, interests, pace, group_type)
        else:
            itinerary = generate_itinerary(primary_dest, interests, pace, days, group_type)
        
        # Inject Meals
        itinerary = inject_meal_slots(itinerary)
        
        total_activities = sum(len([a for a in d['activities'] if not a.get('is_meal')]) for d in itinerary)
        
        # 2. Financials
        if group_type == "College Group":
            budget_data = calculate_college_group_costs(students, staff, drivers, days, travel_type, month, total_activities, budget, primary_dest)
        else:
            budget_data = calculate_detailed_budget(budget, travel_type, days, month, total_activities, group_type, primary_dest)
            
        # Budget Optimization Swapper
        swaps = []
        if budget_data.get('score', 100) < 80:
            itinerary, swaps = optimize_budget_swaps(itinerary, budget, 2000 if travel_type == "Budget" else 4000, primary_dest)
            # Recalculate roughly (status check)
            if swaps: budget_data['status'] = "Optimized Match"

        risks = estimate_risk_factors(primary_dest, month)
        exp_score, exp_status, exp_color = calculate_experience_score(itinerary, interests, primary_dest, group_type)
        time_score, time_status, time_color, avg_h = calculate_time_efficiency(itinerary, group_type)
        risk_score = calculate_risk_score(risks)
        overall_val = calculate_overall_score(budget_data['score'], exp_score, time_score, risk_score)
        
        indicators = calculate_risk_indicators(budget, budget_data, month, itinerary, avg_h, group_type, pace, students, staff)

        # 3. Score Dashboard
        st.markdown("<div class='overall-container'>", unsafe_allow_html=True)
        col_l, col_r = st.columns([1.5, 1])
        
        with col_l:
            st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h2 style='margin:0; color:#00D2FF;'>🧠 Intelligence Score</h2>
                    <div style='font-size: 3rem; font-weight: 800; color: #00D2FF;'>{overall_val}%</div>
                </div>
                <div class="progress-container"><div class="progress-bar-fill" style="width: {overall_val}%;"></div></div>
                <div style='margin-top: 1.5rem; display: flex; gap: 0.8rem; flex-wrap: wrap;'>
                    <div class="score-pill">💰 Budget: {budget_data['score']}%</div>
                    <div class="score-pill">🎭 Exp: {exp_score}%</div>
                    <div class="score-pill">⌛ Geo-Efficiency: {time_score}%</div>
                    <div class="score-pill">🛡️ Stability: {risk_score}%</div>
                </div>
            """, unsafe_allow_html=True)
            if swaps:
                st.info(f"💡 **Budget Optimization Applied**: {len(swaps)} swaps suggest to fit your budget. See console for details.")
            
        with col_r:
            fig = go.Figure(data=go.Scatterpolar(r=[budget_data['score'], exp_score, time_score, risk_score], theta=['Budget', 'Experience', 'Geo-Routing', 'Stability'], fill='toself', line_color='#00D2FF'))
            fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=True, range=[0, 100], color='#475569')), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=30, l=30, r=30), height=250)
            st.plotly_chart(fig, use_container_width=True)
            
        tags = "".join([f'<div class="risk-tag">{i["icon"]} <b>{i["title"]}</b>: {i["desc"]}</div>' for i in indicators])
        st.markdown(f'<div style="display: flex; gap: 0.8rem; flex-wrap: wrap; margin-top: 1rem;">{tags}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 4. Metrics & Tabs
        st.markdown("<br>", unsafe_allow_html=True)
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
        with m_col1: st.markdown(f"<div class='metric-card'><div class='metric-title'>Trip Total</div><div class='metric-value'>₹{int(budget_data['total_estimated']):,}</div></div>", unsafe_allow_html=True)
        with m_col2: st.markdown(f"<div class='metric-card'><div class='metric-title'>Status</div><div class='metric-value' style='color:{budget_data['color']};'>{budget_data['status']}</div></div>", unsafe_allow_html=True)
        with m_col3: st.markdown(f"<div class='metric-card'><div class='metric-title'>Efficiency</div><div class='metric-value'>{time_score}%</div><div style='font-size:0.8rem;'>{avg_h}h/Day Geo-Transit</div></div>", unsafe_allow_html=True)
        with m_col4: st.markdown(f"<div class='metric-card'><div class='metric-title'>Activities</div><div class='metric-value'>{total_activities}</div></div>", unsafe_allow_html=True)
        with m_col5: st.markdown(f"<div class='metric-card'><div class='metric-title'>Stability</div><div class='metric-value'>{risk_score}</div></div>", unsafe_allow_html=True)

        t1, t2, t3, t4 = st.tabs(["🗺️ Multi-City Itinerary", "💰 Optimization Console", "🛰️ Geo-Routing Data", "⚠️ Risks"])
        
        with t1:
            for day in itinerary:
                title = f"Day {day['day']}: {day['area']} Exploration"
                with st.expander(title, expanded=True):
                    if 'transit_info' in day:
                        st.markdown(f"***{day['transit_info']}***")
                    for slot in day['activities']:
                        icon = "🍱" if slot.get('is_meal') else "📍"
                        opt_badge = "✅ (Budget Optimized)" if slot.get('optimized') else ""
                        st.markdown(f"**{slot['time']}** | {icon} {slot['activity']} {opt_badge}")

        with t2:
            st.subheader("Budget Optimization Swaps")
            if swaps:
                for s in swaps: st.success(s)
            else:
                st.info("No swaps required. Your budget comfortably fits the primary attractions.")
            st.table(pd.DataFrame(list(budget_data["breakdown"].items()), columns=["Category", "Amount (₹)"]))

        with t3:
            st.subheader("Geographic Intelligence")
            st.write("Transit times calculated using Haversine Sphere Distance between actual Lat/Long coordinates.")
            for day in itinerary:
                st.write(f"**Day {day['day']} Cluster**: {day['area']}")

        with t4:
            for r in risks: st.warning(f"**{r['type']}**: {r['desc']}")
                
    except Exception as e:
        st.error(f"Logic Error: {str(e)}")
        st.exception(e)
else:
    st.info("👈 Activate 'Multi-City Strategy' or configure parameters to launch.")
