import pandas as pd
import streamlit as st
import numpy as np

# keeping your sklearn structure for data cleaning (Imputation)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer


class DataManager:
    """
    Manages data loading, cleaning, and transformation.
    Acts as the single source of truth for the Streamlit app.
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_df = None
        self.clean_df = None

        # Load data immediately
        self._load_data()

        # Clean and transform immediately
        self.clean_and_transform()

    def _load_data(self):
        """
        Loads the dataset. Uses Streamlit's caching to prevent reloading
        on every user interaction (buttons/filters).
        """
        try:
            # FIX 1: Removed 'skiprows[1]' which is usually incorrect for CSVs with headers
            # Added error_bad_lines=False (or on_bad_lines='skip') to handle corrupted rows
            self.raw_df = pd.read_csv(self.file_path, on_bad_lines='skip')

            # Create a working copy
            self.clean_df = self.raw_df.copy()
            print('Data loaded successfully.')

        except FileNotFoundError:
            st.error(f"File not found at {self.file_path}. Please check your 'data' folder.")
            self.raw_df = pd.DataFrame()
            self.clean_df = pd.DataFrame()
        except Exception as e:
            st.error(f"An error occurred during file initialization: {e}")
            self.raw_df = pd.DataFrame()
            self.clean_df = pd.DataFrame()

    def clean_and_transform(self):
        if self.clean_df is None or self.clean_df.empty:
            return

        # 1. Date Conversion
        # Coerce errors to NaT (Not a Time) to prevent crashes on bad dates
        self.clean_df['date'] = pd.to_datetime(self.clean_df['date'], errors='coerce')

        # Drop rows where date failed to parse (essential for Time-Series analysis)
        self.clean_df = self.clean_df.dropna(subset=['date'])

        # 2. Feature Engineering
        self.clean_df['year'] = self.clean_df['date'].dt.year
        self.clean_df['quarter'] = self.clean_df['date'].dt.quarter
        self.clean_df['month_name'] = self.clean_df['date'].dt.strftime('%B')

        # 3. Sklearn Pipeline for Missing Values (Imputation)
        # Note: We REMOVED StandardScaler. Visualizations need actual PHP prices and Lat/Lon, not Z-scores.

        numerical_features = ['price', 'usdprice', 'latitude', 'longitude']
        # We don't impute Admin/Commodity strings, we just fill missing with 'Unknown'
        categorical_features = ['admin1', 'admin2', 'market', 'category', 'commodity', 'pricetype']

        # Pipeline 1: Numerics (Fill missing prices with median to avoid skewing averages)
        numerical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median'))
        ])

        # Pipeline 2: Categorical (Fill missing text with 'Unknown')
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown'))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ],
            verbose_feature_names_out=False  # Keeps original column names
        )

        try:
            # Apply transformation
            # Note: This returns a numpy array, so we must convert back to DataFrame
            transformed_data = preprocessor.fit_transform(self.clean_df)

            # Reconstruct DataFrame with correct column names
            # Note: ColumnTransformer reorders columns based on the transformers list
            new_columns = numerical_features + categorical_features

            temp_df = pd.DataFrame(transformed_data, columns=new_columns)

            # We need to attach the Date/Year info back because the Transformer dropped them
            # We use index alignment
            temp_df.index = self.clean_df.index
            self.clean_df = pd.concat([temp_df, self.clean_df[['date', 'year', 'quarter', 'month_name']]], axis=1)

            # Enforce correct data types after imputation (Imputer turns things to floats/objects)
            self.clean_df['price'] = pd.to_numeric(self.clean_df['price'])
            self.clean_df['latitude'] = pd.to_numeric(self.clean_df['latitude'])
            self.clean_df['longitude'] = pd.to_numeric(self.clean_df['longitude'])

            print("Data cleaning and transformation complete.")

        except Exception as e:
            st.error(f"An error occurred during SKLearn transformation: {e}")

    # --- GETTERS FOR THE APP ---

    def get_data(self):
        """Returns the cleaned dataframe."""
        return self.clean_df

    def get_commodities(self):
        """Returns sorted list of unique commodities."""
        if self.clean_df is not None:
            return sorted(self.clean_df['commodity'].unique().astype(str))
        return []

    def get_regions(self):
        """Returns sorted list of unique regions (Admin1)."""
        if self.clean_df is not None:
            return sorted(self.clean_df['admin1'].unique().astype(str))
        return []

    def get_summary_stats(self):
        """Returns descriptive statistics for the Overview page."""
        if self.clean_df is not None:
            return self.clean_df.describe()
        return None