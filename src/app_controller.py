import streamlit as st 
from src.data_manager import DataManager
from src.pages import overview_01, data_prep_02


class StreamlitApp:
    def __init__(self):
        #self.data_manager = DataManager(data/)
        self.data_manager = DataManager('data/wfp_food_prices_phl.csv')
    
        self.pages = {
            '01_Overview': overview_01.OverviewPage(self.data_manager),
            '02_Data Prep': data_prep_02.DataPrepPage(self.data_manager)
        }
        
    def run(self):
        
        # if multiple css then lets make a run for every single page load and navigation event
        
        st.set_page_config(layout='wide')
        
        self.inject_css('assets/css/styles.css')
        
        st.sidebar.title('Team Pythers Project')
        
        selection = st.sidebar.selectbox('Go to Section', list(self.pages.keys()))
        
        page = self.pages[selection]
        
        page.render()
        
    def inject_css(self, css_file_path):
        """Helper function to load and inject custom CSS."""
        
        try:
            with open(css_file_path, 'r') as f:
                css_content = f.read()
                
                st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
                
        except FileNotFoundError:
            st.error(f'CSS file not found at path: {css_file_path}')