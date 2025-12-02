import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.exceptions import ConvergenceWarning
import warnings
from itertools import combinations

# Suppress ConvergenceWarning from sklearn
warnings.filterwarnings("ignore", category=ConvergenceWarning)


# ==========================================
# I. Data Manager Helpers (Assumes DM is separate)
# ==========================================

# NOTE: The _clean_data function should logically reside in your Data Manager
# (or its file). Assuming you need to keep a cached copy of the cleaning logic here
# for the Analysis page to use:
@st.cache_data
def _clean_data(df):
    """
    Cleans the WFP dataset format once and caches the clean result.
    """
    df = df.copy()  # Work on a copy of the raw data
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    numeric_cols = ['price', 'usdprice', 'latitude', 'longitude']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['date', 'price', 'latitude', 'longitude'], inplace=True)
    return df


# Helper to find region from city/market name (Julian's requirement)
CITY_TO_REGION = {
    "Palayan": "Central Luzon", "Davao City": "Davao Region",
    "Iloilo City": "Western Visayas", "Metro Manila": "NCR",
    "Cebu City": "Central Visayas", "Legazpi City": "Bicol Region",
    "Zamboanga City": "Zamboanga Peninsula", "Cagayan de Oro City": "Northern Mindanao"
}


def _add_region_label(text):
    for city, region in CITY_TO_REGION.items():
        if city in text:
            return f"{text} [{region}]"
    return text


# ==========================================
# II. CACHED & HELPER FUNCTIONS
# ==========================================

# --- A. Sherielyn's K-Means Caching (OPTIMIZED) ---
# Now handles feature engineering inside the cache to bundle the heavy work.

@st.cache_data
def _run_k_means_and_merge(filtered_df: pd.DataFrame, num_clusters: int):
    """
    K-Means: Runs feature aggregation, clustering, and merges results.
    Feature aggregation is now inside the cached function.
    """
    # 1. Feature Engineering
    market_features = filtered_df.groupby(['market', 'admin1']).agg({
        'price': ['mean', 'std'],
        'latitude': 'first',
        'longitude': 'first'
    }).reset_index()
    market_features.columns = ['market', 'region', 'avg_price', 'volatility', 'lat', 'lon']
    market_features = market_features.dropna()

    # 2. Check Data Sufficiency
    if len(market_features) < num_clusters:
        return None, None, "⚠️ Not enough data points to generate clusters. Adjust filters."

    # 3. Clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    market_features['Cluster'] = kmeans.fit_predict(market_features[['avg_price', 'volatility']])
    market_features['Cluster'] = "Group " + market_features['Cluster'].astype(str)

    # 4. Merge
    merged_df = filtered_df.merge(market_features[['market', 'Cluster']], on='market')

    return market_features, merged_df, None  # return None for error message if successful


# --- B. Plando's EM Clustering Caching ---

@st.cache_data
def _run_em_clustering(df_comm: pd.DataFrame, n_clusters: int):  # Removed unused 'commodity' arg
    """EM Clustering: Runs Gaussian Mixture Model and returns clustered features."""
    regional_features = df_comm.groupby('region').agg(
        avg_price=('price_php', 'mean'),
        std_price=('price_php', 'std'),
        count=('price_php', 'count')
    ).dropna().reset_index()

    if regional_features.shape[0] < n_clusters or regional_features.shape[0] < 3:
        return None, f"Clustering skipped: Not enough regional data points ({regional_features.shape[0]}) for {n_clusters} clusters."

    X_cluster = regional_features[['avg_price', 'std_price']]
    model = GaussianMixture(n_components=n_clusters, random_state=42)
    pipeline = make_pipeline(StandardScaler(), model)
    pipeline.fit(X_cluster)
    regional_features['cluster'] = pipeline.predict(X_cluster)

    return regional_features, f"Model used: EM Clustering, Components (Clusters) found: {n_clusters}"


# --- C. Julian's Apriori Caching ---

