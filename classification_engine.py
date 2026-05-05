import joblib
import pandas as pd
import numpy as np

class ClassificationEngine:

    def __init__(self):
        self.model = joblib.load("risk_model.pkl")
        self.feature_columns = self.model.feature_names_in_

    # -------------------------------------------------
    # Encode Pre-existing Condition
    # -------------------------------------------------
    def encode_condition(self, condition):

        condition_map = {
            "None": 0,
            "Heart Disease": 1,
            "Diabetes": 2,
            "Hypertension": 3,
            "Asthma": 4,
            "Kidney Disease": 5,
            "Liver Disease": 6,
            "Stroke History": 7,
            "Cancer": 8,
            "Pregnancy": 9
        }

        return condition_map.get(condition, 0)

    # -------------------------------------------------
    # Hybrid Emergency Override
    # -------------------------------------------------
    def rule_based_override(self, data):

        if data.get("Oxygen_Level", 100) < 90:
            return "High"

        if data.get("Temperature", 98) > 103:
            return "High"

        severe = [
            data.get("Chest_Pain", 0),
            data.get("Breathing_Difficulty", 0),
            data.get("Seizures", 0),
            data.get("Slurred_Speech", 0),
            data.get("Confusion", 0)
        ]

        if max(severe) >= 3:
            return "High"

        return None

    # -------------------------------------------------
    # Department Recommendation Logic
    # -------------------------------------------------
    def recommend_department(self, data, risk):

        # High Risk Routing
        if risk == "High":
            if data.get("Chest_Pain", 0) >= 2:
                return "Cardiologist"
            if data.get("Breathing_Difficulty", 0) >= 2 or data.get("Oxygen_Level", 100) < 90:
                return "Pulmonologist"
            if data.get("Seizures", 0) >= 1 or data.get("Slurred_Speech", 0) >= 1:
                return "Neurologist"
            return "Emergency Medicine"

        # Medium Risk Routing
        if risk == "Medium":
            if data.get("Chest_Pain", 0) >= 1 or data.get("Palpitations", 0) >= 1:
                return "Cardiologist"
            if data.get("Breathing_Difficulty", 0) >= 1 or data.get("Cough", 0) >= 1:
                return "Pulmonologist"
            if data.get("Abdominal_Pain", 0) >= 1 or data.get("Vomiting", 0) >= 1:
                return "Gastroenterologist"
            if data.get("Seizures", 0) >= 1 or data.get("Confusion", 0) >= 1:
                return "Neurologist"
            return "General Physician"

        # Low Risk
        return "General Physician"

    # -------------------------------------------------
    # Risk Prediction
    # -------------------------------------------------
    def predict_risk(self, input_data):

        input_data = input_data.copy()

        input_data["Pre_Existing_Conditions"] = self.encode_condition(
            input_data.get("Pre_Existing_Conditions", "None")
        )

        # Hybrid override
        override = self.rule_based_override(input_data)

        df = pd.DataFrame([input_data])
        df = df.reindex(columns=self.feature_columns, fill_value=0)

        pred = self.model.predict(df)[0]
        probs = self.model.predict_proba(df)[0]
        confidence = max(probs) * 100

        # Handle numeric model output
        if isinstance(pred, (int, np.integer)):
            if int(pred) == 0:
                risk = "Low"
            elif int(pred) == 1:
                risk = "Medium"
            else:
                risk = "High"
        else:
            risk = str(pred)

        # Override to High if medical rule triggered
        if override == "High":
            risk = "High"

        department = self.recommend_department(input_data, risk)

        return risk, confidence, department

    # -------------------------------------------------
    # Explainability Module
    # -------------------------------------------------
    def explain_prediction(self, input_data):

        input_data = input_data.copy()

        input_data["Pre_Existing_Conditions"] = self.encode_condition(
            input_data.get("Pre_Existing_Conditions", "None")
        )

        df = pd.DataFrame([input_data])
        df = df.reindex(columns=self.feature_columns, fill_value=0)

        importances = self.model.feature_importances_

        explanation_df = pd.DataFrame({
            "Feature": self.feature_columns,
            "Patient Value": df.iloc[0].values,
            "Importance": importances
        })

        explanation_df["Contribution"] = (
            explanation_df["Patient Value"] * explanation_df["Importance"]
        )

        explanation_df = explanation_df.sort_values(
            by="Contribution",
            ascending=False
        )

        return explanation_df.head(5)