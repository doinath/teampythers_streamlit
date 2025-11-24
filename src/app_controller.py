import streamlit as st
import os

# Import the Data Manager
from src.data_manager import DataManager

# Import UI Pages
# Note: Ensure these files exist in src/pages/ with the corresponding class names
from src.pages import overview_01, data_prep_02, analysis_03, conclusions_04


class StreamlitApp:
    def __init__(self):
        # 1. Page Configuration MUST be the first Streamlit command
        st.set_page_config(
            page_title="Team Pythers | Food Prices",
            page_icon="🌾",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # 2. Initialize Data Manager (The Model)
        # Using the specific file name you provided
        self.data_manager = DataManager('data/wfp_food_prices_phl.csv')

        # 3. Initialize Pages (The Views)
        # We instantiate the classes here and pass the data_manager instance to them
        self.pages = {
            '01 Overview': overview_01.OverviewPage(self.data_manager),
            '02 Data Preparation': data_prep_02.DataPrepPage(self.data_manager),
            '03 Analysis': analysis_03.AnalysisPage(self.data_manager),
            '04 Conclusions': conclusions_04.ConclusionsPage(self.data_manager)
        }

    def run(self):
        """
        The main execution method.
        Sets up the styling, sidebar, and renders the selected page.
        """

        # Inject Custom CSS
        # Adjusted path to match your structure: assets/css/styles.css
        self.inject_css('assets/css/styles.css')

        # Sidebar Navigation
        with st.sidebar:
            st.title("Team Pythers")
            st.caption("Philippine Food Price Analysis")
            st.markdown("---")

            # Using radio button for cleaner navigation look
            selection = st.radio(
                "Go to Section",
                list(self.pages.keys()),
                index=0
            )

            st.markdown("---")
            st.info("Data Source: WFP (2000-Present)")

        # Render the selected page
        page = self.pages[selection]
        page.render()

    def inject_css(self, css_file_path):
        """Helper function to load and inject custom CSS."""
        try:
            # Check if file exists first to avoid crashing
            if os.path.exists(css_file_path):
                with open(css_file_path, 'r') as f:
                    css_content = f.read()
                    st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
            else:
                # Warning instead of error so the app still runs without styles
                st.warning(f"⚠️ CSS file not found at: {css_file_path}")

        except Exception as e:
            st.error(f"Error loading CSS: {e}")