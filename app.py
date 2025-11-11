import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from streamlit_folium import st_folium
import folium

# Page config
st.set_page_config(
    page_title="AI Datacenter Company (Demo) - PitchDash",
    layout="wide",
    page_icon="🟢"
)

# Custom CSS for green theme
st.markdown("""
<style>
    .main {background-color: #FAFAFA;}
    h1 {color: #059669;}
    h2 {color: #047857;}
    .stMetric {background-color: white; padding: 15px; border-radius: 8px; border: 1px solid #E5E7EB;}
</style>
""", unsafe_allow_html=True)

# Header
st.title("🟢 AI Datacenter Company (Demo)")
st.markdown("**Series B Investment Opportunity | Sustainable AI Infrastructure**")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    financials = pd.read_csv('data/financial_projections_2015_2030.csv')
    datacenters = pd.read_csv('data/datacenter_locations.csv')
    investor_roi = pd.read_csv('data/investor_roi_summary.csv')
    operational = pd.read_csv('data/operational_metrics.csv')

    # Extend financials to 2035
    extended = []
    for year in range(2031, 2036):
        growth = 0.20 if year <= 2032 else 0.15
        prev_rev = financials.loc[financials['Year']==year-1, 'Revenue'].values[0]
        revenue = prev_rev * (1 + growth)

        if year == 2035:
            valuation = 460000000
        elif year == 2032:
            valuation = 200000000
        else:
            valuation = revenue * 6.5

        extended.append({'Year': year, 'Revenue': revenue, 'Company_Valuation': valuation, 'Status': 'Projected'})

    financials = pd.concat([financials, pd.DataFrame(extended)], ignore_index=True)
    return financials, datacenters, investor_roi, operational

financials, datacenters, investor_roi, operational = load_data()

# Sidebar navigation
st.sidebar.title("Navigation")
tab = st.sidebar.radio("Select Page", ["Growth Trajectory", "Investor Returns", "Operational Metrics", "Exit Scenarios"])

# Helper functions
def marker_radius(sqft):
    if sqft <= 15000: return 10
    if sqft <= 30000: return 15
    return 20

status_colors = {
    "Operational": "#059669",
    "Under Construction": "#F97316", 
    "Planned": "#3B82F6"
}

