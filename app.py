# Import all the necessary libraries
import pandas as pd
import numpy as np
import joblib
import streamlit as st

# Load the model and structure
model = joblib.load("pollution_model.pkl")
model_cols = joblib.load("model_columns.pkl")

# Define pollutant names and safe limits (example thresholds)
pollutants = ['O2', 'NO3', 'NO2', 'SO4', 'PO4', 'CL']
safe_limits = {
    'O2': (5, float('inf')),     # Minimum oxygen level
    'NO3': (0, 50),
    'NO2': (0, 3),
    'SO4': (0, 250),
    'PO4': (0, 5),
    'CL': (0, 250)
}

# Create UI
st.title("Water Pollutants Predictor")
st.write("Predict water pollutant levels and assess drinkability based on Year and Station ID.")

# User inputs
year_input = st.number_input("Enter Year", min_value=2000, max_value=2100, value=2022)
station_id = st.text_input("Enter Station ID", value='1')

# Prediction trigger
if st.button('Predict'):
    if not station_id:
        st.warning('Please enter the station ID')
    else:
        # Prepare input
        input_df = pd.DataFrame({'year': [year_input], 'id': [station_id]})
        input_encoded = pd.get_dummies(input_df, columns=['id'])

        # Align with model columns
        for col in model_cols:
            if col not in input_encoded.columns:
                input_encoded[col] = 0
        input_encoded = input_encoded[model_cols]

        # Predict
        predicted_pollutants = model.predict(input_encoded)[0]

        # Display predicted values
        st.subheader(f"Predicted pollutant levels for station '{station_id}' in {year_input}:")
        total = sum(predicted_pollutants)
        safe = True
        high_count = 0

        for p, val in zip(pollutants, predicted_pollutants):
            percent = (val / total) * 100 if total > 0 else 0
            st.write(f"**{p}**: {val:.2f} mg/L  → {percent:.2f}%")

            # Safety check
            lower, upper = safe_limits[p]
            if not (lower <= val <= upper):
                safe = False
                high_count += 1

        # Type of water logic
        if safe:
            water_type = "Clean"
        elif high_count <= 2:
            water_type = "Moderately Polluted"
        else:
            water_type = "Highly Polluted"

        # Safe to drink or not
        drinkable = "Safe to Drink" if safe else "Not Safe to Drink"

        st.markdown("---")
        st.subheader("Water Quality Summary")
        st.write(f"**Type of Water**: {water_type}")
        st.write(f"**Drinkable?**: {drinkable}")