@st.cache_data
def _run_apriori_analysis(df: pd.DataFrame, query: str, min_support: float, min_confidence: float):
    # ... (Apriori function remains unchanged as it is already cached)
    # Data prep specific to Apriori (Discretize Prices)
    # Using 'pricetype' and 'price' column names consistent with the WFP file structure
    df_ap = df[df['pricetype'] == 'Retail'].dropna(subset=['price']).copy()
    df_ap = df_ap[df_ap['commodity'].str.contains(query, case=False)]

    if df_ap.empty:
        return [], "No retail data found for this commodity."

    def categorize_price(x):
        if len(x) < 5: return pd.Series([np.nan] * len(x), index=x.index)
        q3 = x.quantile(0.75)
        return x.apply(lambda p: 'High' if p >= q3 else 'Normal')

    df_ap['status'] = df_ap.groupby(['market', 'commodity'])['price'].transform(categorize_price)
    df_high = df_ap[df_ap['status'] == 'High'].copy()

    if df_high.empty:
        return [], "No 'High Price' data points available for association mining."

    # Create Transactions
    df_high['item'] = df_high['commodity'] + " is High in " + df_high['market']
    transactions = df_high.groupby('date')['item'].apply(list).tolist()
    N = len(transactions)

    # Simplified Apriori logic for 1-itemsets and 2-itemsets
    item_counts = {}
    for trans in transactions:
        for item in set(trans):
            item_counts[item] = item_counts.get(item, 0) + 1
    frequent_1 = {k: v for k, v in item_counts.items() if v / N >= min_support}

    pair_counts = {}
    for trans in transactions:
        freq_items_in_trans = [i for i in trans if i in frequent_1]
        for pair in combinations(sorted(freq_items_in_trans), 2):
            pair_counts[pair] = pair_counts.get(pair, 0) + 1
    frequent_2 = {k: v for k, v in pair_counts.items() if v / N >= min_support}

    # Generate Rules
    results = []
    for pair, count in frequent_2.items():
        item_A, item_B = pair
        support_AB = count / N

        # Rule: A -> B
        support_A = frequent_1[item_A] / N
        conf_A_to_B = support_AB / support_A
        lift_A_to_B = conf_A_to_B / (frequent_1[item_B] / N)
        if conf_A_to_B >= min_confidence:
            results.append((item_A, item_B, conf_A_to_B, lift_A_to_B))

        # Rule: B -> A
        support_B = frequent_1[item_B] / N
        conf_B_to_A = support_AB / support_B
        lift_B_to_A = conf_B_to_A / (frequent_1[item_A] / N)
        if conf_B_to_A >= min_confidence:
            results.append((item_B, item_A, conf_B_to_A, lift_B_to_A))

    results.sort(key=lambda x: x[3], reverse=True)

    # Format results with region labels
    formatted_results = []
    for r in results:
        ant = _add_region_label(r[0])
        con = _add_region_label(r[1])
        formatted_results.append((ant, con, r[2], r[3]))

    return formatted_results, f"Rules found: {len(formatted_results)}. Support: {min_support}, Confidence: {min_confidence}"


# ==========================================
# III. PAGE RENDERER FUNCTIONS
# ==========================================

