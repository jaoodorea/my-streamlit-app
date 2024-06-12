import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

# Function to calculate emissions and equivalences
def calculate_emissions_and_equivalents(animal_bw, n_intake, n_digestibility, ammonia_percentage, n2o_percentage, num_animals, num_days):
    n_excreted = n_intake * (1 - n_digestibility / 100)
    total_n_excreted_per_day = n_excreted * num_animals
    total_n_excreted = total_n_excreted_per_day * num_days  # Total nitrogen excreted in grams
    
    # Convert from grams to kilograms
    total_n_excreted_kg = total_n_excreted / 1000
    
    ammonia_emissions = total_n_excreted_kg * (ammonia_percentage / 100)
    n2o_emissions = total_n_excreted_kg * (n2o_percentage / 100)
    
    # Convert from kilograms to metric tons
    n2o_emissions_metric_tons = n2o_emissions / 1000
    
    co2_equivalents = n2o_emissions_metric_tons * 298
    
    vehicles_equivalent = co2_equivalents / 4.6
    homes_equivalent = co2_equivalents / 7.5
    
    return total_n_excreted_kg, ammonia_emissions, n2o_emissions_metric_tons, co2_equivalents, vehicles_equivalent, homes_equivalent

# Streamlit UI
st.title("Diet Comparison for Emissions")
st.header("Input Parameters")

# Input values for Diet 1
col1, col2 = st.columns(2)
with col1:
    st.subheader("Diet 1")
    animal_bw_1 = st.number_input("Animal BW (kg) - Diet 1", value=500)
    n_intake_1 = st.number_input("N Intake (g/day) - Diet 1", value=208)
    n_digestibility_1 = st.number_input("N Digestibility (%) - Diet 1", value=75.4)

# Input values for Diet 2
with col2:
    st.subheader("Diet 2")
    animal_bw_2 = st.number_input("Animal BW (kg) - Diet 2", value=500)
    n_intake_2 = st.number_input("N Intake (g/day) - Diet 2", value=183.2)
    n_digestibility_2 = st.number_input("N Digestibility (%) - Diet 2", value=79.6)

# General Inputs
num_animals = st.number_input("Number of Animals", value=100000)
num_days = st.number_input("Number of Days", value=120)

# Percentages from different sources
sources = {
    'Angellds et al': {'urinary_n': 66.4, 'fecal_n': 33.6, 'nh3_n': 18.24, 'n2o': 1.98},
    'Reed et al': {'urinary_n': 59.3, 'fecal_n': 40.7, 'nh3_n': 16.48, 'n2o': 1.96},
    'IPCC 2006': {'urinary_n': 60, 'fecal_n': 40, 'nh3_n': 37.48, 'n2o': 2.27},
    'IPCC 2019': {'urinary_n': 60, 'fecal_n': 40, 'nh3_n': 36.55, 'n2o': 2.02}
}

# Select source
selected_source = st.selectbox("Select Source", list(sources.keys()))
source_values = sources[selected_source]

# Calculate emissions for Diet 1
total_n_1, ammonia_1, n2o_1, co2e_1, vehicles_1, homes_1 = calculate_emissions_and_equivalents(
    animal_bw_1, n_intake_1, n_digestibility_1, 
    source_values['nh3_n'], source_values['n2o'], 
    num_animals, num_days
)

# Calculate emissions for Diet 2
total_n_2, ammonia_2, n2o_2, co2e_2, vehicles_2, homes_2 = calculate_emissions_and_equivalents(
    animal_bw_2, n_intake_2, n_digestibility_2, 
    source_values['nh3_n'], source_values['n2o'], 
    num_animals, num_days
)

# Calculate the differences
diff_co2e = co2e_1 - co2e_2
diff_ammonia = ammonia_1 - ammonia_2
diff_n2o = n2o_1 - n2o_2
diff_vehicles = vehicles_1 - vehicles_2
diff_homes = homes_1 - homes_2

# Display results
st.header("Results")
st.write(f"Difference in CO2 Equivalents: {diff_co2e:.2f} metric tons CO2e")
st.write(f"Difference in Ammonia Emissions: {diff_ammonia:.2f} kg")
st.write(f"Difference in N2O Emissions: {diff_n2o:.2f} metric tons")
st.write(f"Equivalent to {diff_vehicles:.2f} fewer vehicles")
st.write(f"Equivalent to {diff_homes:.2f} fewer homes")

# Create graphs
st.header("Graphs")

# CO2 Equivalents Comparison
fig, ax = plt.subplots()
categories = ['Diet 1', 'Diet 2']
values = [co2e_1, co2e_2]
bars = ax.bar(categories, values, color=['blue', 'orange'])
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
values = [ammonia_1, ammonia_2]
bars = ax.bar(categories, values, color=['blue', 'orange'])
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

# Helper function to create icons
def create_icon_grid(num_icons, icon_path):
    icon = Image.open(icon_path)
    num_columns = 10
    num_rows = (num_icons // num_columns) + 1
    grid_width = num_columns * icon.width
    grid_height = num_rows * icon.height
    grid_image = Image.new('RGBA', (grid_width, grid_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(grid_image)
    for i in range(num_icons):
        x = (i % num_columns) * icon.width
        y = (i // num_columns) * icon.height
        grid_image.paste(icon, (x, y), icon)
    return grid_image

# Vehicles Equivalent Comparison
#st.subheader("Vehicles Equivalent Comparison")
#car_icon_path = "car.jpeg"  # Path to car icon image
#grid_image = create_icon_grid(int(diff_vehicles), car_icon_path)
#st.image(grid_image, use_column_width=True)

# Homes Equivalent Comparison
#st.subheader("Homes Equivalent Comparison")
#home_icon_path = "house.jpeg"  # Path to home icon image
#grid_image = create_icon_grid(int(diff_homes), home_icon_path)
#st.image(grid_image, use_column_width=True)
