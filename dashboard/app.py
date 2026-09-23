import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Olist E-Commerce Analytics", layout="wide")
st.markdown("""
<style>
    .stApp {
        background-color: #0E1621;
        color: white;
    }

    [data-testid="stSidebar"] {
        background-color: #09111A;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetric"] {
        background-color: #162333;
        border: 1px solid #263B52;
        padding: 18px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #AEB8C4;
    }

    [data-testid="stMetricValue"] {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Olist E-Commerce Analytics Dashboard")

# Load data
merged = pd.read_csv('dashboard/merged_data.csv')
rfm = pd.read_csv('dashboard/rfm_data.csv')
delivery_review = pd.read_csv('dashboard/delivery_review_data.csv')

# Date filter
merged['order_purchase_timestamp'] = pd.to_datetime(
    merged['order_purchase_timestamp']
)

min_date = merged['order_purchase_timestamp'].min().date()
max_date = merged['order_purchase_timestamp'].max().date()

date_range = st.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range

    merged = merged[
        (merged['order_purchase_timestamp'].dt.date >= start_date) &
        (merged['order_purchase_timestamp'].dt.date <= end_date)
    ]

# Sidebar filters
st.sidebar.header("Filters")

# State filter
states = ["All"] + sorted(merged["customer_state"].dropna().unique().tolist())
selected_state = st.sidebar.selectbox("Select State", states)

if selected_state != "All":
    merged = merged[merged["customer_state"] == selected_state]

# Product category filter
categories = ["All"] + sorted(merged["product_category_name"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)

if selected_category != "All":
    merged = merged[merged["product_category_name"] == selected_category]

# De-duplicated item-level data (prevents revenue inflation from multiple payment installments)
items = merged.drop_duplicates(subset=["order_id", "order_item_id"])

# De-duplicated payment-level data (prevents payment value inflation from multiple order items)
payments_unique = merged.drop_duplicates(subset=["order_id", "payment_sequential"])

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Revenue",
    f"R$ {merged['price'].sum():,.0f}"
)

col2.metric(
    "🛒 Total Orders",
    f"{merged['order_id'].nunique():,}"
)

col3.metric(
    "👥 Customers",
    f"{merged['customer_unique_id'].nunique():,}"
)

col4.metric(
    "⭐ Avg Review Score",
    f"{delivery_review['review_score'].mean():.2f}"
)

st.subheader("Customer Segments (RFM)")
segment_counts = rfm['Segment'].value_counts()
fig = px.bar(
    segment_counts,
    x=segment_counts.index,
    y=segment_counts.values,
    labels={"x": "Customer Segment", "y": "Number of Customers"},
    title="Customer Segments (RFM)"
)

fig.update_layout(
    template="plotly_dark",
    height=450,
    xaxis_title="Customer Segment",
    yaxis_title="Number of Customers"
)

st.plotly_chart(fig, use_container_width="stretch")

st.subheader("Top Product Categories by Revenue")
top_categories = merged.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_categories)
st.subheader("Revenue Trend")

sales_trend = (
    merged.groupby(merged["order_purchase_timestamp"].dt.to_period("M"))["price"]
    .sum()
    .reset_index()
)

sales_trend["order_purchase_timestamp"] = (
    sales_trend["order_purchase_timestamp"].astype(str)
)

fig = px.line(
    sales_trend,
    x="order_purchase_timestamp",
    y="price",
    markers=True,
    labels={
        "order_purchase_timestamp": "Month",
        "price": "Revenue (BRL)"
    },
    title="Monthly Revenue Trend"
)

fig.update_layout(
    template="plotly_dark",
    height=450
)

st.plotly_chart(fig, width="stretch")

# Revenue by State
# Revenue by State
st.subheader("Revenue by State")

state_revenue = (
    merged.groupby("customer_state")["price"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

state_revenue["Revenue_Label"] = state_revenue["price"].apply(
    lambda x: f"R$ {x/1_000_000:.2f}M"
)

fig_state = px.bar(
    state_revenue,
    x="price",
    y="customer_state",
    orientation="h",
    text="Revenue_Label",
    labels={
        "customer_state": "State",
        "price": "Revenue (BRL)"
    },
    title="Top 10 States by Revenue"
)

fig_state.update_traces(
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Revenue: R$ %{x:,.0f}<extra></extra>"
)

fig_state.update_layout(
    template="plotly_dark",
    height=450,
    xaxis_title="Revenue (BRL)",
    yaxis_title="State",
    yaxis=dict(categoryorder="total ascending"),
    margin=dict(l=20, r=80, t=60, b=40)
)

st.plotly_chart(
    fig_state,
    width="stretch",
    key="revenue_by_state"
)
# Payment Method Analysis
st.subheader("Payment Method Analysis")

payment_data = (
    payments_unique.groupby("payment_type")["payment_value"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
payment_data["Revenue_Label"] = payment_data["payment_value"].apply(
    lambda x: f"R$ {x/1_000_000:.2f}M"
)

fig_payment = px.bar(
    payment_data,
    x="payment_type",
    y="payment_value",
    text="Revenue_Label",
    labels={
        "payment_type": "Payment Method",
        "price": "Revenue (BRL)"
    },
    title="Revenue by Payment Method"
)

fig_payment.update_layout(
    template="plotly_dark",
    height=400,
    margin=dict(l=20, r=40, t=60, b=40)
)

st.plotly_chart(
    fig_payment,
    width="stretch",
    key="payment_method_revenue"
)
