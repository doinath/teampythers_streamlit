import streamlit as st
import plotly.express as px
import pandas as pd


class DataPrepPage:

    def __init__(self, data_manager):
        self.dm = data_manager

    @st.cache_data(show_spinner="Loading and preparing data...")
    def _get_dataframe(_self):
        """Fetches the processed DataFrame from the DataManager."""
        return _self.dm.get_data()

    @st.cache_data(show_spinner=False)
    def _get_missing_metrics(_self, df: pd.DataFrame):
        """Calculates and caches the missing value Series."""
        missing = df.isnull().sum()
        return missing[missing > 0]

    @st.cache_data(show_spinner="Generating Missing Data chart...")
    def _create_missing_bar_chart(_self, missing: pd.Series, layout: dict):
        """Generates and caches the missing data bar chart."""
        fig = px.bar(
            x=missing.index,
            y=missing.values,
            labels={'x': 'Column Name', 'y': 'Missing Rows'},
            title=" Data Gap Analysis",
            text=missing.values
        )

        fig.update_traces(
            marker_color='#E57373',
            marker_line_color='#D32F2F',
            marker_line_width=1.5,
            textposition='outside'
        )

        fig.update_layout(
            **layout,
            xaxis=dict(showgrid=False, title=None),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        )
        return fig

    @st.cache_data(show_spinner="Analyzing Categorical Distributions...")
    def _create_categorical_charts(_self, df: pd.DataFrame, layout: dict):
        """Generates and caches the commodity and pricetype charts."""
        fig_comm = None
        fig_type = None

        if 'commodity' in df.columns and not df['commodity'].empty:
            top_comm = df['commodity'].value_counts().head(10)
            fig_comm = px.pie(names=top_comm.index, values=top_comm.values, hole=0.4, title="Top 10 Commodities")
            fig_comm.update_layout(**layout)

        if 'pricetype' in df.columns and not df['pricetype'].empty:
            fig_type = px.bar(
                df['pricetype'].value_counts(),
                orientation='h',
                color_discrete_sequence=['#2E8B57'],
                title="Market Type Count"
            )
            fig_type.update_layout(
                **layout,
                showlegend=False,
                xaxis_title="Count",
                yaxis_title="Price Type",
            )
        return fig_comm, fig_type

    @st.cache_data(show_spinner=False)
    def _create_clean_pie_chart(_self, layout: dict):
        """Generates and caches the static 100% clean pie chart."""
        dummy_data = pd.DataFrame({'Status': ['Filled Data', 'Missing'], 'Count': [100, 0]})

        fig = px.pie(
            dummy_data,
            names='Status',
            values='Count',
            hole=0.7,
            title="<b>Dataset Health Score</b>",
            color='Status',
            color_discrete_map={'Filled Data': '#537B2F', 'Missing': '#E0E0E0'}
        )

        fig.update_layout(
            **layout,
            showlegend=False,
            annotations=[dict(
                text='100%<br>CLEAN',
                x=0.5, y=0.5,
                font=dict(size=24, color='#537B2F'),
                showarrow=False,
            )]
        )
        fig.update_traces(hoverinfo='label+percent')
        return fig


    def render(self):
        st.title("Data Exploration & Preparation")

        df = self._get_dataframe()

        if df is None or df.empty:
            st.error("No data available to analyze.")
            return

        st.subheader("1. Handling Missing Values")

        missing = self._get_missing_metrics(df)

        col1, col2 = st.columns([1, 2])

        common_layout = dict(
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(color="#2D5128"),
            title=dict(
                font=dict(
                    size=18,
                    color="#537B2F"
                )
            ),
            margin=dict(l=20, r=20, t=50, b=20),
        )

        with col1:
            if not missing.empty:
                st.write("Missing values count per column:")

                st.dataframe(missing)
            else:
                st.success(" No missing values found! The dataset has been cleaned by the DataManager pipeline.")

        with col2:
            if not missing.empty:

                fig = self._create_missing_bar_chart(missing, common_layout)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Visualizing Data Integrity:")

                fig = self._create_clean_pie_chart(common_layout)
                st.plotly_chart(fig, use_container_width=True)

        st.info(
            " **Cleaning Strategy:** Rows with missing dates were dropped. "
            "Numeric gaps (prices, coordinates) were filled using Median Imputation. "
            "Categorical gaps were marked as 'Unknown'."
        )

        st.divider()

        st.subheader("2. Categorical Distributions")

        fig_comm, fig_type = self._create_categorical_charts(df, common_layout)

        col_a, col_b = st.columns(2)

        with col_a:
            st.caption("Distribution of Commodities")
            if fig_comm:
                st.plotly_chart(fig_comm, use_container_width=True)
            else:
                st.warning("Column 'commodity' not found or is empty.")

        with col_b:
            st.caption("Retail vs Wholesale Records")
            if fig_type:
                st.plotly_chart(fig_type, use_container_width=True)
            else:
                st.warning("Column 'pricetype' not found or is empty.")