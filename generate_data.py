import pandas as pd
import random

NUM_PER_CLASS = 3000  # 3000 Low, 3000 Medium, 3000 High

SYMPTOMS = [
    "Chest_Pain","Breathing_Difficulty","Shortness_of_Breath","Fever",
    "Severe_Headache","Dizziness","Fatigue","Sweating","Abdominal_Pain",
    "Nausea","Vomiting","Seizures","Slurred_Speech","Cough",
    "Back_Pain","Palpitations","Confusion","Blurred_Vision"
]

CONDITIONS = [
    "None","Heart Disease","Diabetes","Hypertension","Asthma",
    "Kidney Disease","Liver Disease","Stroke History","Cancer","Pregnancy"
]

data = []

def generate_case(risk_level):

    age = random.randint(1,100)

    if risk_level == "Low":
        systolic = random.randint(100,130)
        oxygen = random.randint(96,100)
    elif risk_level == "Medium":
        systolic = random.randint(130,160)
        oxygen = random.randint(92,96)
    else:  # High
        systolic = random.randint(160,200)
        oxygen = random.randint(80,92)

    diastolic = random.randint(60,120)
    heart_rate = random.randint(60,150)
    temperature = round(random.uniform(97,103),1)
    condition = random.choice(CONDITIONS)

    row = {
        "Age": age,
        "Systolic_BP": systolic,
        "Diastolic_BP": diastolic,
        "Heart_Rate": heart_rate,
        "Temperature": temperature,
        "Oxygen_Level": oxygen,
        "Pre_Existing_Conditions": condition
    }

    for symptom in SYMPTOMS:
        if risk_level == "Low":
            severity = random.choice([0,0,0,1])
        elif risk_level == "Medium":
            severity = random.choice([0,1,2])
        else:
            severity = random.choice([2,3])
        row[symptom] = severity

    row["Risk_Level"] = risk_level
    return row

# Generate balanced data
for _ in range(NUM_PER_CLASS):
    data.append(generate_case("Low"))
    data.append(generate_case("Medium"))
    data.append(generate_case("High"))

df = pd.DataFrame(data)
df.to_csv("synthetic_data.csv", index=False)

print("Balanced Dataset Generated")
print(df["Risk_Level"].value_counts())