# app.py -- Streamlit Sales Analytics dashboard
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Analytics", layout="wide")
st.title("📊 Sales Analytics Dashboard")

# === load CSV from your GitHub repo (raw URL) ===
CSV_URL = "https://raw.githubusercontent.com/yashratailor11559/sales-analytics/main/data/cleaned/sales_data_cleaned.csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df

try:
    df = load_data(CSV_URL)
except Exception as e:
    st.error(f"Failed to load data from GitHub. Error: {e}")
    st.stop()

# === tolerant column detection ===
# possible date columns
date_cols = [c for c in df.columns if c.lower() in ("sale_date","orderdate","order_date","date")]
date_col = date_cols[0] if date_cols else None

# possible sales column
sales_cols = [c for c in df.columns if c.lower() in ("totalsales","total_sales","sales","salesamount","sales_amount","total")]
sales_col = sales_cols[0] if sales_cols else None

# cast date if found
if date_col is not None:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["Month"] = df[date_col].dt.to_period("M").astype(str)

# KPI checks
if sales_col is None:
    st.warning("Could not find a sales column automatically. Available columns:\n" + ", ".join(df.columns))
else:
    st.metric("Total sales", f"{df[sales_col].sum():,.0f}")

# Sidebar filters
st.sidebar.header("Filters")
region_col = next((c for c in df.columns if c.lower() in ("region","state","area")), None)
product_col = next((c for c in df.columns if c.lower() in ("product","product_name","item")), None)
category_col = next((c for c in df.columns if c.lower() in ("category","product_category")), None)

if region_col:
    regions = ["All"] + sorted(df[region_col].dropna().unique().tolist())
    sel_region = st.sidebar.selectbox("Region", regions, index=0)
    if sel_region != "All":
        df = df[df[region_col] == sel_region]

if category_col:
    cats = ["All"] + sorted(df[category_col].dropna().unique().tolist())
    sel_cat = st.sidebar.selectbox("Category", cats, index=0)
    if sel_cat != "All":
        df = df[df[category_col] == sel_cat]

# Main visuals
col1, col2 = st.columns([2,1])

with col1:
    if date_col and sales_col:
        monthly = df.groupby("Month", as_index=False)[sales_col].sum()
        fig = px.line(monthly, x="Month", y=sales_col, markers=True, title="Monthly Sales")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    if product_col and sales_col:
        top_products = df.groupby(product_col, as_index=False)[sales_col].sum().nlargest(10, sales_col)
        fig2 = px.bar(top_products, x=sales_col, y=product_col, orientation="h", title="Top 10 Products by Sales")
        st.plotly_chart(fig2, use_container_width=True)

with col2:
    if region_col and sales_col:
        region_df = df.groupby(region_col, as_index=False)[sales_col].sum().sort_values(sales_col, ascending=False)
        st.write("### Sales by Region")
        fig3 = px.pie(region_df, names=region_col, values=sales_col, title="Sales Share by Region")
        st.plotly_chart(fig3, use_container_width=True)

# Data table & download
st.markdown("### Data sample")
st.dataframe(df.head(100))

@st.cache_data
def convert_df_to_csv(d):
    return d.to_csv(index=False).encode("utf-8")

csv_bytes = convert_df_to_csv(df)
st.download_button("Download filtered data (CSV)", data=csv_bytes, file_name="sales_data_filtered.csv", mime="text/csv")
