import streamlit as st
import pandas as pd
import plotly.express as px

class AnalysisPage:
    def __init__(self, data_manager):
        self.dm = data_manager

    def render(self):
        # ----------------------------------------------------
        # CRITICAL FIX 1: Fetch the data from DataManager
        # ----------------------------------------------------
        df = self.dm.get_data().copy()

        if df is None or df.empty:
            st.error("No data available for analysis. Please check the dataset file.")
            return

