import pandas as pd
import numpy as np
import Read_Files as rf

group_stats = pd.read_csv("Group_Metric_Distribution.csv")

target_athlete = 'Ball, Drew'
target_date = "2025_11_21"

athlete_stats = pd.read_excel(f"Athletes/{target_athlete}/Reports/Reports - Pitch Averages.xlsx", sheet_name="FB")

athlete_day = athlete_stats[athlete_stats[target_date] == target_date]

print(athlete_day)


"""comparison = athlete_df.merge(
    group_stats,
    on="metric",
    how="left"
)

comparison["z_score"] = (
    comparison["value"] - comparison["mean"]
) / comparison["std_dev"]

comparison["abs_z"] = comparison["z_score"].abs()

comparison["within_1_sd"] = comparison["abs_z"] <= 1

comparison = comparison.sort_values(
    by="abs_z",
    ascending=False
).reset_index(drop=True)

comparison["rank"] = comparison.index + 1"""




"""def athlete_vs_group_by_date(athlete_df, group_stats, date):
    df = athlete_df[athlete_df["date"] == date].merge(
        group_stats,
        on="metric",
        how="left"
    )

    df["z_score"] = (df["value"] - df["mean"]) / df["std_dev"]
    df["abs_z"] = df["z_score"].abs()
    df["within_1_sd"] = df["abs_z"] <= 1

    df = df.sort_values("abs_z", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1

    return df"""

