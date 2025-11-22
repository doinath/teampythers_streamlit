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
            self.raw_df = pd.read_csv(self.file_path)
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
        
        # st.cache_data.clear() 
        
        # --- TODO: IMPLEMENTATION START ---
        
        # 1. Handle Missing Values:
        # Example: self.clean_df.fillna(self.clean_df['some_col'].mean(), inplace=True)
        # Your code here...
        
        # 2. Feature Engineering / Encoding:
        # Example: self.clean_df = pd.get_dummies(self.clean_df, columns=['category_col'])
        # Your code here...

        # 3. Data Scaling/Normalization (if required for your analysis technique):
        # Example: from sklearn.preprocessing import StandardScaler
        # scaler = StandardScaler()
        # self.clean_df[['feature1', 'feature2']] = scaler.fit_transform(self.clean_df[['feature1', 'feature2']])
        # Your code here...
        
        # --- TODO: IMPLEMENTATION END ---
        
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