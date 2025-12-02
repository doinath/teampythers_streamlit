# Streamlit Final Project

### Project Overview 

details to be added.

### Project Structure
to be improved... or changed
```angular2html
teampythers_streamlit/
├── .gitignore                            # Tells Git to ignore files like venv/ and notes/
├── .streamlit/                           # Streamlit configuration directory (not in our project)
│   └── secrets.toml                      # For API keys and credentials (not in our project)
├── assets/                               # For static resources like CSS and images
│   └── style.css                         # Your custom styling for the app
├── data/                                 # Data storage directory
│   └── wfp_food_prices_phl.csv           # Your primary project dataset file
├── src/                                  # Source code package (All Python logic lives here)
│   ├── pages/                            # Sub-package for all UI/View classes
│   │   ├── overview_01.py                #
│   │   ├── data_prep_02.py               #
│   ├── app_controller.py                 # StreamlitApp Class (The Controller: Handles state and navigation)
│   └── data_manager.py                   # DataManager Class (The Model: Handles data loading, cleaning, and transformation)
├── app.py                                # Minimal entry point (The Runner: Starts the application)
└── requirements.txt                      # List of Python dependencies (streamlit, pandas, plotly, etc.)
```
### Development Team

This project is a collaborative effort by the following members:

| Role | Name |
| :--- | :--- |
| **Data Analyst** | Julian Ramil Andales |
| **Lead Programmer** | Nathanael Jedd del Castillo |
| **Lead Data Analyst** | Sherielyn Guadiana |
| **Data Analyst** | Kyle Plando |
| **Programmer** | Shervin Dale Tabernero |

### Academic Context

| Detail | Value                                                                                                        |
| :--- |:-------------------------------------------------------------------------------------------------------------|
| **Course Subject** | CS365 - Data Analytics and Visualization                                                                     |
| **Institution** | Cebu Institute of Technology - University                                                                    |
| **Implementation Scope** | This project serves as the comprehensive implementation of **all** concepts taught in CS365, **to be added** |
| **Skills Leveraged** | The team has incorporated **self-taught skills** **to be added**                                             |
