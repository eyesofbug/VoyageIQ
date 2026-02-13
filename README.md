# VoyageIQ - Dataset Cleaning & Conversion Engine 🇮🇳

VoyageIQ is a powerful travel planning engine designed to analyze destinations, seasonality, and logistics to generate optimized Indian travel itineraries.

## 🚀 Features
- **Real-World Indian Data**: Over 200 curated landmarks across 48+ cities (Kerala, Goa, Rajasthan, etc.).
- **Smart Itinerary Generation**: Day-wise planning with variety logic (no repeated activities).
- **Seasonality Engine**: Dynamic pricing multipliers (0.8x - 1.5x) based on official Indian tourism trends.
- **Transport Optimizer**: Automated vehicle recommendations for Bus (45), Tempo Traveller (12), and Van (8).
- **Clean UI**: Built with Streamlit for a fast, responsive dashboard.

## 🛠️ Architecture
- `app.py`: Streamlit frontend for user interaction.
- `utils/analysis.py`: Core logic for itinerary and cost calculation.
- `utils/cleaning_engine.py`: ETL pipeline for processing raw tourism data.
- `data/`: JSON and CSV datasets.

## ⚙️ Local Setup
1. Clone the repository.
2. Install dependencies: `pip install pandas streamlit numpy`.
3. Run the app: `streamlit run app.py`.

---
Developed as part of the VoyageIQ Travel Suite.
