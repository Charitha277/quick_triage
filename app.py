import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from classification_engine import ClassificationEngine
import sqlite3

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect("triage.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    age INTEGER,
    bp TEXT,
    oxygen REAL,
    risk TEXT,
    confidence REAL,
    department TEXT
)
""")
conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department TEXT,
    appointment_date TEXT,
    appointment_time TEXT
)
""")
conn.commit()


# -----------------------------
# LOGIN SYSTEM
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if not st.session_state.logged_in:

    st.title("QuickTriage-AI Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Login As", ["Hospital Staff", "Patient"])

    if st.button("Login"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.rerun()
        else:
            st.error("Enter username and password")

    st.stop()

# THEN your st.set_page_config comes here
st.set_page_config(page_title="QuickTriage-AI", layout="wide")

st.set_page_config(page_title="QuickTriage-AI", layout="wide")

st.title("QuickTriage-AI")
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({
    "logged_in": False,
    "role": None
}))
st.caption("care begins with intelligence")
# =====================================================
# CUSTOM CSS (UI ENHANCEMENT ONLY — NO LOGIC CHANGES)
# =====================================================

# =====================================================
# COMPLETE PROFESSIONAL HOSPITAL DASHBOARD CSS
# =====================================================

st.markdown("""
<style>

/* ---------------- MAIN BACKGROUND ---------------- */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

/* ---------------- HEADINGS ---------------- */
h1 {
    color: #00f2fe;
    text-align: center;
    font-weight: 700;
    letter-spacing: 1px;
}

h2, h3 {
    color: #ffffff;
    border-bottom: 2px solid rgba(255,255,255,0.2);
    padding-bottom: 6px;
    margin-top: 20px;
}

/* ---------------- LABELS (BP, HR, etc.) ---------------- */
label {
    color: white !important;
    font-weight: 500;
}

div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stSlider"] label {
    color: white !important;
}

/* ---------------- INPUT FIELDS ---------------- */
div[data-baseweb="input"] > div {
    background-color: rgba(255,255,255,0.08);
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.2);
    color: white;
}

div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.08);
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.2);
    color: white;
}

/* ---------------- SLIDERS ---------------- */
div[data-testid="stSlider"] {
    color: white;
}

/* ---------------- BUTTONS ---------------- */
div.stButton > button {
    background: linear-gradient(45deg, #00f2fe, #4facfe);
    color: black;
    font-weight: bold;
    border-radius: 10px;
    border: none;
    padding: 8px 18px;
    transition: 0.3s ease;
}

div.stButton > button:hover {
    transform: scale(1.07);
    background: linear-gradient(45deg, #4facfe, #00f2fe);
}

/* ---------------- METRIC CARDS ---------------- */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
}

/* ---------------- ALERTS ---------------- */
div.stAlert-success {
    background-color: rgba(0, 255, 150, 0.15);
    color: #00ffcc;
    border-radius: 10px;
}

div.stAlert-error {
    background-color: rgba(255, 0, 0, 0.15);
    color: #ff4d4d;
    border-radius: 10px;
}

div.stAlert-warning {
    background-color: rgba(255, 193, 7, 0.15);
    color: #ffd966;
    border-radius: 10px;
}

/* ---------------- DATAFRAMES ---------------- */
.stDataFrame {
    background-color: rgba(255,255,255,0.05);
    border-radius: 10px;
}

/* ---------------- SIDEBAR ---------------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1c1c1c, #2a2a2a);
    color: white;
}

/* ---------------- FOOTER HIDE ---------------- */
footer {visibility: hidden;}
header {visibility: hidden;}
/* ===== FIX METRIC COLORS ===== */
div[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

div[data-testid="stMetricLabel"] {
    color: #00f2fe !important;
}
</style>
""", unsafe_allow_html=True)
engine = ClassificationEngine()

if "patients" not in st.session_state:
    st.session_state.patients = []

