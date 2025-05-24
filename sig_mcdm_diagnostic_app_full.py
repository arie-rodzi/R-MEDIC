
# sig_mcdm_diagnostic_app_full.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import os
from fpdf import FPDF
from PIL import Image

# --- Disease Profiles ---
diseases = {
    'Sepsis': [39.0, 180, 25.0, 0, 0.3, 0.6, 0.0],
    'Dengue DHF': [38.5, 45, 4.0, 1, 0.6, 0.3, 0.9],
    'Meningitis': [39.2, 150, 12.0, 0, 0.6, 0.9, 0.3],
    'Leukemia': [38.0, 90, 1.2, 1, 0.6, 0.9, 0.6]
}
criteria = ['Fever (°C)', 'Platelet Count', 'WBC Count', 'Bleeding', 'Fatigue', 'Pain', 'Nausea']
fuzzy_map = {
    "None": 0.0, "Mild": 0.3, "Moderate": 0.6, "Severe": 0.9, "Extreme": 1.0,
    "Slight": 0.6, "Frequent": 0.9, "Yes": 1, "No": 0
}
explanation = {
    'Dengue DHF': [
        "- Fever exactly matches Dengue profile (38.5°C).",
        "- Platelet count is critically low, very close to Dengue's (45 vs patient).",
        "- WBC is low, consistent with viral infection.",
        "- Bleeding present - matches hallmark of Dengue Hemorrhagic Fever.",
        "- Fatigue and nausea severity align closely with Dengue symptoms.",
        "- Overall, 5 out of 7 criteria are strong matches to Dengue."
    ],
    'Sepsis': ["- High fever with systemic fatigue and abnormal WBC alignment."],
    'Meningitis': ["- High fever with nausea and neurological symptom indicators."],
    'Leukemia': ["- Critical low WBC and platelet matching hematologic disorder trends."]
}

st.set_page_config(page_title="SIG-MCDM Diagnostic Support System")
st.title("🧠 SIG-MCDM Diagnostic Support System")

with st.form("diagnosis_form"):
    patient_name = st.text_input("Patient Name")
    doctor_name = st.text_input("Doctor Name")
    fever = st.number_input("Fever (°C)", 35.0, 42.0, step=0.1)
    platelet = st.number_input("Platelet Count", 10, 500)
    wbc = st.number_input("WBC Count", 0.5, 30.0, step=0.1)
    bleeding = st.selectbox("Bleeding", ["No", "Yes"])
    fatigue = st.selectbox("Fatigue", ["None", "Mild", "Moderate", "Severe"])
    pain = st.selectbox("Pain", ["None", "Mild", "Moderate", "Severe", "Extreme"])
    nausea = st.selectbox("Nausea", ["None", "Slight", "Frequent"])
    healthy_image = st.file_uploader("Upload Patient vs Healthy Chart (PNG)", type=["png"])
    submitted = st.form_submit_button("Diagnose")

if submitted and healthy_image:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    patient_vector = [
        fever, platelet, wbc,
        fuzzy_map[bleeding], fuzzy_map[fatigue],
        fuzzy_map[pain], fuzzy_map[nausea]
    ]

    def euclidean_distance(v1, v2):
        return sum((a - b) ** 2 for a, b in zip(v1, v2)) ** 0.5

    distances = {disease: euclidean_distance(patient_vector, profile) for disease, profile in diseases.items()}
    ranking_df = pd.DataFrame(distances.items(), columns=['Disease', 'Distance']).sort_values(by='Distance')
    max_dist = max(ranking_df['Distance'])
    ranking_df['Similarity (%)'] = (1 - ranking_df['Distance'] / max_dist) * 100
    top_disease = ranking_df.iloc[0]['Disease']

    # Save images
    report_dir = "diagnosis_reports"
    os.makedirs(report_dir, exist_ok=True)
    base_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{patient_name.replace(' ', '_')}"
    bar_chart_path = os.path.join(report_dir, f"{base_name}_bar.png")
    radar_chart_path = os.path.join(report_dir, f"{base_name}_radar.png")
    healthy_chart_path = os.path.join(report_dir, f"{base_name}_healthy.png")

    # Save uploaded chart
    with open(healthy_chart_path, "wb") as out_file:
        out_file.write(healthy_image.getbuffer())

    # Bar Chart
    fig1, ax = plt.subplots(figsize=(6, 3))
    ax.barh(ranking_df['Disease'], ranking_df['Similarity (%)'], color='green')
    ax.set_xlabel('Similarity Score (%)')
    ax.set_title('Diagnosis Ranking')
    ax.invert_yaxis()
    for i, (disease, score) in enumerate(zip(ranking_df['Disease'], ranking_df['Similarity (%)'])):
        ax.text(score + 1, i, f"{score:.1f}%", va='center', fontsize=9)
    fig1.savefig(bar_chart_path, bbox_inches='tight')
    plt.close(fig1)

    # Radar Chart
    def normalize(vals):
        max_vals = [42, 500, 30, 1, 1, 1, 1]
        return [v / m for v, m in zip(vals, max_vals)]
    labels = criteria
    patient_norm = normalize(patient_vector)
    disease_norm = normalize(diseases[top_disease])

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    patient_norm += patient_norm[:1]
    disease_norm += disease_norm[:1]

    fig2, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, patient_norm, color="blue", label="Patient")
    ax.fill(angles, patient_norm, color="blue", alpha=0.3)
    ax.plot(angles, disease_norm, color="green", label=top_disease)
    ax.fill(angles, disease_norm, color="green", alpha=0.3)
    ax.set_title(f"Profile Comparison: Patient vs {top_disease}")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.legend(loc="upper right")
    fig2.savefig(radar_chart_path, bbox_inches='tight')
    plt.close(fig2)

    # PDF Report
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", 'B', 12)
            self.cell(0, 10, "SIG-MCDM Diagnosis Report", ln=True, align='C')
        def footer(self):
            self.set_y(-12)
            self.set_font("Arial", 'I', 8)
            self.cell(0, 10, "Generated by SIG-MCDM System", align='C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 8, f"Patient: {patient_name}   Doctor: {doctor_name}   Date: {now}", ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "Patient Input Summary", ln=True)
    pdf.set_font("Arial", '', 10)
    for i, crit in enumerate(criteria):
        val = f"{patient_vector[i]}" if i < 3 else list(fuzzy_map.keys())[list(fuzzy_map.values()).index(patient_vector[i])]
        pdf.cell(0, 6, f"{crit}: {val}", ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, f"Why '{top_disease}' is Ranked #1", ln=True)
    pdf.set_font("Arial", '', 10)
    for line in explanation.get(top_disease, ["Explanation not available."]):
        pdf.multi_cell(0, 6, line)

    pdf.add_page()
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "Similarity Ranking of Diseases", ln=True)
    pdf.image(bar_chart_path, x=10, y=30, w=180)

    pdf.add_page()
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, f"Profile Comparison: Patient vs {top_disease}", ln=True)
    pdf.image(radar_chart_path, x=10, y=30, w=180)

    pdf.add_page()
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "Patient vs Healthy Profile", ln=True)
    pdf.image(healthy_chart_path, x=10, y=30, w=180)

    pdf_path = os.path.join(report_dir, f"{base_name}_Report.pdf")
    pdf.output(pdf_path)

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📥 Download Final Diagnosis Report (PDF)",
            data=f,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf",
            key="final_report_full"
        )
