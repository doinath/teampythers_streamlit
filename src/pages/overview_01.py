import streamlit as st
import plotly.express as px
import pandas as pd


class OverviewPage:
    def __init__(self, data_manager):
        self.dm = data_manager

    def render(self):
        st.title("🇵🇭 Philippine Food Price Analysis")
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
        tab_info, tab_health, tab_team = st.tabs(["Project & Data Dictionary", "Data Health & Distributions", "Meet the Team"])

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

                # --- HISTOGRAM CODE ---
                st.subheader("2. Price Distribution Analysis")

                # We filter out extreme outliers for better visualization (95th percentile)
                filter_limit = df['price'].quantile(0.95)
                filtered_view = df[df['price'] < filter_limit]

                # Create a Histogram with a Box Plot on top (Marginal)
                fig_dist = px.histogram(
                    filtered_view,
                    x="price",
                    nbins=60,  # More bins for detail
                    marginal="box",  # Adds the Box Plot at the top
                    title="<b>Distribution of Food Prices</b> (PHP)",
                    labels={'price': 'Price (PHP)', 'count': 'Frequency'},
                    color_discrete_sequence=['#537B2F'],  # Your Primary Green
                    opacity= 1  # Slight transparency
                )

                # Apply the "Glass/Clean" Theme to the Chart
                fig_dist.update_layout(
                    plot_bgcolor="#FFFFFF",  # <--- Solid White Plot Area
                    paper_bgcolor="#FFFFFF",  # <--- Solid White Surrounding Area
                    bargap=0.2,  # Spacing between bars
                    font=dict(color="#2D5128"),  # Dark Green font
                    title_font_size=18,

                    # Clean up the Axes
                    xaxis=dict(
                        showgrid=False,
                        title_font=dict(size=14, weight='bold')
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(128,128,128,0.2)',  # Faint grid lines
                        title_font=dict(size=14, weight='bold')
                    ),
                    showlegend=False,
                    margin = dict(l=20, r=20, t=50, b=20),
                )

                # Custom Hover Template
                fig_dist.update_traces(
                    hovertemplate="<b>Price:</b> ₱%{x:.2f}<br><b>Count:</b> %{y}"
                )

                st.plotly_chart(fig_dist, use_container_width=True)

                st.caption(
                    f"ℹ️ **Note:** The chart focuses on the main cluster of prices (0 - ₱{filter_limit:,.0f}). Extreme outliers (top 5%) are excluded for clarity.")

                # --- TAB 3: MEET THE TEAM (Pure Streamlit) ---
                with tab_team:
                    st.subheader("1. Development Team")
                    st.write("This project is a collaborative effort by the following members:")

                    # 1. Define Team Data
                    # Note: For images, place files in 'assets/images/'.
                    # If files don't exist, the code handles it gracefully.
                    team = [
                        {"name": "Julian Ramil Andales", "role": "Data Analyst", "photo": "julian.png"},
                        {"name": "Nathanael Jedd del Castillo", "role": "Developer", "photo": "nate.png"},
                        {"name": "Sherielyn Guadiana", "role": "Data Analyst", "photo": "sherielyn.png"},
                        {"name": "Kyle Plando", "role": "Data Analyst", "photo": "kyle.png"},
                        {"name": "Shervin Dale Tabernero", "role": "Developer", "photo": "shervin.png"},
                    ]

                    # 2. Create Layout (5 Columns)
                    cols = st.columns(len(team))

                    # 3. Render Cards
                    for i, member in enumerate(team):
                        with cols[i]:
                            # Create a Card Container with a border
                            with st.container(border=True):
                                # PROFILE PICTURE
                                # Construct the path relative to the root folder
                                image_path = f"assets/images/{member['photo']}"

                                # Load the local image
                                # We use width="stretch" to fix the warning and fill the circle
                                st.image(image_path, width="stretch")

                                # NAME & ROLE
                                st.markdown(f"**{member['name']}**")
                                st.caption(member['role'])

                    st.divider()

                    # 4. Academic Context Section
                    st.subheader("2. Academic Context")

                    # Create a styled container for Academic Info
                    with st.container(border=True):
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