# -----------------------------
# Patient Entry
# -----------------------------
st.header("New Patient Entry")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", 0, 120, 30)
    bp_input = st.text_input("Blood Pressure (120/80)", "120/80")

with col2:
    heart_rate = st.number_input("Heart Rate", 30, 200, 80)
    oxygen = st.number_input("Oxygen Level (%)", 50, 100, 98)

with col3:
    temperature = st.number_input("Temperature (°F)", 90.0, 110.0, 98.6)
    condition = st.selectbox(
        "Pre-existing Condition",
        [
            "None","Heart Disease","Diabetes","Hypertension",
            "Asthma","Kidney Disease","Liver Disease",
            "Stroke History","Cancer","Pregnancy"
        ]
    )

# -----------------------------
# Symptom Selection
# -----------------------------
st.subheader("Select Symptoms")

symptom_list = [
    "Chest_Pain","Breathing_Difficulty","Shortness_of_Breath",
    "Fever","Severe_Headache","Dizziness","Fatigue","Sweating",
    "Abdominal_Pain","Nausea","Vomiting","Seizures",
    "Slurred_Speech","Cough","Back_Pain","Palpitations",
    "Confusion","Blurred_Vision"
]

selected_symptoms = st.multiselect(
    "Choose Present Symptoms",
    symptom_list
)

st.subheader("Set Severity for Selected Symptoms (1 = Mild, 2 = Moderate, 3 = Severe)")

# Default all to 0
symptom_values = {s: 0 for s in symptom_list}

# Only show sliders for selected symptoms
for symptom in selected_symptoms:
    symptom_values[symptom] = st.slider(
        symptom.replace("_", " "),
        min_value=1,
        max_value=3,
        value=1,
        key=f"severity_{symptom}"
    )

