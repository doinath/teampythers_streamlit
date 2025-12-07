import streamlit as st
import os

from src.data_manager import DataManager
from src.pages import overview_01, data_prep_02, analysis_03, conclusions_04


class StreamlitApp:
    def __init__(self):

        st.set_page_config(
            page_title="Team Pythers | Food Prices",
            page_icon="🌾",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        self.data_manager = DataManager('data/wfp_food_prices_phl.csv')

        self.pages = {
            '01 Overview': overview_01.OverviewPage(self.data_manager),
            '02 Data Preparation': data_prep_02.DataPrepPage(self.data_manager),
            '03 Analysis': analysis_03.AnalysisPage(self.data_manager),
            '04 Conclusions': conclusions_04.ConclusionsPage(self.data_manager)
        }

    def run(self):
        self.inject_css('assets/css/styles.css')
        self.inject_css('assets/css/analysis.css')

        if "current_page" not in st.session_state:
            st.session_state.current_page = "01 Overview"

        with st.sidebar:
            st.title("Team Pythers")
            st.caption("Philippine Food Price Analysis")
            st.markdown("---")

            st.markdown('**Go to Section**')

            for page_key in self.pages.keys():

                curr = (st.session_state.current_page == page_key)

                if st.button(
                    page_key,
                    key=f'nav_{page_key}',
                    type='primary' if curr else 'secondary',
                    use_container_width=True,
                    on_click=self.set_page,
                    args=(page_key,)
                ):
                    st.session_state.current_page = page_key

            st.markdown("---")
            st.info("Data Source: WFP (2000 - 2023)")


        page = self.pages[st.session_state.current_page]


        page.render()

    def inject_css(self, css_file_path):
        """Helper function to load and inject custom CSS."""
        try:

            if os.path.exists(css_file_path):
                with open(css_file_path, 'r') as f:
                    css_content = f.read()
                    st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
            else:

                st.warning(f"CSS file not found at: {css_file_path}")

        except Exception as e:
            st.error(f"Error loading CSS: {e}")

    def set_page(self, page_key):
        st.session_state.current_page = page_key