import streamlit as st

class DataPrepPage:
    def __init__(self, data_manager):
        self.dm = data_manager
        
    def render(self):
        st.header('02 Data Preparation')

        st.markdown('hi')
        st.markdown('test')