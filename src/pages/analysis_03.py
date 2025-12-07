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

warnings.filterwarnings("ignore", category=ConvergenceWarning)


class AnalysisPage:
    def __init__(self, data_manager):
        self.dm = data_manager

    def render(self):
        st.title(" Consolidated Market Analysis Dashboard")

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


@st.cache_data
def _clean_data(df):
    """
    Cleans the WFP dataset format once and caches the clean result.
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    numeric_cols = ['price', 'usdprice', 'latitude', 'longitude']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['date', 'price', 'latitude', 'longitude'], inplace=True)
    return df


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


@st.cache_data
def _run_k_means_and_merge(filtered_df: pd.DataFrame, num_clusters: int):
    """
    K-Means: Runs feature aggregation, clustering, and merges results.
    Feature aggregation is now inside the cached function.
    """

    market_features = filtered_df.groupby(['market', 'admin1']).agg({
        'price': ['mean', 'std'],
        'latitude': 'first',
        'longitude': 'first'
    }).reset_index()
    market_features.columns = ['market', 'region', 'avg_price', 'volatility', 'lat', 'lon']
    market_features = market_features.dropna()

    if len(market_features) < num_clusters:
        return None, None, "⚠️ Not enough data points to generate clusters. Adjust filters."

    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    market_features['Cluster'] = kmeans.fit_predict(market_features[['avg_price', 'volatility']])
    market_features['Cluster'] = "Group " + market_features['Cluster'].astype(str)

    merged_df = filtered_df.merge(market_features[['market', 'Cluster']], on='market')

    return market_features, merged_df, None


@st.cache_data
def _run_em_clustering(df_comm: pd.DataFrame, n_clusters: int):
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


@st.cache_data
def _run_apriori_analysis(df: pd.DataFrame, commodities_list: list, scope: str, min_support: float,
                          min_confidence: float):
    """
    UPDATED Apriori: Runs association rule mining with adjustable scope.
    Scope determines how the 'item' is defined (market-specific vs. global commodity).
    """
    if not commodities_list:
        return [], "Please select at least one commodity."

    df_ap = df[df['pricetype'] == 'Retail'].dropna(subset=['price', 'commodity', 'market']).copy()
    df_ap = df_ap[df_ap['commodity'].isin(commodities_list)]

    if df_ap.empty:
        return [], "No retail data found for the selected commodities."

    def categorize_price(x):
        if len(x) < 5: return pd.Series([np.nan] * len(x), index=x.index)
        q3 = x.quantile(0.75)
        return x.apply(lambda p: 'High Price' if p >= q3 else 'Normal')

    df_ap['status'] = df_ap.groupby(['market', 'commodity'])['price'].transform(categorize_price)
    df_high = df_ap[df_ap['status'] == 'High Price'].copy()

    if scope == "Market-Specific (Cross-Market/Cross-Commodity)":

        df_high['item'] = df_high['commodity'] + " is High in " + df_high['market']

    elif scope == "Cross-Commodity (Generalized)":

        df_high['item'] = df_high['commodity'] + " is High"

    else:
        return [], "Invalid analysis scope selected."

    if df_high.empty:
        return [], "No 'High Price' data points available for association mining after filtering."

    transactions = df_high.groupby('date')['item'].apply(lambda x: list(set(x))).tolist()
    N = len(transactions)

    transactions = [t for t in transactions if len(t) >= 2]
    N_filtered = len(transactions)

    if N_filtered < 10:
        return [], f"Insufficient daily transactions ({N_filtered}) where two or more items are 'High Price' simultaneously. Try adjusting filters or reducing thresholds."

    item_counts = {}
    for trans in transactions:
        for item in trans:
            item_counts[item] = item_counts.get(item, 0) + 1
    frequent_1 = {k: v for k, v in item_counts.items() if v / N_filtered >= min_support}

    pair_counts = {}
    for trans in transactions:
        freq_items_in_trans = [i for i in trans if i in frequent_1]
        for pair in combinations(sorted(freq_items_in_trans), 2):
            pair_counts[pair] = pair_counts.get(pair, 0) + 1
    frequent_2 = {k: v for k, v in pair_counts.items() if v / N_filtered >= min_support}

    results = []
    for pair, count in frequent_2.items():
        item_A, item_B = pair
        support_AB = count / N_filtered

        support_A = frequent_1[item_A] / N_filtered
        conf_A_to_B = support_AB / support_A
        lift_A_to_B = conf_A_to_B / (frequent_1[item_B] / N_filtered)
        if conf_A_to_B >= min_confidence:
            results.append((item_A, item_B, conf_A_to_B, lift_A_to_B))

        support_B = frequent_1[item_B] / N_filtered
        conf_B_to_A = support_AB / support_B
        lift_B_to_A = conf_B_to_A / (frequent_1[item_A] / N_filtered)
        if conf_B_to_A >= min_confidence:

            if (item_B, item_A, conf_B_to_A, lift_B_to_A) not in results:
                results.append((item_B, item_A, conf_B_to_A, lift_B_to_A))

    results.sort(key=lambda x: x[3], reverse=True)

    formatted_results = []
    for r in results:
        ant = _add_region_label(r[0]) if "Market-Specific" in scope else r[0]
        con = _add_region_label(r[1]) if "Market-Specific" in scope else r[1]
        formatted_results.append((ant, con, r[2], r[3]))

    return formatted_results, f"Rules found: {len(formatted_results)}. Base Transactions: {N_filtered}. Support: {min_support}, Confidence: {min_confidence}"


def render_sherielyn_analysis(dm):
    """Renders Sherielyn's K-Means clustering analysis."""
    st.header("1. K-Means Market Segmentation")

    df_raw = dm.get_data()

    df = _clean_data(df_raw)

    if df.empty:
        st.error("Data not available.")
        return

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

    default_start_date = max_date - pd.DateOffset(years=1) if pd.notnull(max_date) and max_date > min_date else min_date

    with colC:
        start_date = st.date_input("Start Date:", default_start_date, key='s_start_date')

    with colD:
        end_date = st.date_input("End Date:", max_date, key='s_end_date')

    st.markdown("---")

    mask = (
            (df['commodity'] == selected_commodity) &
            (df['pricetype'] == selected_pricetype) &
            (df['date'] >= pd.to_datetime(start_date)) &
            (df['date'] <= pd.to_datetime(end_date))
    )
    if selected_region != "All Regions":
        mask = mask & (df['admin1'] == selected_region)
    filtered_df = df.loc[mask].copy()

    if st.button(f"Run K-Means Analysis (k={num_clusters})", key='run_kmeans_btn'):

        if filtered_df.empty:
            st.warning("⚠️ No data matches the current filters. Adjust filters and try again.")
            return

        st.markdown(
            f"*Target:* **{selected_commodity}** ({selected_pricetype}) | *Algorithm:* K-Means Clustering (**k={num_clusters}**)")

        market_features_clustered, merged_df, error_msg = _run_k_means_and_merge(
            filtered_df, num_clusters
        )

        if error_msg:
            st.warning(error_msg)
            return

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
    """Renders Plando's EM Clustering and Comparative Analysis."""
    st.header("2. EM Clustering & Comparative Analysis")

    df_raw = dm.get_data()

    df_cleaned = _clean_data(df_raw)

    df = df_cleaned.rename(
        columns={'admin1': 'region', 'commodity': 'commodity', 'price': 'price_php', 'date': 'date'}).copy()

    if df.empty:
        st.error("Data not available.")
        return

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

    tab1, tab2 = st.tabs(["Price Trend Over Time", "EM Clustering Segments"])

    with tab1:
        st.subheader("Historical Price Trend")

        df_comp = df_comm.copy()
        df_comp['month_year'] = df_comp['date'].dt.to_period('M')
        monthly_avg = df_comp.groupby('month_year')['price_php'].mean().reset_index(name='avgPrice')
        monthly_avg['date_for_plot'] = monthly_avg['month_year'].dt.to_timestamp()

        PLOT_BG_COLOR = "#1E2D22"
        TICK_LABEL_COLOR = "#E4EB9C"
        TITLE_COLOR = "#537B2F"
        GRID_COLOR = "#3A4A3A"

        fig, ax = plt.subplots(figsize=(9, 5))

        fig.patch.set_facecolor(PLOT_BG_COLOR)
        ax.set_facecolor(PLOT_BG_COLOR)

        sns.lineplot(x='date_for_plot', y='avgPrice', data=monthly_avg, marker='o', color='#90ce24', ax=ax)

        ax.set_title(
            f'Avg Monthly Price Trend for {selected_commodity} (PHP)',
            color=TICK_LABEL_COLOR
        )
        ax.set_xlabel('Date', color=TICK_LABEL_COLOR)
        ax.set_ylabel('Average Price (PHP/Unit)', color=TICK_LABEL_COLOR)

        ax.tick_params(axis='x', colors=TICK_LABEL_COLOR)
        ax.tick_params(axis='y', colors=TICK_LABEL_COLOR)

        ax.spines['bottom'].set_color(TICK_LABEL_COLOR)
        ax.spines['top'].set_color(TICK_LABEL_COLOR)
        ax.spines['left'].set_color(TICK_LABEL_COLOR)
        ax.spines['right'].set_color(TICK_LABEL_COLOR)

        ax.grid(True, linestyle='--', alpha=0.6, color=GRID_COLOR)


        plt.xticks(rotation=45)
        plt.tight_layout()

        st.pyplot(fig, use_container_width=True)
        st.info("This chart shows the historical average price trend. No forecasting model is applied here.")
    with tab2:
        st.subheader(f"Regional Clustering (Gaussian Mixture Model, k={n_clusters})")

        regional_features, cluster_info = _run_em_clustering(df_comm, n_clusters)

        if regional_features is None:
            st.warning(cluster_info)
            return

        st.info(cluster_info)

        PLOT_BG_COLOR = "#1E2D22"
        TICK_LABEL_COLOR = "#E4EB9C"
        GRID_COLOR = "#3A4A3A"

        fig_cluster, ax_cluster = plt.subplots(figsize=(9, 5))


        fig_cluster.patch.set_facecolor(PLOT_BG_COLOR)

        ax_cluster.set_facecolor(PLOT_BG_COLOR)

        sns.scatterplot(
            x='avg_price', y='std_price', data=regional_features,
            hue='cluster', palette='Set1', style='cluster', s=100, ax=ax_cluster
        )

        for i in range(regional_features.shape[0]):
            ax_cluster.text(
                regional_features['avg_price'][i] * 1.01,
                regional_features['std_price'][i] * 1.01,
                regional_features['region'][i],
                fontsize=8,
                color=TICK_LABEL_COLOR
            )

        ax_cluster.set_title(
            f'Regional Price Segments for {selected_commodity}',
            color=TICK_LABEL_COLOR
        )
        ax_cluster.set_xlabel('Average Price (PHP)', color=TICK_LABEL_COLOR)
        ax_cluster.set_ylabel('Price Volatility (Standard Deviation)', color=TICK_LABEL_COLOR)

        # Set tick colors
        ax_cluster.tick_params(axis='x', colors=TICK_LABEL_COLOR)
        ax_cluster.tick_params(axis='y', colors=TICK_LABEL_COLOR)

        ax_cluster.spines['bottom'].set_color(TICK_LABEL_COLOR)
        ax_cluster.spines['top'].set_color(TICK_LABEL_COLOR)
        ax_cluster.spines['left'].set_color(TICK_LABEL_COLOR)
        ax_cluster.spines['right'].set_color(TICK_LABEL_COLOR)

        ax_cluster.grid(True, linestyle='--', alpha=0.6, color=GRID_COLOR)


        plt.tight_layout()

        st.pyplot(fig_cluster, use_container_width=True)
        st.caption("Each point represents a region, grouped by similar average price and volatility.")

