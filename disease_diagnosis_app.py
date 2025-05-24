
# disease_diagnosis_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- Disease Profiles ---
diseases = {
    'Sepsis': [39.0, 180, 25.0, 0, 0.3, 0.6, 0.0],
    'Dengue DHF': [38.5, 45, 4.0, 1, 0.6, 0.3, 0.9],
    'Meningitis': [39.2, 150, 12.0, 0, 0.6, 0.9, 0.3],
    'Leukemia': [38.0, 90, 1.2, 1, 0.6, 0.9, 0.6]
}
criteria = ['Fever', 'Platelet', 'WBC', 'Bleeding', 'Fatigue', 'Pain', 'Nausea']

# --- Title ---
st.title("🩺 Early Disease Detection App")
st.markdown("Input patient symptoms to detect the most likely serious disease.")

# --- User Input ---
with st.form("diagnosis_form"):
    patient_name = st.text_input("Patient Name")
    doctor_name = st.text_input("Doctor Name")
    fever = st.number_input("Fever (°C)", 35.0, 42.0, step=0.1)
    platelet = st.number_input("Platelet Count (×10⁹/L)", 10, 500)
    wbc = st.number_input("White Blood Cell Count (×10⁹/L)", 0.5, 30.0, step=0.1)
    bleeding = st.selectbox("Bleeding Tendency", ["No", "Yes"])
    fatigue = st.selectbox("Fatigue Level", ["None", "Mild", "Moderate", "Severe"])
    pain = st.selectbox("Pain Level", ["None", "Mild", "Moderate", "Severe", "Extreme"])
    nausea = st.selectbox("Nausea Frequency", ["None", "Slight", "Frequent"])
    submitted = st.form_submit_button("Diagnose")

# --- Fuzzy scale ---
fuzzy_map = {
    "None": 0.0,
    "Mild": 0.3,
    "Moderate": 0.6,
    "Severe": 0.9,
    "Extreme": 1.0,
    "Slight": 0.6,
    "Frequent": 0.9,
    "Yes": 1,
    "No": 0
}

# --- Diagnosis ---
if submitted:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    patient_vector = [fever, platelet, wbc, fuzzy_map[bleeding], fuzzy_map[fatigue], fuzzy_map[pain], fuzzy_map[nausea]]

    def euclidean_distance(v1, v2):
        return sum((a - b) ** 2 for a, b in zip(v1, v2)) ** 0.5

    distances = {disease: euclidean_distance(patient_vector, profile) for disease, profile in diseases.items()}
    ranking_df = pd.DataFrame(distances.items(), columns=['Disease', 'Distance']).sort_values(by='Distance')
    max_dist = max(ranking_df['Distance'])
    ranking_df['Similarity (%)'] = (1 - ranking_df['Distance'] / max_dist) * 100

    # Show summary
    st.subheader("🧾 Patient Summary")
    st.write({"Patient": patient_name, "Doctor": doctor_name, "DateTime": now})

    # Show result chart
    st.subheader("📊 Disease Similarity Chart")
    fig, ax = plt.subplots()
    ax.barh(ranking_df['Disease'], ranking_df['Similarity (%)'])
    ax.set_xlabel('Similarity to Patient Profile (%)')
    ax.set_title('Disease Likelihood Based on Symptom Matching')
    ax.invert_yaxis()
    st.pyplot(fig)

    # Diagnosis table
    st.subheader("📋 Disease Ranking")
    st.dataframe(ranking_df.reset_index(drop=True))

    # Analysis per criterion
    st.subheader("🔍 Analysis by Criterion")
    best_match = ranking_df.iloc[0]['Disease']
    st.write(f"Most likely diagnosis: **{best_match}**")
    st.markdown("---")

    for i, crit in enumerate(criteria):
        st.write(f"### {crit}")
        best_value = diseases[best_match][i]
        patient_value = patient_vector[i]
        st.write(f"**Patient value**: {patient_value:.2f}, **{best_match} typical**: {best_value:.2f}")
        diff = abs(patient_value - best_value)
        if diff < 0.1:
            st.success("✔ Very close match")
        elif diff < 0.5:
            st.info("ℹ Slight deviation")
        else:
            st.warning("⚠ Significant difference")

    st.markdown("---")
    st.success("🩺 Diagnosis complete. Please verify with lab results and clinical judgement.")
