import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Rwanda Trade Intelligence",
    page_icon="🇷🇼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# RWANDA FLAG COLORS
# ============================================================================
RWANDA_BLUE = "#00A1DE"
RWANDA_YELLOW = "#FAD201"
RWANDA_GREEN = "#00A859"
COLORS = [RWANDA_BLUE, RWANDA_YELLOW, RWANDA_GREEN, "#E74C3C", "#9B59B6", "#3498DB"]

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
    <style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #00A1DE 0%, #00A859 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #00A1DE 0%, #00A859 100%);
    }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #00A1DE 0%, #FAD201 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        margin: 10px 0;
        min-height: 140px;
    }
    
    .kpi-value {
        font-size: 2.8rem;
        font-weight: bold;
        margin: 10px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .kpi-label {
        font-size: 1.1rem;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    
    .kpi-change {
        font-size: 1rem;
        margin-top: 5px;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Info box */
    .info-box {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FAD201;
        color: white;
        margin: 10px 0;
    }
    
    /* Filters */
    .stSelectbox label, .stMultiSelect label {
        color: white !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================
@st.cache_data
def load_data():
    """Load Rwanda trade data"""
    try:
        df = pd.read_csv('rwanda_trade_data.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        st.error("⚠️ Data file not found! Please run create_rwanda_trade_data.py first")
        st.stop()

df = load_data()

# ============================================================================
# 1️⃣ HEADER - EXECUTIVE OVERVIEW PAGE
# ============================================================================
col1, col2 = st.columns([3, 1])

with col1:
    st.title("🇷🇼 Merchandise Trade Intelligence Dashboard")
    st.subheader("Executive Overview")

with col2:
    # Reference period and last update
    latest_date = df['Date'].max()
    st.markdown(f"""
        <div class="info-box">
        <strong>Reference Period:</strong><br>
        {latest_date.strftime('%B %Y')}<br>
        <strong>Currency:</strong> USD<br>
        <strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d')}
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# 2️⃣ USER FILTERS - CONTROL PANEL
# ============================================================================
st.sidebar.title("🎛️ Control Panel")
st.sidebar.markdown("---")

# Year Filter
years = sorted(df['Year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox(
    "📅 Select Year",
    options=years,
    index=0
)

# Quarter Filter
quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
selected_quarter = st.sidebar.selectbox(
    "📊 Select Quarter",
    options=quarters,
    index=0
)

# Month Filter (dependent on quarter)
if selected_quarter == 'All':
    available_months = ['All'] + list(df['Month_Name'].unique())
else:
    quarter_months = {
        'Q1': ['January', 'February', 'March'],
        'Q2': ['April', 'May', 'June'],
        'Q3': ['July', 'August', 'September'],
        'Q4': ['October', 'November', 'December']
    }
    available_months = ['All'] + quarter_months[selected_quarter]

selected_month = st.sidebar.selectbox(
    "📆 Select Month",
    options=available_months,
    index=0
)

# Trade Flow Filter
flows = ['All', 'Export', 'Import', 'Re-export']
selected_flow = st.sidebar.selectbox(
    "🔄 Trade Flow",
    options=flows,
    index=0
)

# Partner Level Filter
partner_levels = ['World', 'Regional Block', 'Continent', 'Country']
selected_partner_level = st.sidebar.selectbox(
    "🌍 Partner Level",
    options=partner_levels,
    index=0
)

# Product Filter (HS Code)
hs_codes = ['All'] + sorted(df['HS_Code'].unique().tolist())
selected_hs = st.sidebar.multiselect(
    "📦 HS Code Filter",
    options=hs_codes,
    default=['All']
)

st.sidebar.markdown("---")
st.sidebar.info("**Source:** Rwanda Customs\n\n**Coverage:** Formal merchandise trade only")

# ============================================================================
# 3️⃣ DATA ENGINE - APPLY FILTERS
# ============================================================================
def filter_data(df, year, quarter, month, flow, hs_codes):
    """Apply all filters to the dataset"""
    filtered = df[df['Year'] == year].copy()
    
    # Quarter filter
    if quarter != 'All':
        filtered = filtered[filtered['Quarter'] == quarter]
    
    # Month filter
    if month != 'All':
        filtered = filtered[filtered['Month_Name'] == month]
    
    # Flow filter
    if flow != 'All':
        filtered = filtered[filtered['Flow'] == flow]
    
    # HS Code filter
    if 'All' not in hs_codes:
        filtered = filtered[filtered['HS_Code'].isin(hs_codes)]
    
    return filtered

filtered_df = filter_data(df, selected_year, selected_quarter, selected_month, selected_flow, selected_hs)

# ============================================================================
# 4️⃣ KEY TRADE INDICATORS - KPI SECTION
# ============================================================================
st.header("📊 Key Trade Indicators")

# Calculate KPIs
total_trade = filtered_df['Trade_Value_USD'].sum()
total_exports = filtered_df[filtered_df['Flow'] == 'Export']['Trade_Value_USD'].sum()
total_imports = filtered_df[filtered_df['Flow'] == 'Import']['Trade_Value_USD'].sum()
total_reexports = filtered_df[filtered_df['Flow'] == 'Re-export']['Trade_Value_USD'].sum()
trade_balance = total_exports - total_imports

# Calculate growth (YoY)
prev_year = selected_year - 1
if prev_year in df['Year'].values:
    prev_filtered = filter_data(df, prev_year, selected_quarter, selected_month, selected_flow, selected_hs)
    prev_total = prev_filtered['Trade_Value_USD'].sum()
    if prev_total > 0:
        growth_rate = ((total_trade - prev_total) / prev_total) * 100
    else:
        growth_rate = 0
else:
    growth_rate = 0

# Display KPI Cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Trade</div>
            <div class="kpi-value">${total_trade/1e6:.1f}M</div>
            <div class="kpi-change">{'↑' if growth_rate > 0 else '↓'} {abs(growth_rate):.1f}% YoY</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Exports</div>
            <div class="kpi-value">${total_exports/1e6:.1f}M</div>
            <div class="kpi-change">{(total_exports/total_trade*100):.1f}% of total</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Imports</div>
            <div class="kpi-value">${total_imports/1e6:.1f}M</div>
            <div class="kpi-change">{(total_imports/total_trade*100):.1f}% of total</div>
        </div>
    """, unsafe_allow_html=True)

col4, col5 = st.columns(2)

with col4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Re-exports</div>
            <div class="kpi-value">${total_reexports/1e6:.1f}M</div>
            <div class="kpi-change">{(total_reexports/total_trade*100):.1f}% of total</div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    balance_color = RWANDA_GREEN if trade_balance > 0 else "#E74C3C"
    balance_text = "Surplus" if trade_balance > 0 else "Deficit"
    st.markdown(f"""
        <div class="kpi-card" style="background: linear-gradient(135deg, {balance_color} 0%, {RWANDA_YELLOW} 100%);">
            <div class="kpi-label">Trade Balance</div>
            <div class="kpi-value">${abs(trade_balance)/1e6:.1f}M</div>
            <div class="kpi-change">{balance_text}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# 5️⃣ TRADE DISTRIBUTION - GEOGRAPHY OVERVIEW
# ============================================================================
st.header("🌍 Trade Distribution by Geography")

col1, col2 = st.columns(2)

with col1:
    # Trade by Continent
    continent_data = filtered_df.groupby('Partner_Continent')['Trade_Value_USD'].sum().reset_index()
    continent_data = continent_data.sort_values('Trade_Value_USD', ascending=False)
    
    fig_continent = px.pie(
        continent_data,
        values='Trade_Value_USD',
        names='Partner_Continent',
        title='Trade Distribution by Continent',
        color_discrete_sequence=COLORS,
        hole=0.4
    )
    fig_continent.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_continent, use_container_width=True)

with col2:
    # Trade by Regional Block
    regional_data = filtered_df.groupby('Regional_Block')['Trade_Value_USD'].sum().reset_index()
    regional_data = regional_data.sort_values('Trade_Value_USD', ascending=True)
    
    fig_regional = px.bar(
        regional_data,
        y='Regional_Block',
        x='Trade_Value_USD',
        title='Trade Value by Regional Block',
        orientation='h',
        color='Trade_Value_USD',
        color_continuous_scale=[[0, RWANDA_BLUE], [0.5, RWANDA_YELLOW], [1, RWANDA_GREEN]]
    )
    fig_regional.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False
    )
    st.plotly_chart(fig_regional, use_container_width=True)

st.markdown("---")

# ============================================================================
# 6️⃣ TOP 20 TRADE PARTNERS
# ============================================================================
st.header("🏆 Top 20 Trade Partners")

tab1, tab2, tab3 = st.tabs(["📤 Export Destinations", "📥 Import Origins", "🔄 Re-export Destinations"])

with tab1:
    # Top 20 Export Destinations
    export_data = filtered_df[filtered_df['Flow'] == 'Export'].groupby('Partner_Country')['Trade_Value_USD'].sum()
    top_exports = export_data.nlargest(20).reset_index()
    top_exports['Rank'] = range(1, len(top_exports) + 1)
    top_exports['Share_%'] = (top_exports['Trade_Value_USD'] / top_exports['Trade_Value_USD'].sum() * 100).round(2)
    
    fig_exp = px.bar(
        top_exports,
        y='Partner_Country',
        x='Trade_Value_USD',
        orientation='h',
        title='Top 20 Export Destinations',
        color='Trade_Value_USD',
        color_continuous_scale=[[0, RWANDA_BLUE], [0.5, RWANDA_YELLOW], [1, RWANDA_GREEN]],
        text='Share_%'
    )
    fig_exp.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_exp.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=600
    )
    st.plotly_chart(fig_exp, use_container_width=True)

with tab2:
    # Top 20 Import Origins
    import_data = filtered_df[filtered_df['Flow'] == 'Import'].groupby('Partner_Country')['Trade_Value_USD'].sum()
    top_imports = import_data.nlargest(20).reset_index()
    top_imports['Rank'] = range(1, len(top_imports) + 1)
    top_imports['Share_%'] = (top_imports['Trade_Value_USD'] / top_imports['Trade_Value_USD'].sum() * 100).round(2)
    
    fig_imp = px.bar(
        top_imports,
        y='Partner_Country',
        x='Trade_Value_USD',
        orientation='h',
        title='Top 20 Import Origins',
        color='Trade_Value_USD',
        color_continuous_scale=[[0, RWANDA_GREEN], [0.5, RWANDA_YELLOW], [1, RWANDA_BLUE]],
        text='Share_%'
    )
    fig_imp.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_imp.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=600
    )
    st.plotly_chart(fig_imp, use_container_width=True)

with tab3:
    # Top 20 Re-export Destinations
    reexport_data = filtered_df[filtered_df['Flow'] == 'Re-export'].groupby('Partner_Country')['Trade_Value_USD'].sum()
    top_reexports = reexport_data.nlargest(20).reset_index()
    top_reexports['Rank'] = range(1, len(top_reexports) + 1)
    top_reexports['Share_%'] = (top_reexports['Trade_Value_USD'] / top_reexports['Trade_Value_USD'].sum() * 100).round(2)
    
    fig_reexp = px.bar(
        top_reexports,
        y='Partner_Country',
        x='Trade_Value_USD',
        orientation='h',
        title='Top 20 Re-export Destinations',
        color='Trade_Value_USD',
        color_continuous_scale=[[0, RWANDA_YELLOW], [0.5, RWANDA_GREEN], [1, RWANDA_BLUE]],
        text='Share_%'
    )
    fig_reexp.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_reexp.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=600
    )
    st.plotly_chart(fig_reexp, use_container_width=True)

st.markdown("---")

# ============================================================================
# 7️⃣ KEY PRODUCTS - HS INTELLIGENCE
# ============================================================================
st.header("📦 Key Products (HS Code Analysis)")

col1, col2 = st.columns(2)

with col1:
    # Top 15 Products by Value
    product_data = filtered_df.groupby(['HS_Code', 'HS_Description'])['Trade_Value_USD'].sum()
    top_products = product_data.nlargest(15).reset_index()
    top_products['Product'] = top_products[['HS_Code', 'HS_Description']].astype(str).agg(' - '.join, axis=1)

    
    fig_products = px.bar(
        top_products,
        y='Product',
        x='Trade_Value_USD',
        orientation='h',
        title='Top 15 Products by Trade Value',
        color='Trade_Value_USD',
        color_continuous_scale=[[0, RWANDA_BLUE], [1, RWANDA_GREEN]]
    )
    fig_products.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=500
    )
    st.plotly_chart(fig_products, use_container_width=True)

with col2:
    # Product Distribution by Flow
    flow_product = filtered_df.groupby(['Flow', 'HS_Description'])['Trade_Value_USD'].sum().reset_index()
    top_flow_products = flow_product.nlargest(15, 'Trade_Value_USD')
    
    fig_flow_prod = px.sunburst(
        top_flow_products,
        path=['Flow', 'HS_Description'],
        values='Trade_Value_USD',
        title='Product Distribution by Trade Flow',
        color='Trade_Value_USD',
        color_continuous_scale=[[0, RWANDA_BLUE], [0.5, RWANDA_YELLOW], [1, RWANDA_GREEN]]
    )
    fig_flow_prod.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    st.plotly_chart(fig_flow_prod, use_container_width=True)

st.markdown("---")

# ============================================================================
# 8️⃣ TRENDS & INSIGHTS
# ============================================================================
st.header("📈 Trade Trends & Insights")

# Monthly trend (for selected year)
monthly_trend = df[df['Year'] == selected_year].groupby(['Month_Name', 'Flow'])['Trade_Value_USD'].sum().reset_index()

# Order months correctly
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_trend['Month_Name'] = pd.Categorical(monthly_trend['Month_Name'], categories=month_order, ordered=True)
monthly_trend = monthly_trend.sort_values('Month_Name')

fig_trend = px.line(
    monthly_trend,
    x='Month_Name',
    y='Trade_Value_USD',
    color='Flow',
    title=f'Monthly Trade Trends - {selected_year}',
    markers=True,
    color_discrete_map={'Export': RWANDA_BLUE, 'Import': RWANDA_YELLOW, 'Re-export': RWANDA_GREEN}
)
fig_trend.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    xaxis_title="Month",
    yaxis_title="Trade Value (USD)",
    height=400
)
st.plotly_chart(fig_trend, use_container_width=True)

# Automated Insights
st.subheader("💡 Key Insights")

col1, col2, col3 = st.columns(3)

with col1:
    # Top export partner
    if len(top_exports) > 0:
        top_exp_partner = top_exports.iloc[0]['Partner_Country']
        top_exp_value = top_exports.iloc[0]['Trade_Value_USD']
        top_exp_share = top_exports.iloc[0]['Share_%']
        st.info(f"**Top Export Destination:** {top_exp_partner} (${top_exp_value/1e6:.1f}M, {top_exp_share:.1f}% of exports)")

with col2:
    # Trade balance status
    if trade_balance > 0:
        st.success(f"**Trade Surplus:** Rwanda has a trade surplus of ${abs(trade_balance)/1e6:.1f}M")
    else:
        st.warning(f"**Trade Deficit:** Rwanda has a trade deficit of ${abs(trade_balance)/1e6:.1f}M")

with col3:
    # Regional concentration
    eac_trade = filtered_df[filtered_df['Regional_Block'] == 'EAC']['Trade_Value_USD'].sum()
    eac_share = (eac_trade / total_trade * 100) if total_trade > 0 else 0
    st.info(f"**EAC Trade Share:** {eac_share:.1f}% of total trade is with EAC partners")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: white;'>
        <p>🇷🇼 <strong>Rwanda Merchandise Trade Intelligence Dashboard</strong></p>
        <p>Built with Streamlit | Data Source: Rwanda Customs | Coverage: Formal Trade Only</p>
        <p style='font-size: 0.8rem;'>Last Updated: {}</p>
    </div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M')), unsafe_allow_html=True)
