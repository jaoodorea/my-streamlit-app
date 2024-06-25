import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

# Function to calculate emissions and equivalences
def calculate_emissions_and_equivalents(n_excreted, ammonia_percentage, n2o_percentage, num_animals, num_days):
    total_n_excreted_kg = n_excreted / 1000  # Convert from grams to kilograms
    
    ammonia_emissions = total_n_excreted_kg * (ammonia_percentage / 100) * num_animals * num_days
    n2o_emissions = (total_n_excreted_kg * (n2o_percentage / 100)) * num_animals * num_days
    
    # Convert from kilograms to metric tons
    n2o_emissions_metric_tons = n2o_emissions / 1000
    
    co2_equivalents = n2o_emissions_metric_tons * 298
    
    vehicles_equivalent = co2_equivalents / 4.6
    homes_equivalent = co2_equivalents / 7.5
    
    return total_n_excreted_kg, ammonia_emissions, n2o_emissions_metric_tons, co2_equivalents, vehicles_equivalent, homes_equivalent

# Define the equations and their inputs
equations = {
    "Equation 16 Dairy - DMI": {
        "formula": lambda DMI: 54.5 + (14.4 * DMI),
        "inputs": ["DMI"]
    },
    "Equation 17 Dairy - N_intake": {
        "formula": lambda N_intake: 49.0 + (0.56 * N_intake),
        "inputs": ["N_intake"]
    },
    "Equation 18 Dairy - Diet": {
        "formula": lambda CP, NDF: 40.1 + (2.2 * CP) - (0.13 * NDF),
        "inputs": ["CP","NDF"]
    },
    "Equation 19 Dairy - Milk": {
        "formula": lambda MY, MUN, MProt: -41.0 + (5.1 * MY) + (6.0 * MUN) + (54.5 * MProt),
        "inputs": ["MY", "MUN", "MProt"]
    },
    "Equation 20 Dairy - MUN": {
        "formula": lambda MUN: 290.7 + (6.1 * MUN),
        "inputs": ["MUN"]
    },
    "Equation 21 Dairy - MUN + N_intake": {
        "formula": lambda N_intake, MUN: 30.0 + (0.55 * N_intake) + (2.5 * MUN),
        "inputs": ["N_intake", "MUN"]
    },
    "Equation 22 Dairy - Full Model": {
        "formula": lambda N_intake, MUN, MProt: -24.5 + (0.54 * N_intake) + (2.5 * MUN) + (14.8 * MProt),
        "inputs": ["N_intake", "MUN", "MProt"]
    },
    "Equation 1 Beef - DMI": {
        "formula": lambda DMI_beef: 5.03 + (6.49 * DMI_beef),
        "inputs": ["DMI_beef"]
    },
    "Equation 2 Beef - N_intake": {
        "formula": lambda N_intake_beef: 13.5 + (0.24 * N_intake_beef),
        "inputs": ["N_intake_beef"]
    },
    "Equation 3 Beef - Diet": {
        "formula": lambda CP_beef, NDF_beef: 24.7 + (0.15 * CP_beef) + (0.06 * NDF_beef),
        "inputs": ["CP_beef", "NDF_beef"]
    },
    "Equation 6 Beef - Full Model": {
        "formula": lambda N_intake_beef, NDFI_beef: 18.8 + (0.15 * N_intake_beef) + (8.89 * NDFI_beef),
        "inputs": ["N_intake_beef", "NDFI_beef"]
    }
    # Add other equations similarly
}

# Define the ranges and stats for the inputs based on the summary statistics
input_stats = {
    "DMI": {"mean": 21.9, "stdev": 3.81, "min": 9.9, "max": 33.0},
    "CP": {"mean": 16.4, "stdev": 1.48, "min": 12.5, "max": 20.5},
    "NDF": {"mean": 34.5, "stdev": 5.84, "min": 20.4, "max": 49.8},
    "N_intake": {"mean": 575.8, "stdev": 116.9, "min": 222.4, "max": 927.2},
    "MUN": {"mean": 10.5, "stdev": 4.12, "min": 1.5, "max": 24.0},
    "MY": {"mean": 33.3, "stdev": 8.23, "min": 7.3, "max": 56.9},
    "MProt": {"mean": 3.21, "stdev": 0.298, "min": 2.45, "max": 4.06},
    "DMI_beef": {"mean": 9.3, "stdev": 2.03, "min": 3.3, "max": 13.6},
    "CP_beef": {"mean": 14.8, "stdev": 3.21, "min": 11.3, "max": 23.0},
    "NDF_beef": {"mean": 32.8, "stdev": 9.08, "min": 11.6, "max": 52.1},
    "N_intake_beef": {"mean": 218, "stdev": 63.2, "min": 97.5, "max": 386},
    "NDFI_beef": {"mean": 3.0, "stdev": 0.99, "min": 0.7, "max": 5.7}
}

# Helper function to simulate input values
def simulate_input(mean, stdev, min_val, max_val):
    simulated_value = np.random.normal(mean, stdev)
    return np.clip(simulated_value, min_val, max_val)

# Initialize session state for inputs if not already set
for key in input_stats.keys():
    if f"sim_{key}" not in st.session_state:
        st.session_state[f"sim_{key}"] = input_stats[key]["mean"]

# Initialize session state for corn processing if not already set
if "corn_processing" not in st.session_state:
    st.session_state.corn_processing = False

def toggle_corn_processing():
    st.session_state.corn_processing = not st.session_state.corn_processing

