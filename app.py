import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_folium import st_folium
import folium

# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="TaxiFare NYC", page_icon="🚕", layout="centered")

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0d0d;
    color: #f0ede6;
}
h1, h2, h3 { font-family: 'Bebas Neue', sans-serif; letter-spacing: 0.05em; }
.title-block { text-align: center; padding: 2.5rem 0 1rem 0; border-bottom: 1px solid #2a2a2a; margin-bottom: 2rem; }
.title-block h1 { font-size: 4rem; color: #f7c948; margin: 0; line-height: 1; }
.title-block p { color: #888; font-size: 0.95rem; margin-top: 0.4rem; font-weight: 300; }
.section-label { font-family: 'Bebas Neue', sans-serif; font-size: 0.75rem; letter-spacing: 0.15em; color: #f7c948; text-transform: uppercase; margin-bottom: 0.5rem; margin-top: 1.8rem; }
div[data-testid="stButton"] > button { background-color: #f7c948; color: #0d0d0d; font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem; letter-spacing: 0.1em; border: none; border-radius: 6px; padding: 0.6rem 2.5rem; width: 100%; margin-top: 1.5rem; }
div[data-testid="stButton"] > button:hover { background-color: #ffd966; }
.fare-card { background: linear-gradient(135deg, #1a1a1a, #222); border: 1px solid #f7c948; border-radius: 12px; padding: 2rem; text-align: center; margin-top: 1.5rem; }
.fare-card .label { font-size: 0.75rem; letter-spacing: 0.2em; color: #888; text-transform: uppercase; font-family: 'Bebas Neue', sans-serif; }
.fare-card .amount { font-family: 'Bebas Neue', sans-serif; font-size: 4rem; color: #f7c948; line-height: 1.1; }
</style>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────
st.markdown("""
<div class="title-block">
    <h1>🚕 TAXIFARE NYC</h1>
    <p>Click on the map to set pickup and dropoff locations</p>
</div>
""", unsafe_allow_html=True)

# ── Date & Time ───────────────────────────────────────────────
st.markdown('<div class="section-label">📅 Date & Time</div>', unsafe_allow_html=True)
col_d, col_t = st.columns(2)
with col_d:
    pickup_date = st.date_input("Date", value=datetime.today(), label_visibility="collapsed")
with col_t:
    pickup_time = st.time_input("Time", value=datetime.now().time(), label_visibility="collapsed")
pickup_datetime = f"{pickup_date} {pickup_time}"

# ── Map: click to set pickup & dropoff ────────────────────────
st.markdown('<div class="section-label">🗺 Click: 1st click = Pickup, 2nd click = Dropoff</div>', unsafe_allow_html=True)

# Session state to store clicks
if "pickup" not in st.session_state:
    st.session_state.pickup = None
if "dropoff" not in st.session_state:
    st.session_state.dropoff = None
if "click_count" not in st.session_state:
    st.session_state.click_count = 0

# Build map centered on NYC
m = folium.Map(location=[40.7580, -73.9855], zoom_start=12, tiles="CartoDB dark_matter")

# Show existing markers
if st.session_state.pickup:
    folium.Marker(
        st.session_state.pickup,
        tooltip="Pickup 🟢",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

if st.session_state.dropoff:
    folium.Marker(
        st.session_state.dropoff,
        tooltip="Dropoff 🔴",
        icon=folium.Icon(color="red", icon="stop")
    ).add_to(m)

# Draw line between points
if st.session_state.pickup and st.session_state.dropoff:
    folium.PolyLine(
        [st.session_state.pickup, st.session_state.dropoff],
        color="#f7c948",
        weight=3,
        dash_array="6"
    ).add_to(m)

map_output = st_folium(m, width=700, height=420)

# Handle click
if map_output and map_output.get("last_clicked"):
    lat = map_output["last_clicked"]["lat"]
    lon = map_output["last_clicked"]["lng"]
    clicked = [lat, lon]

    if st.session_state.click_count % 2 == 0:
        st.session_state.pickup = clicked
    else:
        st.session_state.dropoff = clicked

    st.session_state.click_count += 1
    st.rerun()

# Reset button
if st.button("🔄 Reset locations"):
    st.session_state.pickup = None
    st.session_state.dropoff = None
    st.session_state.click_count = 0
    st.rerun()

# Show coordinates
if st.session_state.pickup:
    st.caption(f"✅ Pickup: {st.session_state.pickup[0]:.5f}, {st.session_state.pickup[1]:.5f}")
if st.session_state.dropoff:
    st.caption(f"✅ Dropoff: {st.session_state.dropoff[0]:.5f}, {st.session_state.dropoff[1]:.5f}")

# ── Passengers ────────────────────────────────────────────────
st.markdown('<div class="section-label">👥 Passengers</div>', unsafe_allow_html=True)
passenger_count = st.slider("", min_value=1, max_value=8, value=1)

# ── API Call ──────────────────────────────────────────────────
url = 'https://taxifare.lewagon.ai/predict'

if st.button("PREDICT FARE 🚀"):
    if not st.session_state.pickup or not st.session_state.dropoff:
        st.warning("Please click on the map to set pickup and dropoff first!")
    else:
        params = {
            "pickup_datetime": pickup_datetime,
            "pickup_longitude": st.session_state.pickup[1],
            "pickup_latitude": st.session_state.pickup[0],
            "dropoff_longitude": st.session_state.dropoff[1],
            "dropoff_latitude": st.session_state.dropoff[0],
            "passenger_count": passenger_count
        }
        with st.spinner("Calculating..."):
            response = requests.get(url, params=params)
            prediction = response.json()["fare"]

        st.markdown(f"""
        <div class="fare-card">
            <div class="label">Estimated Fare</div>
            <div class="amount">${prediction:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
