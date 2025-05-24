# 🩺 Early Disease Detection App

This is a Streamlit-based medical decision support tool for early detection of serious diseases (e.g., Dengue, Sepsis, Leukemia, Meningitis) based on patient symptoms.

## 📦 Features

- Doctor input: Patient name, symptoms, diagnosis date
- Mixed-type symptoms: numeric, binary, linguistic
- Disease ranking using Euclidean similarity
- Bar chart of disease likelihood
- Per-criterion analysis
- Fully local or deployable to Streamlit Cloud

## 🧪 Criteria Used

1. Fever (°C)
2. Platelet count (×10⁹/L)
3. White Blood Cell Count (×10⁹/L)
4. Bleeding tendency (Yes/No)
5. Fatigue level (None–Severe)
6. Pain level (None–Extreme)
7. Nausea frequency (None–Frequent)

## ▶️ How to Run

```bash
pip install -r requirements.txt
streamlit run disease_diagnosis_app.py
```

## 📁 Files

- `disease_diagnosis_app.py` - main Streamlit app
- `requirements.txt` - required Python libraries
- `README.md` - this instruction guide

## 🧑‍⚕️ Developed by

Dr. Zahari Md Rodzi and AI assistant - May 2025.