import streamlit as st
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="Trading Dashboard Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'analysts' not in st.session_state:
    st.session_state.analysts = []
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'daily_pnl' not in st.session_state:
    st.session_state.daily_pnl = 0

# ===== SIDEBAR =====
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Discord Token
    st.subheader("Discord Configuration")
    discord_token = st.text_input("Discord Token", type="password", help="Get from Discord Developer Portal")
    
    if st.button("🔗 Connect Discord"):
        st.success("Discord connected! (Demo)")

# ===== MAIN CONTENT =====
st.title("📊 Trading Dashboard Pro v2.0")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Dashboard",
    "👥 Analysts", 
    "🛡️ Risk Controls",
    "📊 Analytics",
    "❌ Rejections"
])

# ===== TAB 1: DASHBOARD =====
with tab1:
    st.header("Dashboard Overview")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Daily P&L",
            value="$0",
            delta="Today",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="Win Rate",
            value="0%",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Active Analysts",
            value=len([a for a in st.session_state.analysts if a.get('enabled')]),
            delta=f"of {len(st.session_state.analysts)}"
        )
    
    with col4:
        st.metric(
            label="Account Equity",
            value="$50,000",
            delta="Current"
        )
    
    st.divider()
    
    # Top Performers
    st.subheader("📊 Top Performers")
    if st.session_state.analysts:
        df = pd.DataFrame(st.session_state.analysts)
        st.dataframe(df[['name', 'enabled', 'source']], use_container_width=True)
    else:
        st.info("No analysts added yet. Go to the Analysts tab to add one!")

# ===== TAB 2: ANALYSTS =====
with tab2:
    st.header("Manage Analysts")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.subheader("Add New Analyst")
    with col2:
        if st.button("➕ Add", use_container_width=True):
            st.session_state.show_add_analyst = True
    
    # Add analyst form
    if st.session_state.get('show_add_analyst'):
        with st.form("add_analyst_form"):
            analyst_name = st.text_input("Analyst Name *", placeholder="e.g., Alice_Pro")
            analyst_source = st.selectbox("Source *", ["Discord Channel", "Discord User", "Manual"])
            analyst_discord_id = st.text_input("Discord ID (if applicable)", placeholder="Paste Discord ID here")
            analyst_notes = st.text_area("Notes (optional)", placeholder="e.g., Consistent scalper")
            
            if st.form_submit_button("✅ Add Analyst"):
                if analyst_name:
                    new_analyst = {
                        'id': f"analyst_{analyst_name.lower().replace(' ', '_')}_{len(st.session_state.analysts)}",
                        'name': analyst_name,
                        'source': analyst_source,
                        'source_id': analyst_discord_id,
                        'enabled': True,
                        'notes': analyst_notes,
                        'trades': 0,
                        'wins': 0,
                        'losses': 0,
                        'win_rate': 0,
                        'expected_value': 1.0
                    }
                    st.session_state.analysts.append(new_analyst)
                    st.success(f"✅ Added {analyst_name}!")
                    st.session_state.show_add_analyst = False
                    st.rerun()
                else:
                    st.error("Please enter analyst name")
    
    st.divider()
    
    # List analysts
    st.subheader("Active Analysts")
    if st.session_state.analysts:
        for analyst in st.session_state.analysts:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{analyst['name']}**")
                st.caption(f"{analyst['source']} • EV: {analyst['expected_value']}")
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_{analyst['id']}"):
                    st.info("Edit feature coming soon")
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{analyst['id']}"):
                    st.session_state.analysts = [a for a in st.session_state.analysts if a['id'] != analyst['id']]
                    st.rerun()
    else:
        st.info("No analysts yet. Click '➕ Add' above to add one!")