def render_julian_analysis(dm):
    """
    Renders Julian's Apriori Association Rule Mining analysis.
    UPDATED: Includes a Scope selector for different rule types.
    """
    st.header("3. Apriori Association Rules")

    df_raw = dm.get_data()

    df = _clean_data(df_raw)

    if df.empty:
        st.error("Data not available.")
        return

    unique_commodities = sorted(df['commodity'].unique().tolist())

    st.subheader("Rule Mining Parameters")
    colA, colB, colC = st.columns([1.5, 1, 1])

    with colA:
        selected_scope = st.radio(
            "Scope of Analysis:",
            [
                "Market-Specific (Cross-Market/Cross-Commodity)",
                "Cross-Commodity (Generalized)"
            ],
            key='j_scope'
        )

    colD, colE = st.columns([1.5, 1.5])
    with colD:
        if "Generalized" in selected_scope:
            commodity_label = "Target Commodities (Select 2+):"
        else:
            commodity_label = "Target Commodities (Select 1+):"

        selected_commodities = st.multiselect(
            commodity_label,
            unique_commodities,
            default=unique_commodities[:2] if len(unique_commodities) >= 2 else unique_commodities,
            key='j_commodities'
        )

    with colE:
        st.markdown("<p style='font-size: 14px; margin-top: 30px;'>Minimum Thresholds:</p>", unsafe_allow_html=True)
        colE1, colE2 = st.columns(2)
        with colE1:
            min_support = st.slider("Min Support:", min_value=0.01, max_value=0.2, value=0.1, key='j_support',
                                    label_visibility="collapsed")
        with colE2:
            min_confidence = st.slider("Min Confidence:", min_value=0.4, max_value=0.9, value=0.5, key='j_confidence',
                                       label_visibility="collapsed")

    st.markdown("---")

    if "Market-Specific" in selected_scope:
        st.info(
            "**Market-Specific:** Rules link specific items in specific markets (e.g., *Rice High in Cebu* $\implies$ *Wheat High in Cebu* OR *Rice High in Iloilo*).")
    else:
        st.info(
            "**Generalized:** Rules link high-price status across all markets (e.g., *Rice is High* $\implies$ *Wheat is High*). Requires 2+ commodities.")

    if st.button("Run Apriori Analysis"):
        st.markdown("### Association Rules Found (High Price Occurrences)")

        if "Generalized" in selected_scope and len(selected_commodities) < 2:
            st.warning("**Generalized Cross-Commodity** analysis requires selecting at least two commodities.")
            return

        results, info = _run_apriori_analysis(df, selected_commodities, selected_scope, min_support, min_confidence)

        st.info(info)

        if not results:
            st.warning(
                "No strong rules found. Try selecting different commodities, switching the Scope, or adjusting the Minimum Support/Confidence thresholds.")
            return

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