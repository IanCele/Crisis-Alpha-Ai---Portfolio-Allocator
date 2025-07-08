import streamlit as st
from src.allocator import CrisisAllocator
from src.news_scraper import CrisisMonitor
import yfinance as yf
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize services
allocator = CrisisAllocator(os.getenv("OPENAI_API_KEY"))
monitor = CrisisMonitor(os.getenv("NEWS_API_KEY"))

# App config
st.set_page_config(
    page_title="🧭 Crisis Alpha AI", 
    page_icon="📊",
    layout="wide"
)

# Sidebar - User Inputs
with st.sidebar:
    st.header("🌍 Crisis Parameters")
    crisis_type = st.selectbox("Crisis Focus", ["Geopolitical", "Inflation", "Election", "Market Crash", "Custom"])
    
    col1, col2 = st.columns(2)
    with col1:
        geo_risk = st.slider("Geopolitical Risk", 0.0, 10.0, 7.5)
    with col2:
        inflation = st.slider("Inflation (%)", 0.0, 20.0, 6.5)
    
    election_risk = st.slider("Election Uncertainty", 0.0, 10.0, 4.0)
    custom_factors = st.text_area("Additional Factors", "Iran-Israel tensions, Fed rate uncertainty")
    
    if st.button("🚀 Generate Crisis Allocation", type="primary", use_container_width=True):
        with st.spinner("Analyzing global risks..."):
            # Get news-based insights
            news_insights = monitor.get_crisis_insights(custom_factors)
            crisis_score = monitor.calculate_crisis_score(news_insights)
            
            # Generate allocation
            market_data = allocator.get_market_snapshot()
            st.session_state.allocation = allocator.generate_allocation(
                f"{crisis_type} crisis | Score: {crisis_score}/10 | Factors: {custom_factors}",
                market_data
            )
            st.session_state.news = news_insights

# Main Dashboard
st.title("🧭 Crisis Alpha AI Portfolio Allocator")
st.caption("AI-powered asset allocation for turbulent markets")

if "allocation" in st.session_state:
    alloc = st.session_state.allocation
    
    # Portfolio Allocation
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Recommended Allocation")
        st.metric("Defense Stocks", f"{alloc['defense']:.1f}%")
        st.metric("Gold", f"{alloc['gold']:.1f}%")
        st.metric("ESG Assets", f"{alloc['esg']:.1f}%")
        st.metric("Cryptocurrency", f"{alloc['crypto']:.1f}%")
        st.metric("Cash", f"{alloc['cash']:.1f}%")
        
        st.divider()
        st.write("**Investment Thesis**")
        st.info(alloc['thesis'])
        
        st.download_button(
            label="📥 Download Allocation Report",
            data=f"Crisis Allocation Report\n\n{st.session_state.allocation}",
            file_name="crisis_alpha_allocation.txt"
        )
    
    with col2:
        # Visualization
        st.subheader("Portfolio Composition")
        allocation_data = {
            "Asset": ["Defense", "Gold", "ESG", "Crypto", "Cash"],
            "Allocation": [alloc['defense'], alloc['gold'], alloc['esg'], alloc['crypto'], alloc['cash']]
        }
        st.bar_chart(allocation_data, x="Asset", y="Allocation")
        
        # News Insights
        st.subheader("Top Crisis News")
        for insight in st.session_state.news[:3]:
            sentiment_color = "#ef4444" if insight['sentiment'] == "NEGATIVE" else "#22c55e"
            st.markdown(
                f"**{insight['title']}**  \n"
                f"*{insight['source']}* · "
                f"<span style='color:{sentiment_color}'>Sentiment: {insight['sentiment']} ({insight['score']:.2f})</span>",
                unsafe_allow_html=True
            )
            st.caption(f"[Read more]({insight['url']})")
            st.divider()
else:
    st.info("Configure crisis parameters and generate allocation")
    st.image("assets/crisis_framework.png", caption="Crisis Response Framework")
    
    # Real-time Market Snapshot
    st.subheader("Live Market Indicators")
    tickers = st.multiselect(
        "Track Assets", 
        ["SPY", "GLD", "BTC-USD", "LMT", "^VIX"], 
        default=["SPY", "^VIX"]
    )
    if tickers:
        data = yf.download(tickers, period="1d")
        st.line_chart(data["Close"])