# ===== TAB 3: RISK CONTROLS =====
with tab3:
    st.header("Risk Controls")
    
    # Daily Loss Limit
    st.subheader("💰 Daily Loss Limit")
    col1, col2 = st.columns(2)
    
    with col1:
        daily_loss_enabled = st.toggle("Enable Daily Loss Limit", value=True)
    
    if daily_loss_enabled:
        col1, col2 = st.columns(2)
        with col1:
            loss_type = st.radio("Type", ["Dollar Amount ($)", "Percent of Account (%)"])
        with col2:
            if loss_type == "Dollar Amount ($)":
                loss_value = st.number_input("Amount", min_value=0, value=500, step=100)
            else:
                loss_value = st.number_input("Percentage", min_value=0, max_value=100, value=5, step=1)
    
    st.divider()
    
    # Account Equity Monitor
    st.subheader("🏦 Account Equity Monitor")
    col1, col2 = st.columns(2)
    
    with col1:
        equity_enabled = st.toggle("Enable Account Equity Monitor", value=True)
    
    if equity_enabled:
        col1, col2 = st.columns(2)
        with col1:
            min_balance_dollar = st.number_input("Minimum Balance ($)", min_value=0, value=10000, step=1000)
        with col2:
            min_balance_percent = st.number_input("Minimum Balance (%)", min_value=0, max_value=100, value=50, step=5)
    
    st.divider()
    
    # Price Confirmation
    st.subheader("📍 Price Confirmation")
    col1, col2 = st.columns(2)
    
    with col1:
        price_conf_enabled = st.toggle("Enable Price Confirmation", value=True)
    
    if price_conf_enabled:
        with col2:
            max_slippage = st.number_input("Max Slippage (%)", min_value=0.0, value=2.0, step=0.1)
    
    st.divider()
    
    # Spread Protection
    st.subheader("📊 Spread Protection (Options)")
    col1, col2 = st.columns(2)
    
    with col1:
        spread_enabled = st.toggle("Enable Spread Protection", value=True)
    
    if spread_enabled:
        col1, col2 = st.columns(2)
        with col1:
            max_spread = st.number_input("Max Spread (%)", min_value=0.0, value=5.0, step=0.5)
        with col2:
            spread_action = st.selectbox("Action on Wide Spread", ["Place at Bid", "Place at Mid", "Place at Ask", "Reject"])
    
    # Save settings button
    if st.button("💾 Save Risk Settings"):
        st.success("✅ Risk settings saved!")

# ===== TAB 4: ANALYTICS =====
with tab4:
    st.header("Performance Analytics")
    
    if st.session_state.analysts:
        # Create dataframe
        analysts_data = []
        for analyst in st.session_state.analysts:
            analysts_data.append({
                'Analyst': analyst['name'],
                'Status': '🟢 On' if analyst['enabled'] else '🔴 Off',
                'Trades': analyst['trades'],
                'Wins': analyst['wins'],
                'Losses': analyst['losses'],
                'Win Rate': f"{analyst['win_rate']}%",
                'Expected Value': f"{analyst['expected_value']:.2f}"
            })
        
        df = pd.DataFrame(analysts_data)
        st.dataframe(df, use_container_width=True)
        
        # Charts (placeholder)
        st.subheader("📈 Charts")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("Win Rate Distribution - Coming Soon")
        
        with col2:
            st.info("Expected Value Comparison - Coming Soon")
    else:
        st.info("No analysts yet. Add analysts to see analytics.")

# ===== TAB 5: REJECTIONS =====
with tab5:
    st.header("Rejected Orders")
    
    st.info("No rejected orders yet.")
    
    # Placeholder table
    st.subheader("Recent Rejections")
    rejection_data = {
        'Time': [],
        'Symbol': [],
        'Action': [],
        'Reason': [],
        'Analyst': []
    }
    
    if rejection_data['Time']:
        df = pd.DataFrame(rejection_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No rejections. Your risk controls are working!")

# ===== FOOTER =====
st.divider()
st.caption("Trading Dashboard Pro v2.0 | Built with Streamlit")