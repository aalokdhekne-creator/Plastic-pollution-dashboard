# =============================================================
# ♻️ PLASTIC POLLUTION DASHBOARD — ECO GREEN THEME (FINAL POLISHED)
# Added dashboard title: "Worldwide Plastic Pollution Data"
# =============================================================

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------
# 🌿 Eco-Green Theme Styling
# -----------------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #E8F5E9;
    color: #1B5E20;
}
[data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
[data-testid="stSidebar"] {
    background-color: #C8E6C9;
    color: #1B5E20;
}
h1, h2, h3, h4, h5 { color: #1B5E20; }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -----------------------------
# Load data
# -----------------------------
file_path = r"D:\Plastic_Data\Data\new\plastics_normalized.csv"
df = pd.read_csv(file_path)

required = [
    "country","year","parent_company","empty","hdpe","ldpe","o","pet","pp","ps","pvc",
    "grand_total","num_events","volunteers","grand_total_per_volunteer"
]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(f"❌ Missing columns: {missing}")
    st.stop()

# Identify total vs company rows
df = df.sort_values(["country", "year"]).reset_index(drop=True)
df["is_total_row"] = df.groupby(["country", "year"]).cumcount() == 0
totals = df[df["is_total_row"]]
companies = df[~df["is_total_row"]]

# -----------------------------
# 🏷️ Dashboard Header
# -----------------------------
st.markdown("""
<h1 style='text-align: center; color: #1B5E20;'>
🌍 Worldwide Plastic Pollution Data Dashboard
</h1>
<p style='text-align: center; font-size:18px; color:#2E7D32;'>
Analyzing plastic waste trends, recyclability, and brand impact across countries.
</p>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.title("🌍 Plastic Pollution Dashboard")

year_selected = st.sidebar.selectbox("Select Year", sorted(totals["year"].unique()))
country_selected = st.sidebar.selectbox("Select Country", sorted(totals["country"].unique()))
parent_company_selected = st.sidebar.selectbox(
    "Select Parent Company (for composition)",
    ["All"] + sorted(companies["parent_company"].dropna().unique())
)

totals_y = totals[totals["year"] == year_selected]
total_row = totals_y[totals_y["country"] == country_selected]
companies_y = companies[companies["year"] == year_selected]
companies_yc = companies[(companies["year"] == year_selected) & (companies["country"] == country_selected)]

# -----------------------------
# KPI Section
# -----------------------------
st.markdown(f"## 📊 Key Indicators — {country_selected} ({year_selected})")

if not total_row.empty:
    total_plastic = float(total_row["grand_total"].iloc[0])
    volunteers = float(total_row["volunteers"].iloc[0])
    events = float(total_row["num_events"].iloc[0])
    per_vol = float(total_row["grand_total_per_volunteer"].iloc[0])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🪣 Total Plastic Collected", f"{total_plastic:,.0f}")
    c2.metric("👥 Volunteers", f"{volunteers:,.0f}")
    c3.metric("📆 Events", f"{events:,.0f}")
    c4.metric("⚖️ Plastic per Volunteer", f"{per_vol:,.2f}")
else:
    st.warning(f"No total row for {country_selected} in {year_selected}")

# -----------------------------
# 🌍 World Map (Pretty Hover Template)
# -----------------------------
hover_template = (
    "<b>%{customdata[0]}</b><br><br>"
    "🗓 Year: %{customdata[1]}<br>"
    "🪣 Total Plastic: %{customdata[2]:,.0f} pieces<br>"
    "👥 Volunteers: %{customdata[3]:,.0f}<br>"
    "⚖️ Plastic/Volunteer: %{customdata[4]:,.2f} pieces<br><extra></extra>"
)

totals_y["custom_hover"] = list(
    zip(
        totals_y["country"],
        totals_y["year"],
        totals_y["grand_total"],
        totals_y["volunteers"],
        totals_y["grand_total_per_volunteer"]
    )
)

fig_map = go.Figure(go.Choropleth(
    locations=totals_y["country"],
    locationmode="country names",
    z=totals_y["grand_total_per_volunteer"],
    colorscale="OrRd",
    text=totals_y["country"],
    customdata=totals_y["custom_hover"],
    hovertemplate=hover_template,
    colorbar_title="Plastic/Volunteer"
))

sel_t = totals_y[totals_y["country"] == country_selected]
if not sel_t.empty:
    fig_map.add_trace(go.Scattergeo(
        locations=[country_selected],
        locationmode="country names",
        text=[country_selected],
        mode="markers+text",
        marker=dict(size=15, color="navy", line=dict(width=2, color="white")),
        textposition="top center",
        name="Selected Country"
    ))

fig_map.update_layout(
    title=f"🌎 Plastic Collected per Volunteer — {year_selected}",
    height=600
)
st.plotly_chart(fig_map, use_container_width=True)

# -----------------------------
# 🧱 Plastic Type Composition
# -----------------------------
plastics_cols = ["hdpe","ldpe","o","pet","pp","ps","pvc"]

if parent_company_selected == "All":
    comp_for_comp = companies_yc
    title_suffix = f"All Companies — {country_selected} ({year_selected})"
else:
    comp_for_comp = companies_yc[companies_yc["parent_company"] == parent_company_selected]
    title_suffix = f"{parent_company_selected} — {country_selected} ({year_selected})"

if not comp_for_comp.empty:
    comp_vals = comp_for_comp[plastics_cols].sum()
    fig_bar = go.Figure(go.Bar(
        x=comp_vals.values,
        y=[c.upper() for c in comp_vals.index],
        orientation="h",
        marker=dict(color="steelblue"),
        text=[f"{v:,.0f}" for v in comp_vals.values],
        textposition="auto"
    ))
    fig_bar.update_layout(
        title=f"♻️ Plastic Type Distribution — {title_suffix}",
        xaxis_title="Quantity (pieces)",
        yaxis_title="Plastic Type",
        height=420
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# 🔄 Recyclable vs Non-Recyclable Trend
# -----------------------------
recyclable = ["hdpe","ldpe","pet","pp"]
non_recyclable = ["ps","pvc","o"]

comp_country_all_years = companies[companies["country"] == country_selected]

if not comp_country_all_years.empty:
    trend = (
        comp_country_all_years
        .groupby("year")[recyclable + non_recyclable]
        .sum()
        .reset_index()
    )
    trend["Recyclable"] = trend[recyclable].sum(axis=1)
    trend["Non-Recyclable"] = trend[non_recyclable].sum(axis=1)

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(
        x=trend["year"], y=trend["Recyclable"],
        name="Recyclable", marker_color="royalblue"
    ))
    fig_trend.add_trace(go.Bar(
        x=trend["year"], y=trend["Non-Recyclable"],
        name="Non-Recyclable", marker_color="darkorange"
    ))
    fig_trend.update_layout(
        title=f"♻️ Recyclable vs Non-Recyclable — {country_selected} (by Year)",
        xaxis_title="Year", yaxis_title="Plastic (pieces)",
        barmode="group", height=460
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------
# 📈 Plastic Type Trend (2019–2020)
# -----------------------------
if not comp_country_all_years.empty:
    trend_types = (
        comp_country_all_years
        .groupby("year")[plastics_cols]
        .sum()
        .reset_index()
    )

    fig_type_trend = px.line(
        trend_types,
        x="year",
        y=plastics_cols,
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Set2,
        title=f"📈 Plastic Type Trend — {country_selected} (2019–2020)"
    )
    fig_type_trend.update_layout(height=480)
    st.plotly_chart(fig_type_trend, use_container_width=True)

# -----------------------------
# 🏭 Top 10 Parent Companies
# -----------------------------
top10 = (
    companies_y
    .groupby("parent_company")["grand_total_per_volunteer"]
    .sum()
    .reset_index()
    .sort_values(by="grand_total_per_volunteer", ascending=False)
    .head(10)
)

if not top10.empty:
    fig_top10 = px.bar(
        top10,
        x="parent_company",
        y="grand_total_per_volunteer",
        text_auto=".2f",
        color="grand_total_per_volunteer",
        color_continuous_scale="Purples",
        title=f"🏭 Top 10 Parent Companies by Plastic per Volunteer ({year_selected})"
    )
    fig_top10.update_layout(
        xaxis_title="Parent Company",
        yaxis_title="Plastic per Volunteer",
        height=500
    )
    st.plotly_chart(fig_top10, use_container_width=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Developed for Plastic Pollution Data Analysis • Eco Green Theme • Streamlit + Plotly")
