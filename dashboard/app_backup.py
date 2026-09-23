import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Olist E-Commerce Analytics", layout="wide")

st.title("📊 Olist E-Commerce Analytics Dashboard")

# Load data
merged = pd.read_csv('merged_data.csv')
rfm = pd.read_csv('rfm_data.csv')
delivery_review = pd.read_csv('delivery_review_data.csv')

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

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue (BRL)", f"{merged['price'].sum():,.0f}")
col2.metric("Total Orders", merged['order_id'].nunique())
col3.metric("Avg Review Score", f"{delivery_review['review_score'].mean():.2f}")

st.subheader("Customer Segments (RFM)")
segment_counts = rfm['Segment'].value_counts()
st.bar_chart(segment_counts)

st.subheader("Top Product Categories by Revenue")
top_categories = merged.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_categories)


