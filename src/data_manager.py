import pandas as pd

# possible imports
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class DataManager:
    """
    Manages data loading, cleaning, and transformation.
    It ensures data is laoded only once and is accessible 
    to all Streamlit pages classes.
    """
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_df = None
        self.clean_df = None
        
        # loads data when initialize or instantiated
        self._load_data()
        
        # cleaning and transformation
        self.clean_and_transform()
        
    def _load_data(self):
        """
        Loads the initial dataset from the file path defined in app_controller.py.
        This fulfills the first part of the 'Overview' and 'Exploration' sections.
        """
        
        try:

            self.raw_df = pd.read_csv(self.file_path, skiprows[1])
            self.clean_df = self.raw_df.copy()
            print('data loaded sucessfully.')
            
        except FileNotFoundError:
            print(f'error: file not found at {self.file_path}. check your data folder.')
            self.raw_df = pd.DataFrame()
            self.clean_df = pd.DataFrame()
        except Exception as e:
            print(f'an error occured during the file initialization: {e}')
            self.raw_df = pd.DataFrame()
            self.clean_df = pd.DataFrame()
            
    def clean_and_transform(self):
        
        if self.clean_df is None or self.clean_df.empty:
            print('cannot clean data: DataFrame is empty.')
            return

        print('Starting data cleaning and transformation for the pythers project.')

        self.clean_df['date'] = pd.to_datetime(self.clean_df['date'])

        self.clean_df['year'] = self.clean_df['date'].dt.year
        self.clean_df['quarter'] = self.clean_df['date'].dt.quarter

        # config

        numerical_features = ['price', 'usdprice', 'latitude', 'longitude']
        categorical_features = ['admin1', 'admin2', 'market', 'category', 'commodity', 'pricetype']


        # scaling
        numerical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing'))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ],
            remainder = 'passthrough'
        )

        try:
            transformed_data = preprocessor.fit_transform(self.clean_df[numerical_features + categorical_features])

            transformed_df = pd.DataFrame(
                transformed_data,
                columns=numerical_features + categorical_features
            )

            self.clean_df = transformed_df.join(self.clean_df[['date', 'year', 'quarter']])

        except Exception as e:
            print(f'An unexpected error occured during data transformation: {e}')
        
        print("Data cleaning and transformation complete.")
        
    def get_raw_data(self):
        """Returns the original, unmodified DataFrame for display in the Overview section."""
        return self.raw_df
    
    def get_clean_data(self):
        """Calculates and returns summary statistics for the Overview section."""
        return self.clean_df
    
    def get_summary_stats(self):
        """Calculates and returns summary statistics for the Overview section."""
        if self.raw_df is not None and not self.raw_df.empty:
            return self.raw_df.describe()
        
        return None