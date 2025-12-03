import pandas as pd
import streamlit as st

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

        self._load_data()

        self.clean_and_transform()

    def _load_data(self):
        """
        Loads the dataset. Uses Streamlit's caching to prevent reloading
        on every user interaction (buttons/filters).
        """
        try:

            self.raw_df = pd.read_csv(self.file_path, on_bad_lines='skip')

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

        self.clean_df['date'] = pd.to_datetime(self.clean_df['date'], format='mixed', errors='coerce')

        self.clean_df = self.clean_df.dropna(subset=['date'])

        self.clean_df['year'] = self.clean_df['date'].dt.year
        self.clean_df['quarter'] = self.clean_df['date'].dt.quarter
        self.clean_df['month_name'] = self.clean_df['date'].dt.strftime('%B')

        numerical_features = ['price', 'usdprice', 'latitude', 'longitude']

        categorical_features = ['admin1', 'admin2', 'market', 'category', 'commodity', 'pricetype']


        numerical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median'))
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown'))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ],
            verbose_feature_names_out=False
        )

        try:

            transformed_data = preprocessor.fit_transform(self.clean_df)

            new_columns = numerical_features + categorical_features

            temp_df = pd.DataFrame(transformed_data, columns=new_columns)

            temp_df.index = self.clean_df.index
            self.clean_df = pd.concat([temp_df, self.clean_df[['date', 'year', 'quarter', 'month_name']]], axis=1)

            self.clean_df['price'] = pd.to_numeric(self.clean_df['price'])
            self.clean_df['latitude'] = pd.to_numeric(self.clean_df['latitude'])
            self.clean_df['longitude'] = pd.to_numeric(self.clean_df['longitude'])

            print("Data cleaning and transformation complete.")

        except Exception as e:
            st.error(f"An error occurred during SKLearn transformation: {e}")


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