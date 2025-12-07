import streamlit as st
import plotly.express as px
import pandas as pd
import base64
import os

class OverviewPage:
    def __init__(self, data_manager):
        self.dm = data_manager

    def render(self):

        st.title("🇵🇭 Philippine Food Price Analysis")
        st.markdown("### A comprehensive record of food prices from 2000 to 2023")

        df = self.dm.get_data()

        if df is None or df.empty:
            st.error("No data available. Please check the dataset file.")
            return

        metrics = self._get_cached_metrics(df)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Records", f"{metrics['total_records']:,}")
        with c2:
            st.metric("Commodities", metrics['commodities'])
        with c3:
            st.metric("Regions", metrics['regions'])
        with c4:
            st.metric("Time Span", metrics['time_span'])

        st.divider()

        tab_info, tab_health, tab_team = st.tabs(
            ["Project & Data Dictionary", "Data Health & Distributions", "Meet the Team"])

        with tab_info:
            st.subheader("Research Context")
            st.markdown("""
            **Research Question:** *How have food prices in the Philippines evolved over the last two decades across different administrative regions, and what are the disparities between retail and wholesale markets?*

            **Analysis Techniques:**
            1. **Time-Series Analysis:** To track inflation and seasonal trends.
            2. **Geospatial Analysis:** To identify regional price disparities.
            3. **Descriptive Statistics:** To understand price distributions.
            """)

            st.subheader("Data Dictionary")
            st.markdown("Below is the structure of the dataset used for this analysis:")

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

            st.divider()
            with st.expander("Technical Details: Data Cleaning Pipeline"):
                st.markdown("""
                        The following steps were automated in the `DataManager` class using `sklearn.pipeline`:

                        1. **Date Parsing:** Converted `date` column to datetime objects; rows with invalid dates were dropped.
                        2. **Feature Engineering:** Extracted `year`, `quarter`, and `month_name` for temporal analysis.
                        3. **Numerical Imputation:** Missing values in `price`, `latitude`, and `longitude` were filled using the **Median** strategy (robust against outliers).
                        4. **Categorical Imputation:** Missing values in text columns (e.g., `market`) were filled with the placeholder "Unknown".
                        5. **Data Type Enforcement:** Ensured `price` is float and `date` is datetime.
                        """)

        with tab_health:
            st.subheader("1. Missing Data Analysis")

            missing = df.isnull().sum()
            missing = missing[missing > 0]

            if not missing.empty:
                st.warning("The following columns have missing values:")

                fig_missing = self._get_cached_missing_data_chart(missing)
                st.plotly_chart(fig_missing, use_container_width=True)
            else:
                st.success("No missing values detected in the processed dataset (Imputation applied).")

                st.subheader("2. Price Distribution Analysis")

                filter_limit = df['price'].quantile(0.95)
                fig_dist = self._get_cached_price_distribution_chart(df, filter_limit)

                st.plotly_chart(fig_dist, use_container_width=True)

                st.caption(
                    f"️ **Note:** The chart focuses on the main cluster of prices (0 - ₱{filter_limit:,.0f}). Extreme outliers (top 5%) are excluded for clarity.")

        with tab_team:
            st.subheader("1. Development Team")
            st.write("This project is a collaborative effort by the following members:")

            team = [
                {"name": "Julian Ramil Andales", "role": "Data Analyst", "photo": "julian.png"},
                {"name": "Nathanael Jedd del Castillo", "role": "Developer", "photo": "nate.png"},
                {"name": "Sherielyn Guadiana", "role": "Data Analyst", "photo": "sherielyn.png"},
                {"name": "Kyle Plando", "role": "Data Analyst", "photo": "kyle.png"},
                {"name": "Shervin Dale Tabernero", "role": "Developer", "photo": "shervin.png"},
            ]

            cols = st.columns(len(team))

            for i, member in enumerate(team):
                with cols[i]:
                    file_path = f"assets/images/{member['photo']}"

                    base64_src = self._get_cached_image_base64(file_path)

                    card_html = f"""
                        <div class="team-card">
                            <img src="{base64_src}" alt="{member['name']}'s photo">
                            <div class="team-name">{member['name']}</div>
                            <div class="team-role">{member['role']}</div>
                        </div>
                        """
                    st.markdown(card_html, unsafe_allow_html=True)

            st.divider()

            st.subheader("2. Academic Context")


            color_container = """
            <style>
            .st-key-my-styled-container {
                background-color: #537B2FFF;
                border-radius: 10px;
                padding: 10px;
                box-shadow: 0px 2px 6px rgba(0,0,0,0.15);
                border: #7ebb48 solid 1px;
            }
            </style>
            """

            st.markdown(color_container, unsafe_allow_html=True)

            with st.container(border=True, key='my-styled-container'):

                c1, c2 = st.columns([1, 2])

                with c1:
                    st.info(" **Course Subject**")
                    st.write("CS365 - Data Analytics and Visualization")

                    st.success(" **Institution**")
                    st.write("Cebu Institute of Technology - University")

                with c2:
                    st.markdown("### Implementation Scope")
                    st.write(
                        "This project serves as the comprehensive implementation of all concepts taught in CS365. It demonstrates the full data pipeline: Extraction, Cleaning, Analysis, and Interactive Visualization.")

                    st.markdown("###  Skills Leveraged")
                    st.write(
                        "The team has incorporated learned skills from the course (Pandas, Plotly, Streamlit) alongside self-taught advanced techniques in CSS styling, software architecture, and geospatial mapping.")


            st.divider()

    @st.cache_data(show_spinner=False)
    def _get_cached_css(_self, file_name):
        """Caches the content of the CSS file, preventing file I/O on every rerun."""
        try:
            with open(file_name) as f:
                return f.read()

        except FileNotFoundError:
            return ""

    @st.cache_data(show_spinner=False)
    def _get_cached_image_base64(_self, file_path):
        """Caches the base64 encoding of a local image file, preventing repeated file reads."""
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()

                return f"data:image/png;base64,{encoded_string}"
            except Exception:
                return ""
        return ""


    @st.cache_data(show_spinner="Calculating top-level metrics...")
    def _get_cached_metrics(_self, df: pd.DataFrame) -> dict:
        """Calculates and caches the top-level summary metrics. FIX: Uses _self."""
        min_year = df['year'].min()
        max_year = df['year'].max()

        return {
            'total_records': len(df),
            'commodities': df['commodity'].nunique(),
            'regions': df['admin1'].nunique(),
            'time_span': f"{int(min_year)} - {int(max_year)}"
        }

    @st.cache_data(show_spinner="Generating Missing Data chart...")
    def _get_cached_missing_data_chart(_self, missing: pd.Series):
        """Generates and caches the missing data bar chart. FIX: Uses _self."""
        return px.bar(
            x=missing.index,
            y=missing.values,
            labels={'x': 'Column', 'y': 'Count of Nulls'},
            title="Missing Values Count",
            color_discrete_sequence=['#FF6347']
        )

    @st.cache_data(show_spinner="Generating Price Distribution chart...")
    def _get_cached_price_distribution_chart(_self, df: pd.DataFrame, filter_limit: float):
        """Generates and caches the price distribution histogram/box plot. FIX: Uses _self."""
        filtered_view = df[df['price'] < filter_limit]

        fig_dist = px.histogram(
            filtered_view,
            x="price",
            nbins=60,
            marginal="box",
            title="<b>Distribution of Food Prices</b> (PHP)",
            labels={'price': 'Price (PHP)', 'count': 'Frequency'},
            color_discrete_sequence=['#537B2F'],
            opacity=1
        )

        fig_dist.update_layout(
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            bargap=0.2,
            font=dict(color="#2D5128"),
            title_font_size=18,
            xaxis=dict(showgrid=False, title_font=dict(size=14)),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)', title_font=dict(size=14)),
            showlegend=False,
            margin=dict(l=20, r=20, t=50, b=20),
        )

        fig_dist.update_traces(hovertemplate="<b>Price:</b> ₱%{x:.2f}<br><b>Count:</b> %{y}")

        return fig_dist

    # def inject_css(self, file_name):
    #     """Loads a local CSS file and injects it into the Streamlit app."""
    #     try:
    #         with open(file_name) as f:
    #             st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    #
    #     except FileNotFoundError:
    #         st.error(f"Error: Could not find '{file_name}'. Ensure it is in the root directory.")