# -----------------------------
# Add Patient
# -----------------------------
if st.button("Add Patient"):

    try:
        systolic = int(bp_input.split("/")[0])
        diastolic = int(bp_input.split("/")[1])
    except:
        st.error("Invalid BP format. Example: 120/80")
        st.stop()

    input_data = {
        "Age": age,
        "Systolic_BP": systolic,
        "Diastolic_BP": diastolic,
        "Heart_Rate": heart_rate,
        "Temperature": temperature,
        "Oxygen_Level": oxygen,
        "Pre_Existing_Conditions": condition,
        **symptom_values
    }

    risk, confidence, department = engine.predict_risk(input_data)

    explanation = engine.explain_prediction(input_data)

    cursor.execute("""
INSERT INTO patients (timestamp, age, bp, oxygen, risk, confidence, department)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    datetime.now().strftime("%H:%M:%S"),
    age,
    bp_input,
    oxygen,
    risk,
    round(confidence, 2),
    department
))

conn.commit()

st.success("Patient Added Successfully")
# -----------------------------
# Dashboard (Hospital Only)
# -----------------------------
if st.session_state.role == "Hospital Staff":

    df = pd.read_sql_query("SELECT * FROM patients", conn)

    st.header("Live Dashboard")

    if not df.empty:

        high = len(df[df["risk"] == "High"])
        medium = len(df[df["risk"] == "Medium"])
        low = len(df[df["risk"] == "Low"])
        total = len(df)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("High Risk", high)
        c2.metric("Medium Risk", medium)
        c3.metric("Low Risk", low)
        c4.metric("Total Patients", total)

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.pie(
                df,
                names="risk",
                color="risk",
                color_discrete_map={
                    "High": "#D32F2F",
                    "Medium": "#F9A825",
                    "Low": "#388E3C"
                }
            )
            st.plotly_chart(fig1, width="stretch")

        with col2:
            dept_counts = df["department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Patients"]
            fig2 = px.bar(dept_counts, x="Department", y="Patients")
            st.plotly_chart(fig2, width="stretch")

        st.divider()

        st.subheader("Priority Queue")

        risk_order = {"High": 0, "Medium": 1, "Low": 2}
        df["Priority"] = df["risk"].map(risk_order)

        df_sorted = df.sort_values(
            by=["Priority", "oxygen", "confidence"],
            ascending=[True, True, False]
        )

        st.dataframe(df_sorted.drop(columns=["Priority"]), width="stretch")

    else:
        st.info("No patients added yet.")

    # ✅ MOVE THIS OUTSIDE the patient condition
    st.divider()
    st.subheader("Booked Appointments")

    appointments_df = pd.read_sql_query("SELECT * FROM appointments", conn)
    

    if not appointments_df.empty:
        st.dataframe(appointments_df, width="stretch")
    else:
        st.info("No appointments booked yet.")
        # ---------------- Delete Patient ----------------
        st.subheader("Delete Patient")

        delete_id = st.number_input(
            "Enter Patient ID to Delete",
            min_value=1,
            step=1
        )

        if st.button("Delete Patient"):
            cursor.execute("DELETE FROM patients WHERE id = ?", (delete_id,))
            conn.commit()
            st.success("Patient deleted successfully")
            st.rerun()

        else:
            st.info("No patients added yet.")
    # =====================================================
# ADDITION: PATIENT SIMULATION (No UI Changes Above)
# =====================================================

st.header("Simulate Patient Scenarios")

scenario = st.selectbox(
    "Select Scenario",
    [
        "Normal Healthy Patient",
        "Moderate Fever Case",
        "Severe Emergency Case",
        "Chronic Disease Patient"
    ]
)
if st.button("Run Simulation"):

    if scenario == "Normal Healthy Patient":
        simulated_data = {
            "Age": 25,
            "Blood_Pressure": 120,
            "Heart_Rate": 72,
            "Oxygen_Level": 99,
            "Temperature": 98.6,
            "Pre_Existing_Conditions": "None"
        }

    elif scenario == "Moderate Fever Case":
        simulated_data = {
            "Age": 40,
            "Blood_Pressure": 130,
            "Heart_Rate": 95,
            "Oxygen_Level": 95,
            "Temperature": 101.5,
            "Pre_Existing_Conditions": "None"
        }

    elif scenario == "Severe Emergency Case":
        simulated_data = {
            "Age": 65,
            "Blood_Pressure": 170,
            "Heart_Rate": 120,
            "Oxygen_Level": 85,
            "Temperature": 104,
            "Pre_Existing_Conditions": "Heart Disease"
        }

    else:
        simulated_data = {
            "Age": 55,
            "Blood_Pressure": 150,
            "Heart_Rate": 100,
            "Oxygen_Level": 93,
            "Temperature": 99,
            "Pre_Existing_Conditions": "Diabetes"
        }

    for col in engine.feature_columns:
        if col not in simulated_data:
            simulated_data[col] = 0

    risk, confidence, department = engine.predict_risk(simulated_data)
    st.session_state.department = department

    st.success(f"Simulated Risk Level: {risk}")
    st.write(f"Confidence: {confidence:.2f}%")
    st.write(f"Assigned Department: {department}")

    st.divider()
    st.subheader("What This Means")

    if risk == "Low":
        st.markdown("🟢 LOW RISK – Condition appears stable.")

    elif risk == "Medium":
        st.markdown("🟠 MEDIUM RISK – Consult specialist soon.")

    elif risk == "High":
        st.markdown("🔴 HIGH RISK – Seek emergency care immediately.")

    st.write(f"Recommended Specialist: **{department}**")

# Appointment Section (OUTSIDE Run Simulation button)
if "department" in st.session_state:

    st.divider()
    st.subheader("Book Appointment")

    appointment_date = st.date_input("Select Appointment Date")
    appointment_time = st.time_input("Select Appointment Time")

    if st.button("Confirm Appointment"):

        cursor.execute("""
        INSERT INTO appointments (department, appointment_date, appointment_time)
        VALUES (?, ?, ?)
        """, (
            st.session_state.department,
            str(appointment_date),
            str(appointment_time)
        ))

        conn.commit()

        st.success(
            f"Appointment booked with {st.session_state.department} on {appointment_date} at {appointment_time}."
        )