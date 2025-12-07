# Streamlit Final Project

### Project Overview 

This project aims to develop an interactive streamlit app for the course subject CS365 Data Analytics and Visualization using the dataset wfp_food_prices_phl.csv or Philippine food prices. 

### Project Structure
```angular2html
teampythers_streamlit/
├── .gitignore                            # Tells Git to ignore files like venv/ and notes/
├── assets/                               # For static resources like CSS and images
│   │   ├── css/                          # Directory for the .css files
│   │   │   ├── style.css                 # Custom styling for the overall app
│   │   │   ├── overview.css              # Custom styling for the overview_01.py page
│   │   │   ├── app_controller.css        # Custom styling for the app_controller.py page
│   │   ├── images/                       # Directory for the images
│   │   │   ├── julian.png                # .png for profile
│   │   │   ├── kyle.png                  # .png for profile
│   │   │   ├── nate.png                  # .png for profile
│   │   │   ├── sherielyn.png             # .png for profile
│   │   │   ├── sherbin.png               # .png for profile
├── data/                                 # Data storage directory
│   └── wfp_food_prices_phl.csv           # Your primary project dataset file
├── src/                                  # Source code package (All Python logic lives here)
│   ├── pages/                            # Sub-package for all UI/View classes
│   │   ├── overview_01.py                # UI for the overview
│   │   ├── data_prep_02.py               # UI for the data preparation
│   │   ├── analysis_03.py                # UI for the analysis
│   │   ├── conclusion_04.py              # UI for the conclusion
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