# ===================
# TAB 1: GROWTH TRAJECTORY
# ===================
if tab == "Growth Trajectory":
    st.header("📈 Growth Trajectory")

    # Revenue & Valuation Chart
    st.subheader("Revenue & Company Valuation (2015-2035)")

    light_green = '#10B981'
    dark_green = '#047857'

    fig = go.Figure()

    # Revenue line
    fig.add_trace(go.Scatter(
        x=financials['Year'],
        y=financials['Revenue']/1e6,
        name='Revenue ($M)',
        mode='lines+markers',
        line=dict(color=light_green, width=3),
        marker=dict(size=6, color=light_green, line=dict(width=2, color='white')),
        yaxis='y'
    ))

    # Valuation line
    fig.add_trace(go.Scatter(
        x=financials['Year'],
        y=financials['Company_Valuation']/1e6,
        name='Valuation ($M)',
        mode='lines+markers',
        line=dict(color=dark_green, width=3),
        marker=dict(size=6, color=dark_green, line=dict(width=2, color='white')),
        yaxis='y2'
    ))

    fig.update_layout(
        height=450,
        plot_bgcolor='white',
        xaxis=dict(title='Year', gridcolor='#F3F4F6'),
        yaxis=dict(
            title='Revenue ($M)',
            titlefont=dict(color=light_green),
            tickfont=dict(color=light_green),
            gridcolor='#F3F4F6'
        ),
        yaxis2=dict(
            title='Company Valuation ($M)',
            titlefont=dict(color=dark_green),
            tickfont=dict(color=dark_green),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.5, y=1.1, xanchor='center', yanchor='bottom', orientation='h'),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Datacenter Map
    st.subheader("🗺️ Datacenter Expansion Map")

    col1, col2 = st.columns([3, 1])

    with col1:
        year_selected = st.slider("Select Year", 2015, 2035, 2026, 1)

    with col2:
        st.markdown("**Legend**")
        st.markdown("🟢 Operational")
        st.markdown("🟠 Under Construction")
        st.markdown("🔵 Planned")

    # Filter datacenters
    active_dcs = datacenters[datacenters['year'] <= year_selected]

    # Create map
    m = folium.Map(location=[53.0, -115.0], zoom_start=4, tiles='cartodbpositron')

    for _, dc in active_dcs.iterrows():
        folium.CircleMarker(
            location=[dc['lat'], dc['lng']],
            radius=marker_radius(dc['sqft']),
            color=status_colors[dc['status']],
            fill=True,
            fillColor=status_colors[dc['status']],
            fillOpacity=0.7,
            weight=3,
            popup=f"<b>{dc['name']}</b><br>{dc['location']}<br>Year: {dc['year']}<br>Size: {dc['sqft']:,} sq ft<br>GPUs: {dc['gpus']:,}<br>Status: {dc['status']}"
        ).add_to(m)

    st_folium(m, width=None, height=500)

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Facilities", len(active_dcs))
    col2.metric("Total Space", f"{active_dcs['sqft'].sum():,} sq ft")
    col3.metric("Total GPUs", f"{active_dcs['gpus'].sum():,}")
    col4.metric("Total Power", f"{active_dcs['power_kw'].sum():,} kW")

# ===================
# TAB 2: INVESTOR RETURNS
# ===================
elif tab == "Investor Returns":
    st.header("💰 Investor Returns")

    st.subheader("Returns by Funding Round (Hold to IPO)")

    metric = st.selectbox("Select Metric", ["MOIC (Multiple)", "IRR %", "Exit Value ($M)", "Holding Period (Years)"])

    fig = go.Figure()

    if metric == "MOIC (Multiple)":
        y_data = investor_roi['MOIC']
        y_title = "MOIC (x)"
    elif metric == "IRR %":
        y_data = investor_roi['IRR_%']
        y_title = "IRR (%)"
    elif metric == "Exit Value ($M)":
        y_data = investor_roi['Exit_Value_M']
        y_title = "Exit Value ($M)"
    else:
        y_data = investor_roi['Holding_Period_Years']
        y_title = "Years"

    colors = ['#10B981' if r == 'Series B' else '#047857' for r in investor_roi['Round']]

    fig.add_trace(go.Bar(
        x=investor_roi['Round'],
        y=y_data,
        marker_color=colors,
        text=y_data.round(1),
        textposition='outside'
    ))

    fig.update_layout(
        height=400,
        plot_bgcolor='white',
        yaxis_title=y_title,
        xaxis_title="Funding Round",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Series B Investment Highlights")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Investment", "$8.0M")
    col2.metric("Exit Value", "$64.0M")
    col3.metric("MOIC", "8.0x")
    col4.metric("IRR", "26.0%")

# ===================
# TAB 3: OPERATIONAL METRICS
# ===================
elif tab == "Operational Metrics":
    st.header("📊 Operational Metrics")

    st.subheader("Infrastructure Growth (2015-2024)")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=operational['Year'],
        y=operational['GPU_Count'],
        name='GPU Count',
        mode='lines+markers',
        line=dict(color='#10B981', width=3),
        yaxis='y'
    ))

    fig.add_trace(go.Scatter(
        x=operational['Year'],
        y=operational['Number_of_Customers'],
        name='Customers',
        mode='lines+markers',
        line=dict(color='#047857', width=3),
        yaxis='y2'
    ))

    fig.update_layout(
        height=400,
        plot_bgcolor='white',
        yaxis=dict(title='GPU Count', titlefont=dict(color='#10B981'), tickfont=dict(color='#10B981')),
        yaxis2=dict(title='Customers', titlefont=dict(color='#047857'), tickfont=dict(color='#047857'), overlaying='y', side='right'),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("2024 Current State")

    col1, col2, col3 = st.columns(3)
    col1.metric("GPU Count", "2,184")
    col2.metric("Customers", "29")
    col3.metric("Avg Revenue/Customer", "$341K")

# ===================
# TAB 4: EXIT SCENARIOS
# ===================
else:
    st.header("🎯 Exit Scenarios")

    st.subheader("Interactive ROI Calculator")

    # Quick scenario buttons
    col1, col2, col3 = st.columns(3)

    if col1.button("🟢 Early Exit (Series C)", use_container_width=True):
        st.session_state.investment = 8.0
        st.session_state.exit_quarter = 11
    if col2.button("🟢 Mid Exit (Series D)", use_container_width=True):
        st.session_state.investment = 8.0
        st.session_state.exit_quarter = 25
    if col3.button("🟢 IPO Exit", use_container_width=True):
        st.session_state.investment = 8.0
        st.session_state.exit_quarter = 38

    st.markdown("---")

    # Sliders
    investment = st.slider("Investment Amount ($M)", 1.0, 20.0, st.session_state.get('investment', 8.0), 0.5)
    exit_quarter = st.slider("Exit Quarter (0 = Q2 2026, 38 = Q4 2035)", 0, 38, st.session_state.get('exit_quarter', 38), 1)

    # Store in session state
    st.session_state.investment = investment
    st.session_state.exit_quarter = exit_quarter

    # Calculate returns
    quarters = ['Q2 2026','Q3 2026','Q4 2026','Q1 2027','Q2 2027','Q3 2027','Q4 2027','Q1 2028','Q2 2028','Q3 2028','Q4 2028',
                'Q1 2029','Q2 2029','Q3 2029','Q4 2029','Q1 2030','Q2 2030','Q3 2030','Q4 2030','Q1 2031','Q2 2031','Q3 2031',
                'Q4 2031','Q1 2032','Q2 2032','Q3 2032','Q4 2032','Q1 2033','Q2 2033','Q3 2033','Q4 2033','Q1 2034','Q2 2034',
                'Q3 2034','Q4 2034','Q1 2035','Q2 2035','Q3 2035','Q4 2035']

    valuations = [33,34,35,40,45,50,55,66.25,77.5,88.75,100,100,120,140,160,180,200,220,240,242.35,244.7,247.05,249.4,
                  216.47,208.23,200,200,232.05,264.1,296.15,328.2,338.23,348.25,358.27,368.3,391.23,414.15,437.07,460]

    series_b_val = 33.0
    initial_ownership = (investment / series_b_val) * 100

    exit_ownership = initial_ownership
    if exit_quarter >= 11:  # After Series C
        exit_ownership *= 0.80
    if exit_quarter >= 25:  # After Series D
        exit_ownership *= 0.825

    exit_val = valuations[exit_quarter]
    exit_value = (exit_ownership / 100) * exit_val
    moic = exit_value / investment
    years = exit_quarter / 4.0
    irr = ((moic ** (1/years)) - 1) * 100 if years > 0 else 0

    # Display results
    st.markdown("### Results")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Initial Ownership", f"{initial_ownership:.2f}%")
    col2.metric("Exit Ownership", f"{exit_ownership:.2f}%")
    col3.metric("Exit Value", f"${exit_value:.1f}M")
    col4.metric("Return", f"${exit_value - investment:.1f}M")
    col5.metric("MOIC", f"{moic:.2f}x")
    col6.metric("IRR", f"{irr:.1f}%")

    st.info(f"**Exit:** {quarters[exit_quarter]} ({years:.1f} years) | **Company Valuation:** ${exit_val:.0f}M")

st.markdown("---")
st.caption("Demo dashboard for AI Datacenter Company - Fictional company showcasing PitchDash capabilities")
