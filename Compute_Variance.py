import os
import pandas as pd
import Read_Files as rf
from Pitch_Average_Metrics import calculate_average, athlete_overall_averages

root_dir = "./Athletes"

all_athletes = []

athlete_folders = rf.resolve_athlete_folders(root_dir)

for folder_path in athlete_folders:
    athlete_name = os.path.basename(os.path.normpath(folder_path))

    dfs = rf.process_athlete_folder(folder_path)
    pitch_avgs = calculate_average(dfs)

    athlete_avg = athlete_overall_averages(pitch_avgs)
    athlete_avg["athlete"] = athlete_name

    all_athletes.append(athlete_avg)

group_df = pd.concat(all_athletes, ignore_index=True)

group_stats = (
    group_df
    .groupby("metric")["value"]
    .agg(mean="mean", std_dev="std")
    .reset_index()
)

master_df = pd.read_excel("All Athlete Averages\Master_Pitch_Averages.xlsx")

comparison = master_df.merge(
    group_stats,
    left_on="Metric",
    right_on="metric",
    how="left"
)

comparison["mean_diff"] = comparison["Average Value"] - comparison["mean"]

group_stats.to_csv("Group_Metric_Distribution.csv", index=False)

