import streamlit as st
import plotly.express as px
import pandas as pd


class OverviewPage:
    def __init__(self, data_manager):
        self.dm = data_manager

    def render(self):
        st.title("🇵🇭 Philippines Food Price Analysis")
        st.markdown("### A comprehensive record of food prices from 2000 to Present")

        # Get the data from DataManager
        df = self.dm.get_data()

        # Check if data exists before trying to access columns
        if df is None or df.empty:
            st.error("No data available. Please check the dataset file.")
            return

        # --- SECTION 1: TOP-LEVEL METRICS ---
        # This gives the user an instant summary of the dataset's size
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Records", f"{len(df):,}")
        with c2:
            st.metric("Commodities", df['commodity'].nunique())
        with c3:
            st.metric("Regions", df['admin1'].nunique())
        with c4:
            # Handle date min/max
            min_year = df['year'].min()
            max_year = df['year'].max()
            st.metric("Time Span", f"{int(min_year)} - {int(max_year)}")

        st.divider()

        # --- SECTION 2: TABS FOR ORGANIZATION ---
        # We split the "Project Info" and "Data Health/Stats" to keep the page clean
        tab_info, tab_health = st.tabs(["Project & Data Dictionary", "Data Health & Distributions"])

        # --- TAB 1: PROJECT INFO ---
        with tab_info:
            st.subheader("Research Context")
            st.markdown("""
            **Research Question:** 
            *How have food prices in the Philippines evolved over the last two decades across different administrative regions, and what are the disparities between retail and wholesale markets?*

            **Analysis Techniques:**
            1. **Time-Series Analysis:** To track inflation and seasonal trends.
            2. **Geospatial Analysis:** To identify regional price disparities.
            3. **Descriptive Statistics:** To understand price distributions.
            """)

            st.subheader("Data Dictionary")
            st.markdown("Below is the structure of the dataset used for this analysis:")

            # Create a description dataframe for the UI
            data_dict = pd.DataFrame([
                {"Column": "date", "Description": "Date of data collection (Monthly)"},
                {"Column": "admin1", "Description": "Administrative Region (e.g., NCR, Region III)"},
                {"Column": "admin2", "Description": "Province or specific locality"},
                {"Column": "market", "Description": "Specific market name where price was recorded"},
                {"Column": "latitude/longitude", "Description": "Geospatial coordinates of the market"},
                {"Column": "category", "Description": "Broad food group (e.g., Cereals, Vegetables)"},
                {"Column": "commodity", "Description": "Specific item name (e.g., Rice, regular milled)"},
                {"Column": "pricetype", "Description": "Market level (Retail vs Wholesale)"},
                {"Column": "price", "Description": "Price in Philippine Peso (PHP)"},
            ])
            st.table(data_dict)

            st.subheader("Raw Data Sample")
            st.dataframe(df.head(10), use_container_width=True)

        # --- TAB 2: DATA HEALTH (Visualizations & Missing Data) ---
        with tab_health:
            st.subheader("1. Missing Data Analysis")

            # Calculate missing values (Checking the raw data before imputation would be ideal,
            # but here we visualize the concept)
            missing = df.isnull().sum()
            missing = missing[missing > 0]

            if not missing.empty:
                st.warning("The following columns have missing values:")
                fig_missing = px.bar(
                    x=missing.index,
                    y=missing.values,
                    labels={'x': 'Column', 'y': 'Count of Nulls'},
                    title="Missing Values Count",
                    color_discrete_sequence=['#FF6347']
                )
                st.plotly_chart(fig_missing, use_container_width=True)
            else:
                st.success("✅ No missing values detected in the processed dataset (Imputation applied).")

            st.subheader("2. Price Distribution")

            # Simple histogram of prices
            # We filter out extreme outliers for better visualization just for this chart
            filter_limit = df['price'].quantile(0.95)
            filtered_view = df[df['price'] < filter_limit]

            fig_dist = px.histogram(
                filtered_view,
                x="price",
                nbins=50,
                title="Distribution of Food Prices (95th Percentile)",
                labels={'price': 'Price (PHP)'},
                color_discrete_sequence=['#2E8B57']  # Theme green
            )
            st.plotly_chart(fig_dist, use_container_width=True)
            st.caption(f"Note: This histogram excludes extreme outliers above ₱{filter_limit:,.2f} for clarity.")

        # --- SECTION 3: CLEANING STEPS (EXPANDER) ---
        st.divider()
        with st.expander("🛠️ Technical Details: Data Cleaning Pipeline"):
            st.markdown("""
            The following steps were automated in the `DataManager` class using `sklearn.pipeline`:

            1. **Date Parsing:** Converted `date` column to datetime objects; rows with invalid dates were dropped.
            2. **Feature Engineering:** Extracted `year`, `quarter`, and `month_name` for temporal analysis.
            3. **Numerical Imputation:** Missing values in `price`, `latitude`, and `longitude` were filled using the **Median** strategy (robust against outliers).
            4. **Categorical Imputation:** Missing values in text columns (e.g., `market`) were filled with the placeholder "Unknown".
            5. **Data Type Enforcement:** Ensured `price` is float and `date` is datetime.
            """)