def render_sherielyn_analysis(dm):
    """
    Renders Sherielyn's K-Means clustering analysis.
    Optimization: Clustering is now button-triggered for lower widget lag.
    """
    st.header("1. 🧩 K-Means Market Segmentation")

    df_raw = dm.get_data()
    # OPTIMIZATION: Use the cached _clean_data function from Section I
    df = _clean_data(df_raw)

    if df.empty:
        st.error("Data not available.")
        return

    # --- Controls for K-Means ---
    st.subheader("Clustering Parameters")
    colA, colB, colC, colD = st.columns([1.5, 1.5, 1, 1])

    with colA:
        unique_regions = sorted(df['admin1'].unique())
        selected_region = st.selectbox("Region Scope:", ["All Regions"] + unique_regions, key='s_region')
        commodities = sorted(df['commodity'].unique())
        selected_commodity = st.selectbox("Commodity:", commodities, key='s_commodity')

    with colB:
        pricetypes = sorted(df['pricetype'].unique())
        selected_pricetype = st.selectbox("Price Type:", pricetypes, key='s_price_type')
        num_clusters = st.slider("Number of Clusters (k):", 2, 5, 3, key='s_k')

    min_date, max_date = df['date'].min(), df['date'].max()

    # OPTIMIZATION: Set a smaller default date range to speed up initial script run
    default_start_date = max_date - pd.DateOffset(years=1) if pd.notnull(max_date) and max_date > min_date else min_date

    with colC:
        start_date = st.date_input("Start Date:", default_start_date, key='s_start_date')

    with colD:
        end_date = st.date_input("End Date:", max_date, key='s_end_date')

    st.markdown("---")

    # --- Data Filtering (Runs on every script rerun, kept minimal) ---
    mask = (
            (df['commodity'] == selected_commodity) &
            (df['pricetype'] == selected_pricetype) &
            (df['date'] >= pd.to_datetime(start_date)) &
            (df['date'] <= pd.to_datetime(end_date))
    )
    if selected_region != "All Regions":
        mask = mask & (df['admin1'] == selected_region)
    filtered_df = df.loc[mask].copy()

    # --- Clustering & Visualization (BUTTON-TRIGGERED OPTIMIZATION) ---
    if st.button(f"Run K-Means Analysis (k={num_clusters})", key='run_kmeans_btn'):

        if filtered_df.empty:
            st.warning("⚠️ No data matches the current filters. Adjust filters and try again.")
            return

        st.markdown(
            f"*Target:* **{selected_commodity}** ({selected_pricetype}) | *Algorithm:* K-Means Clustering (**k={num_clusters}**)")

        # Run the cached function
        market_features_clustered, merged_df, error_msg = _run_k_means_and_merge(
            filtered_df, num_clusters
        )

        if error_msg:
            st.warning(error_msg)
            return

        # Use tabs for visualization (as requested previously)
        tab1, tab2, tab3 = st.tabs(["Scatter & Map", "Time Series Behavior", "Insights"])

        with tab1:
            st.subheader("Cluster Identification & Geography")
            colA_vis, colB_vis = st.columns(2)

            with colA_vis:
                fig_scatter = px.scatter(
                    market_features_clustered, x='avg_price', y='volatility', color='Cluster',
                    hover_name='market', title="Market Segments", template="plotly_white"
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

            with colB_vis:
                fig_map = px.scatter_mapbox(
                    market_features_clustered, lat="lat", lon="lon", color="Cluster",
                    hover_name="market", zoom=4, mapbox_style="carto-positron", title="Cluster Map"
                )
                st.plotly_chart(fig_map, use_container_width=True)

        with tab2:
            st.subheader("Time Series Price Trends by Cluster")
            cluster_time_series = merged_df.groupby(['date', 'Cluster'])['price'].mean().reset_index()
            fig_ts = px.line(cluster_time_series, x='date', y='price', color='Cluster',
                             title=f"Price Trends of Cluster Groups: {selected_commodity}", template="plotly_white")
            st.plotly_chart(fig_ts, use_container_width=True)

        with tab3:
            st.info(
                "K-Means groups markets based on similarity in price and volatility. The maps help confirm regional patterns.")
    else:
        st.info("Click the 'Run K-Means Analysis' button above to start the analysis.")


def render_plando_analysis(dm):
    """
    Renders Plando's EM Clustering and Comparative Analysis.
    Optimization: Matplotlib plotting uses explicit figure/axes objects.
    """
    st.header("2. 📊 EM Clustering & Comparative Analysis")

    df_raw = dm.get_data()
    # OPTIMIZATION: Use the cached _clean_data function from Section I
    df_cleaned = _clean_data(df_raw)

    # Plando's code structure assumes specific renamed columns
    df = df_cleaned.rename(
        columns={'admin1': 'region', 'commodity': 'commodity', 'price': 'price_php', 'date': 'date'}).copy()

    if df.empty:
        st.error("Data not available.")
        return

    # --- Controls for EM Clustering ---
    st.subheader("Analysis Parameters")
    colA, colB = st.columns([1, 1])

    with colA:
        unique_commodities = sorted(df['commodity'].unique().tolist())
        selected_commodity = st.selectbox("Commodity:", unique_commodities, key='p_commodity')

    with colB:
        n_clusters = st.slider("Number of Components (Clusters):", min_value=2, max_value=8, value=4, key='p_k')

    st.markdown("---")

    df_comm = df[df['commodity'] == selected_commodity].copy()

    if df_comm.empty:
        st.warning(f"No data found for {selected_commodity}.")
        return

    # --- Tab 1: Comparative Analysis (Time Series) ---
    tab1, tab2 = st.tabs(["Price Trend Over Time", "EM Clustering Segments"])

    with tab1:
        st.subheader("Historical Price Trend")

        df_comp = df_comm.copy()
        df_comp['month_year'] = df_comp['date'].dt.to_period('M')
        monthly_avg = df_comp.groupby('month_year')['price_php'].mean().reset_index(name='avgPrice')
        monthly_avg['date_for_plot'] = monthly_avg['month_year'].dt.to_timestamp()

        # OPTIMIZATION: Use figure/axes objects explicitly for Matplotlib
        fig, ax = plt.subplots(figsize=(9, 5))

        sns.lineplot(x='date_for_plot', y='avgPrice', data=monthly_avg, marker='o', color='#3498db', ax=ax)

        ax.set_title(f'Avg Monthly Price Trend for {selected_commodity} (PHP)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Average Price (PHP/Unit)')
        ax.grid(True, linestyle='--', alpha=0.6)

        plt.xticks(rotation=45)
        plt.tight_layout()

        st.pyplot(fig, use_container_width=True)  # Use the figure object
        st.info("This chart shows the historical average price trend. No forecasting model is applied here.")

    with tab2:
        st.subheader(f"Regional Clustering (Gaussian Mixture Model, k={n_clusters})")

        # The clustering function is cached
        regional_features, cluster_info = _run_em_clustering(df_comm, n_clusters)

        if regional_features is None:
            st.warning(cluster_info)
            return

        st.info(cluster_info)

        # Plotting Clustering Results (Scatter Plot - Matplotlib)
        fig_cluster, ax_cluster = plt.subplots(figsize=(9, 5))

        sns.scatterplot(
            x='avg_price', y='std_price', data=regional_features,
            hue='cluster', palette='Set1', style='cluster', s=100, ax=ax_cluster
        )

        for i in range(regional_features.shape[0]):
            ax_cluster.text(
                regional_features['avg_price'][i] * 1.01,
                regional_features['std_price'][i] * 1.01,
                regional_features['region'][i],
                fontsize=8
            )
        ax_cluster.set_title(f'Regional Price Segments for {selected_commodity}')
        ax_cluster.set_xlabel('Average Price (PHP)')
        ax_cluster.set_ylabel('Price Volatility (Standard Deviation)')
        plt.tight_layout()

        st.pyplot(fig_cluster, use_container_width=True)  # Use the figure object
        st.caption("Each point represents a region, grouped by similar average price and volatility.")


def render_julian_analysis(dm):
    """Renders Julian's Apriori Association Rule Mining analysis."""
    st.header("3. 🔗 Apriori Association Rules")

    df_raw = dm.get_data()
    # OPTIMIZATION: Use the cached _clean_data function from Section I
    df = _clean_data(df_raw)

    # Check if data is available and extract unique commodities
    if df.empty:
        st.error("Data not available.")
        return

    # Get the unique list of commodities for the dropdown
    unique_commodities = sorted(df['commodity'].unique().tolist())

    # --- Controls for Apriori ---
    st.subheader("Rule Mining Parameters")
    colA, colB, colC = st.columns([1, 1, 1])

    with colA:
        selected_commodity = st.selectbox("Commodity:", unique_commodities, key='j_commodity')
    with colB:
        min_support = st.slider("Minimum Support:", min_value=0.01, max_value=0.2, value=0.1, key='j_support')
    with colC:
        min_confidence = st.slider("Minimum Confidence:", min_value=0.4, max_value=0.9, value=0.5, key='j_confidence')

    st.markdown("---")

    if st.button("Run Apriori Analysis"):
        st.markdown("### Association Rules Found (High Price Occurrences)")

        # Run the cached Apriori analysis
        results, info = _run_apriori_analysis(df, selected_commodity, min_support, min_confidence)

        st.info(info)

        if not results:
            st.warning(
                "No rules found. Try adjusting the Minimum Support, Minimum Confidence, or selecting a different Commodity.")
            return

        # Format and display results in a table
        data_to_display = []
        for ant, con, conf, lift in results[:10]:
            data_to_display.append({
                "Antecedent": ant,
                "Consequent": con,
                "Confidence": f"{conf:.2f}",
                "Lift": f"{lift:.2f}"
            })

        st.dataframe(
            pd.DataFrame(data_to_display),
            hide_index=True,
        )
        st.caption("Showing Top 10 Rules sorted by Lift.")


# ==========================================
# IV. ANALYSIS PAGE CLASS (DISPATCHER)
# ==========================================
class AnalysisPage:
    def __init__(self, data_manager):
        self.dm = data_manager

    def render(self):
        st.title("🔬 Consolidated Market Analysis Dashboard")

        # Create the three tabs for dispatching the analyses
        tab_sherielyn, tab_plando, tab_julian = st.tabs([
            "1. K-Means Clustering",
            "2. EM Clustering & Comparative",
            "3. Apriori Association Rules"
        ])

        with tab_sherielyn:
            render_sherielyn_analysis(self.dm)

        with tab_plando:
            render_plando_analysis(self.dm)

        with tab_julian:
            render_julian_analysis(self.dm)