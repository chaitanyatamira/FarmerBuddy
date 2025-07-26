import streamlit as st
import requests
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add services to path
sys.path.append('services')

from services.ai_assistant import FarmerAssistant
from services.weather import WeatherService

# Load environment variables
load_dotenv()

# Initialize services
@st.cache_resource
def init_services():
    return FarmerAssistant(), WeatherService()

farmer_ai, weather_service = init_services()

# Page config
st.set_page_config(
    page_title="FarmerBuddy - कृषि सहायक",
    page_icon="🌾",
    layout="wide"
)

# Title with multilingual support
st.title("🌾 FarmerBuddy - तुम्हारा कृषि सहायक")
st.markdown("*Your Voice-Powered Agriculture Assistant*")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    language = st.selectbox("भाषा चुनें / Choose Language", ["English", "Hindi", "Telugu"])
    location = st.text_input("Your Location", value="Hyderabad")
    
    # Get real weather data
    if st.button("🔄 Refresh Weather"):
        st.rerun()
    
    weather_data = weather_service.get_current_weather(location)
    
    st.markdown("---")
    st.markdown("### 📊 Live Weather Stats")
    st.metric("Temperature", f"{weather_data['temperature']}°C", 
              f"{weather_data['temperature'] - 30}°C")
    st.metric("Humidity", f"{weather_data['humidity']}%", 
              f"{weather_data['humidity'] - 70}%")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Ask FarmerBuddy")
    
    # Text input for now (we'll add voice later)
    user_question = st.text_area(
        "What would you like to know about farming?",
        placeholder="Example: Which crops should I plant this season in Telanganga?",
        height=100
    )
    
    if st.button("🚀 Get Answer", type="primary"):
        if user_question:
            with st.spinner("FarmerBuddy is thinking..."):
                # Get AI response using our smart assistant
                ai_response = farmer_ai.get_response(
                    user_question, 
                    weather_data=weather_data,
                    location=location
                )
                
                st.success("**FarmerBuddy's Response:**")
                st.write(ai_response)
                
                # Show relevant quick actions based on query
                if farmer_ai.analyze_weather_query(user_question):
                    st.info("💡 **Related:** Check today's weather in the sidebar!")
                elif farmer_ai.analyze_market_query(user_question):
                    st.info("💡 **Related:** Current market prices shown below!")
        else:
            st.warning("Please ask a question first!")

with col2:
    st.header("🌤️ Live Weather")
    
    # Real weather data
    st.info(f"📍 {weather_data['city']}, {weather_data['country']}")
    st.write(f"🌡️ **Temperature:** {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)")
    st.write(f"💧 **Humidity:** {weather_data['humidity']}%")
    st.write(f"🌤️ **Condition:** {weather_data['description']}")
    st.write(f"💨 **Wind:** {weather_data['wind_speed']} km/h")
    
    # Farming advice based on weather
    farming_advice = weather_service.get_farming_advice(weather_data)
    st.markdown("**🌾 Weather-Based Farming Tips:**")
    for advice in farming_advice:
        st.write(f"• {advice}")
    
    st.markdown("---")
    
    st.header("💰 Market Prices")
    st.write("🌾 **Rice:** ₹2,500/quintal")
    st.write("🌿 **Cotton:** ₹6,200/quintal") 
    st.write("🌰 **Groundnut:** ₹5,800/quintal")
    st.caption("*Prices updated daily*")

# Quick action buttons
st.markdown("### 🚀 Quick Actions")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🌾 Crop Recommendations"):
        with st.spinner("Getting recommendations..."):
            recommendations = farmer_ai.get_crop_recommendations(location=location)
            st.success("**Best Crops for This Season:**")
            st.write(recommendations)

with col2:
    if st.button("🌤️ Farming Weather Tips"):
        with st.spinner("Analyzing weather..."):
            weather_query = f"Give me farming advice based on current weather in {location}"
            weather_tips = farmer_ai.get_response(weather_query, weather_data, location)
            st.info("**Weather-Based Farming Tips:**")
            st.write(weather_tips)

with col3:
    if st.button("💰 Market Analysis"):
        with st.spinner("Analyzing market..."):
            market_query = "What are the current market trends and which crops have better prices?"
            market_analysis = farmer_ai.get_response(market_query, weather_data, location)
            st.warning("**Market Analysis:**")
            st.write(market_analysis)

with col4:
    if st.button("🆘 Farming Help"):
        st.info("**Common Questions:**")
        st.write("• Which crop to plant this season?")
        st.write("• How to protect crops from pests?")
        st.write("• Best irrigation practices?")
        st.write("• Government schemes for farmers?")

st.markdown("---")
st.markdown("### 🌱 Crop Recommendations for This Season")

# Sample crop cards
col1, col2, col3 = st.columns(3)

with col1:
    st.success("**🌾 Rice**")
    st.write("✅ Best for Kharif season")
    st.write("💧 High water requirement")
    st.write("📅 Plant: June-July")

with col2:
    st.info("**🌿 Cotton**") 
    st.write("✅ Good market demand")
    st.write("☀️ Needs warm weather")
    st.write("📅 Plant: May-June")

with col3:
    st.warning("**🌰 Groundnut**")
    st.write("✅ Drought resistant")
    st.write("💰 Stable prices")
    st.write("📅 Plant: June-July")

# Development note
st.markdown("---")
st.markdown("*🚧 Development Status: Basic UI Complete! Next: Connecting APIs...*")