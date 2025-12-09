### Force Plate/Trackman Data Analysis
### Created by: Tony Lanier
### 12/7/2025
### This script will read in force plate/trackman data .csv's for athletes and analyze trends in performance


########## Import packages ##########
import os
import pandas as pd
import numpy as np
import re
import csv

########## Locate each athlete folder ##########
def process_athlete_folder(athlete_path, athlete_name):
    ########## Read in .csv files to unique dataframes ##########
    data_folder = "."

    dfs = {}

    pattern = re.compile(r"([^,]+), ([^,]+), (\d{4}_\d{2}_\d{2}), (.+)\.csv")

    for filename in os.listdir(data_folder):
        if filename.endswith(".csv"):
            match = pattern.match(filename)
            if match:
                last, first, date_str, pitch_type_raw = match.groups()

                # Extract pitch code ("FB", "SL", etc.)
                pitch_code = pitch_type_raw.split("_")[-1]

                filepath = os.path.join(data_folder, filename)
                summary, df_timeseries = load_raw_data(filepath)

                if summary.empty:
                    print(f"Skipped empty file: {filename}")
                    continue
                if df_timeseries.empty:
                    print(f"Skipped empty file: {filename}")
                    continue

                # Create date bucket if doesn’t exist
                if date_str not in dfs:
                    dfs[date_str] = {}

                # Create pitch bucket if doesn't exist
                if pitch_code not in dfs[date_str]:
                    dfs[date_str][pitch_code] = []    

                # Store pitch type under the date
                dfs[date_str][pitch_code].append({
                    "summary": summary,
                    "data": df_timeseries
                })

                print(f"Loaded {pitch_code} for {date_str}")
            else:
                print(f"Filename did not match pattern: {filename}")

    ########## Calculate average for Stride(in), Stride Angle(deg), and Stride Ratio (%) ##########
    # Columns to average
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

    """########## Print results ##########
    for date_str, pitch_dict in pitch_averages.items():
        print(f"=== Date: {date_str} ===")
        for pitch_code, averages in pitch_dict.items():
            print(f"Pitch: {pitch_code}")
            for col, value in averages.items():
                if pd.isna(value):
                    print(f"  {col}: NaN")
                else:
                    print(f"  {col}: {value:.2f}")
        print("\n")"""

    output_folder = os.path.join(athlete_path, "Reports")
    os.makedirs(output_folder, exist_ok=True)

    # Clean filename: "Smith, John" → "Smith_John"
    safe_name = athlete_name#.replace(", ", "_").replace(" ", "_")

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

########## Load in messy data ##########
def load_raw_data(path):
    summary_header = None
    summary_values = None
    ts_header = None
    ts_rows = []

    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)  # assumes comma delimiter; change if needed
        for row in reader:
            if not row:
                continue
            first, last = row[0].strip().lower(), row[-1].strip().lower()

            # Find summary header
            if "accel impulse" in first and "radar ball speed" in last:
                summary_header = row
                summary_values = next(reader)  # next line is the data
                continue

            # Find time series header
            if "time" in first and "y(in)" in last:
                ts_header = row
                ts_rows = list(reader)  # remaining lines
                break

    if summary_header is None or summary_values is None:
        raise ValueError("Summary header row not found or malformed")
    if ts_header is None or not ts_rows:
        raise ValueError("Time series header row not found or empty")

    # Convert summary to DataFrame
    df_summary = pd.DataFrame([summary_values], columns=summary_header)

    # Convert time series to DataFrame
    df_timeseries = pd.DataFrame(ts_rows, columns=ts_header)

    return df_summary, df_timeseries

########## Main loop to process athlete data ##########

root_dir = "."  # change if needed

for folder in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder)

    # Must be directory and match "LastName, FirstName" pattern
    if os.path.isdir(folder_path) and ", " in folder:
        print(f"\n=== Processing athlete: {folder} ===")
        process_athlete_folder(folder_path, folder)











"""########## Export average to file ##########
output_folder = "."

output_file = os.path.join(output_folder, "pitch_averages.xlsx")

# Get all pitch types
all_pitch_types = set()
for date_dict in pitch_averages.values():
    all_pitch_types.update(date_dict.keys())

with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    for pitch_code in all_pitch_types:
        # Collect rows for all metrics across all dates
        data_dict = {}
        for date_str, pitch_dict in pitch_averages.items():
            if pitch_code in pitch_dict:
                for metric, value in pitch_dict[pitch_code].items():
                    if metric not in data_dict:
                        data_dict[metric] = {}
                    data_dict[metric][date_str] = value

        # Build DataFrame: rows = metrics, columns = dates
        df_export = pd.DataFrame(data_dict).T  # metrics as rows
        df_export = df_export.reindex(sorted(df_export.columns), axis=1)  # sort dates

        # Fill missing combinations with NaN
        df_export = df_export.fillna("NaN")

        # Write to a sheet named after the pitch code
        df_export.to_excel(writer, sheet_name=pitch_code)

print(f"Saved all pitch averages to {output_file}")"""

