import streamlit as st
from styles import add_logo
from mortgage_details import display_mortgage_details
from simulation_analysis import display_simulation_and_analysis

# Set page layout to wide
st.set_page_config(page_title="Mortgage Buddy", layout="wide")

add_logo()

# Create tabs
tab1, tab2 = st.tabs(["Mortgage Details", "Simulation and Analysis"])

# Inputs tab
with tab1:
    display_mortgage_details()

# Simulation and Analysis tab
with tab2:
    display_simulation_and_analysis()
