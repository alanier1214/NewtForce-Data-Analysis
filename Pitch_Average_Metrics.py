### Force Plate/Trackman Data Analysis
### Created by: Tony Lanier
### 12/7/2025
### This script will read in force plate/trackman data .csv's for athletes and analyze trends in pitch metrics by pitch type


########## Import packages ##########
import os
import pandas as pd
import numpy as np
import Read_Files as rf

########## Calculate average for Stride(in), Stride Angle(deg), and Stride Ratio (%) ##########
# Columns to average
def calculate_average(dfs):
    cols_to_avg = ["Accel Impulse(lb*s)","Accel Impulse Score(sec)","Decel Impulse(lb*s)","Player Velo(mph)","Stride(in)", "Stride Angle(deg)", "Stride Ratio(%)",
                "X-Y Back(lb)","X-Y Front(lb)","Y Back(lb)","Y Back Score(lb/lb)","Y Front(lb)","Y Front Score(lb/lb)","Y Transfer(sec)","YZ Back Score(lb/lb)",
                "YZ Front Score(lb/lb)","YZ Transfer Back(sec)","YZ Transfer Front(sec)","Z Back(lb)","Z Back Score(lb/lb)","Z Front(lb)","Z Front Score(lb/lb)","Z Transfer(sec)",
                "Pitch Speed(mph)","Total Spin(rpm)","Release Height(ft)","Release Side(ft)","Active Spin(rpm)","Extension(ft)","Gyro(deg)","Horz Rel Angle(deg)",
                "Spin Efficiency(%)","Vert Rel Angle(deg)","Tilt(clock)","I. Vert. Mov(in)","Horz. Mov(in)","Spin Axis(deg)","Plate Height(ft)","Plate Side(ft)",
                "Vert Appr Angle(deg)","Horz Appr Angle(deg)"]

    pitch_averages = {}

    for date_str, pitch_dict in dfs.items():
        pitch_averages[date_str] = {}

        for pitch_code, content_list in pitch_dict.items():
            # Concatenate all summary DataFrames for this date/pitch
            all_summaries = pd.concat([c['summary'] for c in content_list], ignore_index=True)

            avg_values = {}
            for col in cols_to_avg:
                if col in all_summaries.columns:
                    numeric_col = pd.to_numeric(all_summaries[col], errors='coerce')
                    # Compute mean ignoring NaN
                    if numeric_col.notna().any():
                        avg_values[col] = numeric_col.mean()
                    else:
                        avg_values[col] = np.nan
                else:
                    avg_values[col] = np.nan

            pitch_averages[date_str][pitch_code] = avg_values
    return pitch_averages

def export_pitch_averages(athlete_path, athlete_name, pitch_averages):
    output_folder = os.path.join(athlete_path, "Reports")
    os.makedirs(output_folder, exist_ok=True)

    # Clean filename: "Smith, John" → "Smith_John"
    safe_name = os.path.basename(os.path.join(athlete_path, "Reports"))#.replace(", ", "_").replace(" ", "_")

    output_file = os.path.join(output_folder, f"{safe_name} - Pitch Averages.xlsx")

    all_pitch_types = set()
    for date_dict in pitch_averages.values():
        all_pitch_types.update(date_dict.keys())

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for pitch_code in all_pitch_types:
            data_dict = {}
            for date_str, pitch_dict in pitch_averages.items():
                if pitch_code in pitch_dict:
                    for metric, value in pitch_dict[pitch_code].items():
                        if metric not in data_dict:
                            data_dict[metric] = {}
                        data_dict[metric][date_str] = value

            df_export = pd.DataFrame(data_dict).T
            df_export = df_export.reindex(sorted(df_export.columns), axis=1)
            df_export = df_export.fillna("NaN")

            df_export.to_excel(writer, sheet_name=pitch_code)

    print(f"✓ Export complete for {athlete_name}: {output_file}")

def athlete_overall_averages(pitch_averages):
    """
    Collapses date + pitch averages into one average per metric for an athlete
    """
    records = []

    for date_str, pitch_dict in pitch_averages.items():
        for pitch_code, metrics in pitch_dict.items():
            for metric, value in metrics.items():
                if pd.notna(value):
                    records.append({
                        "metric": metric,
                        "value": value
                    })

    df = pd.DataFrame(records)

    return (
        df.groupby("metric")["value"]
        .mean()
        .reset_index()
    )

########## Main loop to process athlete data ##########

root_dir = "./Athletes"  # change if needed
athlete_folders = rf.resolve_athlete_folders(root_dir)

if not athlete_folders:
    raise RuntimeError(f"No athlete folders found under: {root_dir}")

for folder_path in athlete_folders:
    athlete_name = os.path.basename(os.path.normpath(folder_path))
    print(f"\n=== Processing athlete: {athlete_name} ===")
    dfs = rf.process_athlete_folder(folder_path)
    pitch_avgs = calculate_average(dfs)
    export_pitch_averages(folder_path, athlete_name, pitch_avgs)



