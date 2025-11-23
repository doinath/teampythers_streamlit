import streamlit as st
import plotly.express as px
import pandas as pd


class DataPrepPage:
    """
    Page class for Data Exploration & Preparation.
    Matches the structure required by app_controller.py
    """

    def __init__(self, data_manager):
        # Store the data manager instance
        self.dm = data_manager

    def render(self):
        st.title("🛠️ Data Exploration & Preparation")

        # Get the data from the manager
        # Note: Using get_data() as per the optimized DataManager structure
        df = self.dm.get_data()

        if df is None or df.empty:
            st.error("No data available to analyze.")
            return

        # --- 1. Missing Values Analysis ---
        st.subheader("1. Handling Missing Values")

        # Calculate missing values directly here to be robust
        missing = df.isnull().sum()
        missing = missing[missing > 0]  # Only show columns with actual missing data

        col1, col2 = st.columns([1, 2])

        with col1:
            if not missing.empty:
                st.write("Missing values count per column:")
                st.dataframe(missing)
            else:
                st.success("✅ No missing values found! The dataset has been cleaned by the DataManager pipeline.")

        with col2:
            if not missing.empty:
                # Visualization of completeness
                fig = px.bar(
                    x=missing.index,
                    y=missing.values,
                    labels={'x': 'Columns', 'y': 'Null Count'},
                    title="Data Gap Analysis",
                    color=missing.values,
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Show a "Perfect Score" chart if data is clean
                st.info("Visualizing Clean Data Integrity:")
                dummy_data = pd.DataFrame({'Status': ['Filled', 'Missing'], 'Count': [len(df), 0]})
                fig = px.pie(dummy_data, names='Status', values='Count',
                             color='Status',
                             color_discrete_map={'Filled': '#2E8B57', 'Missing': 'red'},
                             hole=0.6)
                st.plotly_chart(fig, use_container_width=True)

        st.info(
            "ℹ️ **Cleaning Strategy:** Rows with missing dates were dropped. "
            "Numeric gaps (prices, coordinates) were filled using Median Imputation. "
            "Categorical gaps were marked as 'Unknown'."
        )

        st.divider()

        # --- 2. Distributions ---
        st.subheader("2. Categorical Distributions")

        col_a, col_b = st.columns(2)

        with col_a:
            st.caption("Distribution of Commodities")
            # Safety check: Ensure commodity column exists
            if 'commodity' in df.columns:
                top_comm = df['commodity'].value_counts().head(10)
                fig_comm = px.pie(names=top_comm.index, values=top_comm.values, hole=0.4, title="Top 10 Commodities")
                st.plotly_chart(fig_comm, use_container_width=True)
            else:
                st.warning("Column 'commodity' not found.")

        with col_b:
            st.caption("Retail vs Wholesale Records")
            # Safety check: Ensure pricetype column exists
            if 'pricetype' in df.columns:
                fig_type = px.bar(
                    df['pricetype'].value_counts(),
                    orientation='h',
                    color_discrete_sequence=['#2E8B57'],
                    title="Market Type Count"
                )
                fig_type.update_layout(showlegend=False, xaxis_title="Count", yaxis_title="Price Type")
                st.plotly_chart(fig_type, use_container_width=True)
            else:
                st.warning("Column 'pricetype' not found.")