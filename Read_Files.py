import os
import re
import pandas as pd
import csv

########## Locate each athlete folder ##########
def process_athlete_folder(athlete_path):

    ########## Read in .csv files to unique dataframes ##########
    dfs = {}

    pattern = re.compile(r"([^,]+), ([^,]+), (\d{4}_\d{2}_\d{2}), (.+)\.csv")

    for filename in os.listdir(athlete_path):
        if filename.endswith(".csv"):
            match = pattern.match(filename)
            if match:
                #last, first, 
                date_str, pitch_type_raw = match.groups()

                # Extract pitch code ("FB", "SL", etc.)
                pitch_code = pitch_type_raw.split("_")[-1]

                filepath = os.path.join(athlete_path, filename)
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
    return dfs

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

# Check if a single athlete folder or multiple athlete folders
def is_athlete_folder(path):
    return os.path.isdir(path) and ", " in os.path.basename(path)
