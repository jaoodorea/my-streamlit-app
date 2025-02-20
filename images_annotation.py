import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from PIL import Image

# Load dataset
@st.cache_data
def load_data(csv_path):
    return pd.read_csv(csv_path)

# Function to display image and classification options
def display_image_with_classes(image_path, row, df):
    st.image(image_path, caption=f"{row['Filename']}", use_column_width=True)
    
    # Display class probability
    st.markdown(f"### Predicted Class: {row['Class']} ({row['Probability']*100:.2f}%)")
    
    # Available class options (excluding the predicted one)
    classes = ["Empty", "Low", "Medium", "Full"]
    remaining_classes = [c for c in classes if c != row['Class']]
    
    selected_class = st.radio("Select Correct Class if Incorrect:", [row['Class']] + remaining_classes)
    
    return selected_class

# Function to update classification
def update_classification(df, index, new_class, csv_path):
    df.loc[index, "Corrected Class"] = new_class
    df.to_csv(csv_path, index=False)
    
# Main App
def main():
    st.title("Image Classification Evaluator")
    
    # File paths with user input at startup
    if "image_folder" not in st.session_state:
        st.session_state.image_folder = ""
    if "csv_path" not in st.session_state:
        st.session_state.csv_path = ""
    
    st.session_state.image_folder = st.text_input("Enter the image folder path:", st.session_state.image_folder)
    st.session_state.csv_path = st.text_input("Enter the CSV file path:", st.session_state.csv_path)
    
    if not st.session_state.image_folder or not st.session_state.csv_path:
        st.warning("Please enter the paths above to start.")
        return
    
    if not os.path.exists(st.session_state.image_folder) or not os.path.exists(st.session_state.csv_path):
        st.error("Invalid paths. Please check the file paths and try again.")
        return
    
    df = load_data(st.session_state.csv_path)
    if "Corrected Class" not in df.columns:
        df["Corrected Class"] = df["Class"]
    
    # Initialize index in session state
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    
    index = st.session_state.current_index
    
    if index >= len(df):
        st.success("All images reviewed!")
        return
    
    row = df.iloc[index]
    image_path = os.path.join(st.session_state.image_folder, row["Filename"])
    
    if not os.path.exists(image_path):
        st.error(f"Image not found: {image_path}")
        return
    
    selected_class = display_image_with_classes(image_path, row, df)
    
    if st.button("Next Image"):
        if selected_class != row["Class"]:
            update_classification(df, index, selected_class, st.session_state.csv_path)
        st.session_state.current_index += 1
        st.experimental_rerun()
    
if __name__ == "__main__":
    main()
