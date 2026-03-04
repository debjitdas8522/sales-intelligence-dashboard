import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.load_data import load_sales_data


st.markdown("""
<style>
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #111, #1a1a1a);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #333;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


# Page config
st.set_page_config(layout="wide", page_title="Sales Dashboard", page_icon="📊")

# -----------------------------
# TITLE
# -----------------------------
st.markdown("## 📊 Sales Intelligence Dashboard")
st.caption("Analyze sales performance with interactive filters and business insights")
st.markdown("---")

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
df = load_sales_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.markdown("### 🔍 Filters")
st.markdown("<hr style='margin-top:-10px;margin-bottom:20px;'>", unsafe_allow_html=True)

min_date = df['Order Date'].min()
max_date = df['Order Date'].max()

f1, f2, f3 = st.columns(3)

with f1:
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

with f2:
    region = st.selectbox("Region", df['Region'].unique())

with f3:
    category = st.selectbox("Category", df['Category'].unique())

st.markdown("---")


# Handle date safely
if isinstance(date_range, tuple):
    start_date = date_range[0]
    end_date = date_range[1] if len(date_range) > 1 else date_range[0]
else:
    start_date = date_range
    end_date = date_range


# Apply filters
filtered_df = df[
    (df['Region'] == region) &
    (df['Category'] == category) &
    (df['Order Date'] >= pd.to_datetime(start_date)) &
    (df['Order Date'] <= pd.to_datetime(end_date))
]

if filtered_df.empty:
    st.warning("No data available for selected filters")
    st.stop()


# -----------------------------
# KPI CALCULATIONS 
# -----------------------------
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
profit_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0
# -----------------------------
# KPIs
# -----------------------------
st.markdown("### 📌 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric(
    "💰 Total Sales",
    f"₹ {total_sales:,.0f}",
    delta=None
)

col2.metric(
    "📈 Total Profit",
    f"₹ {total_profit:,.0f}",
    delta="Good" if total_profit > 0 else "Loss"
)

col3.metric(
    "📊 Profit Margin",
    f"{profit_margin:.2f}%",
    delta="Healthy" if profit_margin > 10 else "Low"
)


# -----------------------------
# Monthly Sales (Plotly)
st.markdown("### 📈 Monthly Sales Trend")

from charts.monthly_sales import monthly_sales_chart

fig = monthly_sales_chart(filtered_df)
st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Forecast
# -----------------------------
st.markdown("---")
st.markdown("## 🔮 Sales Forecast (Next 3 Months)")

# Monthly sales data
monthly_sales = (
    filtered_df
    .set_index("Order Date")
    .resample("M")["Sales"]
    .sum()
    .reset_index()
)

# Create numeric index
monthly_sales["t"] = np.arange(len(monthly_sales))

# Linear regression (trend line)
coeffs = np.polyfit(monthly_sales["t"], monthly_sales["Sales"], 1)

# Forecast next 3 months
future_t = np.arange(len(monthly_sales), len(monthly_sales) + 3)
future_sales = np.polyval(coeffs, future_t)

future_dates = pd.date_range(
    monthly_sales["Order Date"].iloc[-1] + pd.DateOffset(months=1),
    periods=3,
    freq="M"
)

forecast_df = pd.DataFrame({
    "Order Date": future_dates,
    "Sales": future_sales
})

forecast_df["Type"] = "Forecast"
monthly_sales["Type"] = "Actual"

combined_df = pd.concat([monthly_sales, forecast_df])

fig_forecast = px.line(
    combined_df,
    x="Order Date",
    y="Sales",
    color="Type",
    markers=True
)

fig_forecast.update_layout(
    template="plotly_dark",
    title="Sales Forecast (Next 3 Months)",
    title_x=0.3
)

st.plotly_chart(fig_forecast, use_container_width=True)


# -----------------------------
# REGION-WISE SALES
# -----------------------------

st.markdown("---")
st.markdown("## 🌍 Region Performance")

from charts.region_sales import region_sales_chart

fig = region_sales_chart(df)
st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# TOP PRODUCTS + CUSTOMERS
# -----------------------------
st.markdown("---")
st.markdown("## 🏆 Business Insights")

# Top products
top_products = (
    filtered_df.groupby('Product Name')['Sales']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

# Top customers
top_customers = (
    filtered_df.groupby("Customer Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)


col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🛒 Top Products")

    fig_prod = px.bar(
        top_products.sort_values(),
        orientation='h'
    )

    fig_prod.update_layout(
        template="plotly_dark",
        height=500,
        title="Top Products by Sales",
        title_x=0.3
    )

    st.plotly_chart(fig_prod, use_container_width=True)


with col2:
    st.markdown("### 👥 Top Customers")

    fig_cust = px.bar(
        top_customers.sort_values(by="Sales"),
        x="Sales",
        y="Customer Name",
        orientation='h'
    )

    fig_cust.update_layout(
        template="plotly_dark",
        height=500,
        title="Top Customers by Sales",
        title_x=0.3
    )

    st.plotly_chart(fig_cust, use_container_width=True)


# -----------------------------
# PROFIT vs LOSS
# -----------------------------
st.markdown("---")
st.markdown("## 📉 Profit Analysis")

profit_df = (
    filtered_df
    .groupby('Sub-Category')['Profit']
    .sum()
    .reset_index()
)

fig_profit = px.bar(
    profit_df,
    x="Profit",
    y="Sub-Category",
    orientation='h',
    color="Profit",
    color_continuous_scale=["red", "green"]
)

fig_profit.update_layout(
    template="plotly_dark",
    height=500,
    title="Profit / Loss by Sub-Category",
    title_x=0.3
)

st.plotly_chart(fig_profit, use_container_width=True)


# -----------------------------
# Business Insights
# -----------------------------

st.markdown("## 🧠 AI-Generated Business Insights")

# Top region contribution
region_sales = filtered_df.groupby("Region")["Sales"].sum()
top_region = region_sales.idxmax()
region_share = (region_sales.max() / region_sales.sum()) * 100

# Highest profit category
category_profit = filtered_df.groupby("Category")["Profit"].sum()
top_category = category_profit.idxmax()

# Loss-making sub-category
sub_profit = filtered_df.groupby("Sub-Category")["Profit"].sum()

# Insights display
st.info(f"🌍 **{top_region}** region contributes **{region_share:.1f}%** of selected revenue.")
st.success(f"📈 **{top_category}** category has the highest total profit.")

if (sub_profit < 0).any():
    loss_sub = sub_profit.idxmin()
    st.warning(f"⚠ **{loss_sub}** sub-category shows the highest loss and may need attention.")


# -----------------------------
# Download Report
# -----------------------------

st.markdown("---")
st.markdown("### 📥 Download Report")

csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name='sales_report.csv',
    mime='text/csv',
)



st.markdown("---")
st.caption("Sales Intelligence Dashboard • Built with Streamlit, Plotly & Python")