# Streamlit UI
st.title("Nitrogen Excretion and Emissions Estimation")

# Dropdown for selecting equation
selected_equation = st.selectbox("Select: Dairy Equations from Reed et al., 2015 - https://doi.org/10.3168/jds.2014-8397 or Beef Equations from Bougouin et al., 2022 https://doi.org/10.1093/jas/skac150", list(equations.keys()))

# Display inputs based on selected equation
inputs = {}
for input_name in equations[selected_equation]["inputs"]:
    simulated_value = st.session_state[f"sim_{input_name}"]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        inputs[input_name] = st.number_input(f"Enter {input_name}", value=float(simulated_value), min_value=float(input_stats[input_name]["min"]), max_value=float(input_stats[input_name]["max"]), key=input_name)
    with col2:
        if st.button(f"Simulate {input_name}", key=f"sim_{input_name}_btn"):
            simulated_value = simulate_input(input_stats[input_name]["mean"], input_stats[input_name]["stdev"], input_stats[input_name]["min"], input_stats[input_name]["max"])
            st.session_state[f"sim_{input_name}"] = simulated_value
            st.experimental_rerun()

# Calculate N Excretion based on selected equation and inputs
n_excretion = equations[selected_equation]["formula"](**inputs)

# Display the result
st.write(f"N Excretion: {n_excretion:.2f} g/day")

# Emissions Calculation
st.header("Emissions Calculation")

# General Inputs for Emissions
num_animals = st.number_input("Number of Animals", value=1000, min_value=1)
num_days = st.number_input("Number of Days", value=365, min_value=1)

# Percentages from different sources
sources = {
    'IPCC 2006': {'nh3_n': 37.48, 'n2o': 2.27},
    'IPCC 2019': {'nh3_n': 36.55, 'n2o': 2.02}
}

# Select source
selected_source = st.selectbox("Select Source", list(sources.keys()))
source_values = sources[selected_source]

# Calculate emissions
total_n_excreted_kg, ammonia_emissions, n2o_emissions_metric_tons, co2_equivalents, vehicles_equivalent, homes_equivalent = calculate_emissions_and_equivalents(
    n_excretion, source_values['nh3_n'], source_values['n2o'], num_animals, num_days
)

# Corn processing toggle
corn_processing_btn = st.button("Corn Genetic Improvement", on_click=toggle_corn_processing)

# Apply discount if corn processing is enabled
if st.session_state.corn_processing:
    ammonia_emissions_discounted = ammonia_emissions * 0.73  # Example discount of 10%
    co2_equivalents_discounted = co2_equivalents * 0.73 # Example discount of 10%
    vehicles_equivalent_discounted = co2_equivalents_discounted / 4.6
    homes_equivalent_discounted = co2_equivalents_discounted / 7.5
    button_color = "red"
else:
    ammonia_emissions_discounted = ammonia_emissions
    co2_equivalents_discounted = co2_equivalents
    vehicles_equivalent_discounted = vehicles_equivalent
    homes_equivalent_discounted = homes_equivalent
    button_color = "default"

# Display results
st.write(f"Total N Excreted: {total_n_excreted_kg:.2f} kg")
st.write(f"Ammonia Emissions: {ammonia_emissions:.2f} kg")
st.write(f"N2O Emissions: {n2o_emissions_metric_tons:.2f} metric tons")
st.write(f"CO2 Equivalents: {co2_equivalents:.2f} metric tons CO2e")
st.write(f"Equivalent to {vehicles_equivalent:.2f} vehicles")
st.write(f"Equivalent to {homes_equivalent:.2f} homes")

# Display reduction results if corn processing is enabled
# Display reduction results if corn processing is enabled
if st.session_state.corn_processing:
    st.markdown(f"<span style='color:red'>Reduction in Ammonia Emissions: {ammonia_emissions - ammonia_emissions_discounted:.2f} kg</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:red'>Reduction in CO2 Equivalents: {co2_equivalents - co2_equivalents_discounted:.2f} metric tons CO2e</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:red'>Reduction equivalent to {vehicles_equivalent - vehicles_equivalent_discounted:.2f} vehicles</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:red'>Reduction equivalent to {homes_equivalent - homes_equivalent_discounted:.2f} homes</span>", unsafe_allow_html=True)


# Create graphs
st.header("Graphs")

# CO2 Equivalents Comparison
fig, ax = plt.subplots()
categories = ['Original']
values = [co2_equivalents]

if st.session_state.corn_processing:
    categories.append('Natalia New CornNitro Genotype')
    values.append(co2_equivalents_discounted)

bars = ax.bar(categories, values, color=['blue', 'red'][:len(values)])
ax.set_title('CO2 Equivalents Comparison')
ax.set_ylabel('CO2 Equivalents (metric tons)')

# Add labels
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom')
st.pyplot(fig)

# Ammonia Emissions Comparison
fig, ax = plt.subplots()
categories = ['Original']
values = [ammonia_emissions]

if st.session_state.corn_processing:
    categories.append('With Genetic Improvement')
    values.append(ammonia_emissions_discounted)

bars = ax.bar(categories, values, color=['blue', 'red'][:len(values)])
ax.set_title('Ammonia Emissions Comparison')
ax.set_ylabel('Ammonia Emissions (kg)')

# Add labels
for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='bottom')
st.pyplot(fig)

# Custom CSS for the button
st.markdown(f"""
    <style>
    div.stButton > button:first-child {{
        background-color: {'red' if st.session_state.corn_processing else 'grey'};
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }}
    </style>
""", unsafe_allow_html=True)
