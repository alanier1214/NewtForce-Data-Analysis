import pandas as pd
import joblib

########## Load in the prediction model ##########
model = joblib.load("random_forest_model.pkl")
imputer = joblib.load("imputer.pkl")
selected_features = joblib.load("selected_features.pkl")

print("✓ Loaded model, imputer, and feature list.")

########## Get athlete data ##########
fb_df = pd.read_csv("all_athletes_fastballs.csv")  

# Specify the athlete to test
athlete_name = "Scherer, Maddux"
athlete_df = fb_df[fb_df["Athlete"] == athlete_name].copy()

if athlete_df.empty:
    raise ValueError(f"No data found for athlete: {athlete_name}")

########## Prepare model ##########
X_athlete = athlete_df[selected_features].copy()

# Handle missing values using the saved imputer
X_athlete = pd.DataFrame(
    imputer.transform(X_athlete),
    columns=X_athlete.columns,
    index=X_athlete.index
)

# Predict
y_pred = model.predict(X_athlete)
athlete_df["Predicted Pitch Speed"] = y_pred
target_col = "Pitch Speed(mph)"
print(athlete_df[["Athlete", target_col, "Predicted Pitch Speed"]].head(10))