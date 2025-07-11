import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os
import openai
import matplotlib.pyplot as plt
import plotly.express as px

# Configuration
st.set_page_config(
    page_title="🧭 Crisis Alpha AI Portfolio Allocator",
    page_icon="📊",
    layout="wide"
)

# API Setup
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# Asset Configuration
ASSET_CATEGORIES = {
    "Defense Stocks": ["LMT", "RTX", "NOC"],
    "Gold": ["GLD"],
    "ESG Assets": ["ICLN", "ESGU"],
    "Cryptocurrency": ["BTC-USD", "ETH-USD"]
}

# Helper Functions
def get_market_data():
    """Get real-time market data for all assets"""
    all_tickers = [t for sublist in ASSET_CATEGORIES.values() for t in sublist]
    data = yf.download(all_tickers, period="1d", progress=False)
    return data['Close'].iloc[-1] if not data.empty else None

def get_news_headlines(query="war inflation election market volatility"):
    """Get relevant news headlines (simplified version)"""
    try:
        url = f"https://news.google.com/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')[:5]
        return [article.find('a', {'class': 'JtKRv'}).text for article in articles if article.find('a', {'class': 'JtKRv'})]
    except:
        return ["Market stable amid global tensions", "Fed considers rate cuts", "Election uncertainty affects markets"]

def generate_allocation_with_ai(crisis_description, selected_assets, market_data):
    """Generate portfolio allocation using GPT-4"""
    if not openai.api_key:
        st.error("OpenAI API key not configured!")
        return None
        
    asset_list = ", ".join(selected_assets)
    market_info = f"Current market snapshot: {market_data.to_dict()}" if market_data is not None else ""
    
    prompt = f"""
    You are Crisis Alpha AI, an expert portfolio allocator during global crises. 
    Based on the current crisis situation: "{crisis_description}",
    and current market conditions: {market_info},
    recommend an allocation percentage for these asset classes: {asset_list}.
    
    Provide output ONLY in this format:
    Defense Stocks: X%
    Gold: Y%
    ESG Assets: Z%
    Cryptocurrency: W%
    Cash: V%
    
    Investment thesis: [2-3 sentence explanation]
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3,
            max_tokens=256
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"AI error: {str(e)}")
        return None

# Main App
st.title("🧭 Crisis Alpha AI Portfolio Allocator")
st.write("""
**Dynamically allocate assets based on real-time crisis inputs**
- Defense Stocks: Lockheed Martin (LMT), Raytheon (RTX), Northrop Grumman (NOC)
- Gold: GLD ETF
- ESG Assets: iShares Global Clean Energy ETF (ICLN), iShares ESG Aware ETF (ESGU)
- Cryptocurrency: Bitcoin (BTC-USD), Ethereum (ETH-USD)
""")

# Sidebar - User Inputs
with st.sidebar:
    st.header("🌍 Crisis Parameters")
    crisis_description = st.text_area("Describe current crisis factors:", 
                                     "Iran-Israel tensions, US election uncertainty, high inflation")
    
    st.subheader("Select Asset Classes")
    selected_assets = []
    for category in ASSET_CATEGORIES.keys():
        if st.checkbox(category, value=True):
            selected_assets.append(category)
    
    if st.button("🚀 Generate Allocation", type="primary", use_container_width=True):
        st.session_state.market_data = get_market_data()
        st.session_state.news_headlines = get_news_headlines()
        st.session_state.allocation = generate_allocation_with_ai(
            crisis_description,
            selected_assets,
            st.session_state.market_data
        )

# Main Content
if 'allocation' in st.session_state and st.session_state.allocation:
    st.success("AI Portfolio Allocation Generated!")
    st.subheader("Recommended Allocation")
    st.code(st.session_state.allocation, language="text")
    
    # Simple Visualization
    allocation_data = {}
    for line in st.session_state.allocation.split('\n'):
        if '%' in line:
            parts = line.split(':')
            if len(parts) == 2:
                asset = parts[0].strip()
                percentage = parts[1].replace('%', '').strip()
                if percentage.replace('.', '', 1).isdigit():
                    allocation_data[asset] = float(percentage)
    
    if allocation_data:
        st.subheader("Allocation Breakdown")
        fig = px.pie(
            names=list(allocation_data.keys()),
            values=list(allocation_data.values()),
            title="Portfolio Allocation"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Couldn't parse allocation percentages")
    
    # Market Data
    if 'market_data' in st.session_state and st.session_state.market_data is not None:
        st.subheader("Current Market Prices")
        st.write(st.session_state.market_data)
    
    # News
    if 'news_headlines' in st.session_state:
        st.subheader("Relevant News Headlines")
        for headline in st.session_state.news_headlines:
            st.write(f"- {headline}")
else:
    st.info("Configure crisis parameters and generate allocation")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Crisis Response Framework")
        st.image("https://i.imgur.com/3JmBWlC.png", caption="Dynamic Asset Allocation Strategy")
    with col2:
        st.subheader("How It Works")
        st.write("""
        1. Describe current crisis factors
        2. Select asset classes to include
        3. AI analyzes market conditions
        4. Get recommended allocation
        """)

# Disclaimer
st.divider()
st.caption("""
**Disclaimer**: This tool provides AI-generated suggestions only. Not financial advice. 
Past performance ≠ future results. Always do your own research.
""")
