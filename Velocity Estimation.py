import pandas as pd
import numpy as np
import Model_Data as md
import Pitch_Average_Metrics as fp
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
    
athlete_path = "./Athletes"

dfs = fp.process_athlete_folder(athlete_path)

fb_df = md.collect_fastballs(dfs)

print("Columns in fb_df:")
print(fb_df.columns.tolist())
"""########## Start running regressions on fastball data ##########
target = "Pitch Speed(mph)"

y = pd.to_numeric(fb_df[target], errors="coerce")
X = fb_df.drop(columns=[target])

# Convert all remaining columns to numeric
X = X.apply(pd.to_numeric, errors="coerce")

# Drop columns that are fully NaN
X = X.dropna(axis=1, how="all")

# Drop rows with missing target
valid = y.notna()
X = X[valid]
y = y[valid]

#
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=500,
    random_state=42,
    max_depth=None
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("R²:", r2_score(y_test, y_pred))

importance = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
})

importance = importance.sort_values("importance", ascending=False)
print(importance.head(15))"""









"""for date, pitch_dict in dfs.items():
    for pitch, content_list in pitch_dict.items():
        for content in content_list:
            summary_df = content['summary']
            #timeseries_df = content['data']
            print(summary_df.head())
            #print(timeseries_df.head())"""
