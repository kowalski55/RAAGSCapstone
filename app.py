import streamlit as st
import pandas as pd

# ---------- 1. PAGE CONFIG ----------
st.set_page_config(
    page_title="Sales Insights Dashboard",
    layout="wide",
)

st.title("📊 Sales Data Insights")

# ---------- 2. LOAD DATA ----------
@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv")
    # Ensure Date is datetime
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

st.sidebar.header("Filters")

# ---------- 3. SIDEBAR FILTERS ----------
# Date range filter
min_date = df["Date"].min()
max_date = df["Date"].max()
start_date, end_date = st.sidebar.date_input(
    "Date range", value=(min_date, max_date)
)

# Region filter
regions = ["All"] + sorted(df["Region"].unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)

# Product filter
products = ["All"] + sorted(df["Product"].unique().tolist())
selected_product = st.sidebar.selectbox("Product", products)

# ---------- 4. APPLY FILTERS (defines filtered_df) ----------
mask = df["Date"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))

if selected_region != "All":
    mask &= df["Region"] == selected_region

if selected_product != "All":
    mask &= df["Product"] == selected_product

filtered_df = df[mask]

st.write(f"Showing **{len(filtered_df)}** rows after filters.")

# ---------- 5. TOP-LEVEL METRICS ----------
total_sales = filtered_df["Sales"].sum()
avg_sales = filtered_df["Sales"].mean()

top_product = (
    filtered_df.groupby("Product")["Sales"].sum().idxmax()
    if not filtered_df.empty else "N/A"
)

top_region = (
    filtered_df.groupby("Region")["Sales"].sum().idxmax()
    if not filtered_df.empty else "N/A"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric(
    "Average Sale",
    f"${avg_sales:,.2f}" if not pd.isna(avg_sales) else "N/A"
)
col3.metric("Top Product", top_product)
col4.metric("Top Region", top_region)

st.markdown("---")

# ---------- 6. DATA PREVIEW ----------
with st.expander("🔍 View raw filtered data"):
    st.dataframe(filtered_df)

# ---------- 7. CHARTS ----------
tab1, tab2, tab3 = st.tabs(["Sales over Time", "Sales by Region", "Sales by Product"])

with tab1:
    st.subheader("📈 Sales Over Time")
    if not filtered_df.empty:
        time_series = (
            filtered_df
            .groupby("Date", as_index=False)["Sales"]
            .sum()
            .sort_values("Date")
        )
        st.line_chart(time_series, x="Date", y="Sales")
    else:
        st.info("No data for selected filters.")

with tab2:
    st.subheader("🌍 Sales by Region")
    if not filtered_df.empty:
        region_sales = (
            filtered_df
            .groupby("Region", as_index=False)["Sales"]
            .sum()
            .sort_values("Sales", ascending=False)
        )
        st.bar_chart(region_sales, x="Region", y="Sales")
    else:
        st.info("No data for selected filters.")

with tab3:
    st.subheader("📦 Sales by Product")
    if not filtered_df.empty:
        prod_sales = (
            filtered_df
            .groupby("Product", as_index=False)["Sales"]
            .sum()
            .sort_values("Sales", ascending=False)
        )
        st.bar_chart(prod_sales, x="Product", y="Sales")
    else:
        st.info("No data for selected filters.")
