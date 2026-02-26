import streamlit as st
import pandas as pd
import plotly.express as px

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="US Cost of Living",
    page_icon="🏙️",
    layout="wide",
)

# ── Theme / CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #111827; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3, p, label { color: #f9fafb !important; }
    [data-testid="metric-container"] {
        background: #1f2937;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 1rem 1.25rem;
    }
    [data-testid="metric-container"] label { color: #9ca3af !important; font-size: 0.8rem; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #f9fafb !important; }
    .stMultiSelect [data-baseweb="tag"] { background-color: #6366f1; }
    /* Expander dark theme */
    [data-testid="stExpander"] details {
        background-color: #1f2937;
        border: 1px solid #374151 !important;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    [data-testid="stExpander"] summary { color: #f9fafb !important; }
    [data-testid="stExpander"] summary:hover { background-color: #374151 !important; border-radius: 8px; }
    /* Mobile adjustments */
    @media (max-width: 640px) {
        .block-container { padding-left: 0.75rem !important; padding-right: 0.75rem !important; padding-top: 1rem !important; }
        h1 { font-size: 1.4rem !important; }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 0.5rem !important; }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] { flex: 1 1 calc(50% - 0.5rem) !important; min-width: calc(50% - 0.5rem) !important; }
        [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 0.8rem !important; word-break: break-word !important; }
        [data-testid="metric-container"] { padding: 0.75rem 1rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ── Plotly dark template ───────────────────────────────────────────────────────
TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="#1f2937",
        plot_bgcolor="#1f2937",
        font=dict(color="#f9fafb", family="Inter, sans-serif"),
        colorway=["#6366f1", "#818cf8", "#a5b4fc"],
        xaxis=dict(gridcolor="#374151", linecolor="#374151", zerolinecolor="#374151"),
        yaxis=dict(gridcolor="#374151", linecolor="#374151", zerolinecolor="#374151"),
        margin=dict(t=40, b=40, l=40, r=40),
    )
)

# ── Data ───────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("us_cost_of_living.csv")
    df["Purchasing_Power"] = (
        df["Avg_Monthly_Net_Salary"] /
        (df["Rent_1BR_City_Center"] + df["Groceries_Monthly_Est"] + df["Dining_Monthly_Est"])
    ).round(2)
    df["City_State"] = df["City"] + ", " + df["State"]
    return df

df = load_data()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# 🏙️ US Cost of Living Dashboard")
st.markdown(
    "<p style='color:#9ca3af;margin-top:-0.5rem;margin-bottom:1rem'>"
    "Comparing rent, groceries, dining, and purchasing power across 142 major US cities.</p>",
    unsafe_allow_html=True,
)

# ── Filters ─────────────────────────────────────────────────────────────────────
with st.expander("⚙️ Filters", expanded=False):
    all_states = sorted(df["State"].unique())

    btn_col1, btn_col2 = st.columns(2)
    if btn_col1.button("Select All", use_container_width=True):
        st.session_state["selected_states"] = all_states
    if btn_col2.button("Clear All", use_container_width=True):
        st.session_state["selected_states"] = []

    selected_states = st.multiselect(
        "States",
        all_states,
        default=st.session_state.get("selected_states", all_states),
        key="selected_states",
    )
    col_range = st.slider(
        "Cost of Living Index",
        int(df["Cost_of_Living_Index"].min()),
        int(df["Cost_of_Living_Index"].max()),
        (int(df["Cost_of_Living_Index"].min()), int(df["Cost_of_Living_Index"].max())),
    )
    st.markdown(
        "<small style='color:#9ca3af'>Data sourced from Numbeo public data. "
        "All figures approximate.</small>",
        unsafe_allow_html=True,
    )

filtered = df[
    df["State"].isin(selected_states) &
    df["Cost_of_Living_Index"].between(*col_range)
]

# ── KPI metrics ────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Cities", len(filtered))
m2.metric("Avg Monthly Rent (1BR)", f"${filtered['Rent_1BR_City_Center'].mean():,.0f}")
m3.metric("Avg Monthly Salary", f"${filtered['Avg_Monthly_Net_Salary'].mean():,.0f}")
m4.metric(
    "Best Purchasing Power",
    filtered.loc[filtered["Purchasing_Power"].idxmax(), "City"] if not filtered.empty else "—",
)

st.markdown("---")

# ── Map ────────────────────────────────────────────────────────────────────────
st.markdown("### Cost of Living by City")

fig_map = px.scatter_mapbox(
    filtered,
    lat="Lat",
    lon="Lon",
    size="Cost_of_Living_Index",
    color="Cost_of_Living_Index",
    hover_name="City_State",
    hover_data={
        "Cost_of_Living_Index": True,
        "Rent_1BR_City_Center": ":$,.0f",
        "Avg_Monthly_Net_Salary": ":$,.0f",
        "Lat": False,
        "Lon": False,
    },
    color_continuous_scale=["#312e81", "#6366f1", "#a5b4fc"],
    size_max=30,
    zoom=3.2,
    center={"lat": 39.5, "lon": -98.35},
    mapbox_style="carto-darkmatter",
    labels={
        "Cost_of_Living_Index": "CoL Index",
        "Rent_1BR_City_Center": "1BR Rent",
        "Avg_Monthly_Net_Salary": "Avg Salary",
    },
)
fig_map.update_layout(
    **TEMPLATE["layout"],
    height=440,
    coloraxis_colorbar=dict(title="CoL Index", tickfont=dict(color="#9ca3af")),
)
st.plotly_chart(fig_map, use_container_width=True)

# ── Scatter ────────────────────────────────────────────────────────────────────
st.markdown("### Salary vs. Cost of Living")
fig_scatter = px.scatter(
    filtered,
    x="Cost_of_Living_Index",
    y="Avg_Monthly_Net_Salary",
    size="Purchasing_Power",
    color="Purchasing_Power",
    hover_name="City_State",
    hover_data={
        "Cost_of_Living_Index": True,
        "Avg_Monthly_Net_Salary": ":$,.0f",
        "Purchasing_Power": ":.2f",
    },
    color_continuous_scale=["#312e81", "#6366f1", "#a5b4fc"],
    labels={
        "Cost_of_Living_Index": "Cost of Living Index",
        "Avg_Monthly_Net_Salary": "Avg Monthly Salary (USD)",
        "Purchasing_Power": "Purchasing Power",
    },
    size_max=25,
)
fig_scatter.update_layout(
    **TEMPLATE["layout"],
    height=500,
    coloraxis_colorbar=dict(title="Purch. Power", tickfont=dict(color="#9ca3af")),
    yaxis_tickprefix="$",
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ── Data table ─────────────────────────────────────────────────────────────────
st.markdown("### Full Data Table")
table_df = (
    filtered[["City", "State", "Cost_of_Living_Index", "Rent_1BR_City_Center",
              "Rent_1BR_Outside_Center", "Avg_Monthly_Net_Salary",
              "Groceries_Monthly_Est", "Dining_Monthly_Est", "Purchasing_Power"]]
    .sort_values("Cost_of_Living_Index", ascending=False)
    .rename(columns={
        "Cost_of_Living_Index": "CoL Index",
        "Rent_1BR_City_Center": "Rent (Center)",
        "Rent_1BR_Outside_Center": "Rent (Outside)",
        "Avg_Monthly_Net_Salary": "Avg Salary",
        "Groceries_Monthly_Est": "Groceries/mo",
        "Dining_Monthly_Est": "Dining/mo",
        "Purchasing_Power": "Purch. Power",
    })
)
st.dataframe(
    table_df.style.format({
        "CoL Index": "{:.1f}",
        "Rent (Center)": "${:,.0f}",
        "Rent (Outside)": "${:,.0f}",
        "Avg Salary": "${:,.0f}",
        "Groceries/mo": "${:,.0f}",
        "Dining/mo": "${:,.0f}",
        "Purch. Power": "{:.2f}",
    }),
    use_container_width=True,
    hide_index=True,
)

# ── Data sources ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Data Sources")
st.markdown("""
| Source | Data Used | Link |
|---|---|---|
| **Numbeo** | Cost of living indices, rent prices, groceries & dining estimates, average net salary | [numbeo.com/cost-of-living](https://www.numbeo.com/cost-of-living/) |
| **US Census Bureau** | City geographic coordinates (latitude/longitude) | [census.gov](https://www.census.gov/geographies/reference-files.html) |

**Notes:**
- All cost figures are in **USD** and represent approximate monthly estimates for a single person.
- The **Cost of Living Index** is relative to New York City (NYC = 100). A score of 50 means roughly half the cost of living in NYC.
- The **Purchasing Power Score** is calculated as: *Average Monthly Net Salary ÷ (Rent + Groceries + Dining)*. A score above 1.5 indicates strong purchasing power; below 1.0 means typical expenses exceed take-home pay.
- Salary figures represent average **after-tax** monthly net income and vary by occupation and individual circumstances.
- Data reflects conditions as of **2024–2025**. Figures may not capture the most recent market changes.
""")
