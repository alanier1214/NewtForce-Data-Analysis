import os
import pandas as pd

# ---------------- CONFIG ----------------
ATHLETES_ROOT = "./Athletes"
MASTER_ROOT = "./All Athlete Averages"
MASTER_FILE = os.path.join(MASTER_ROOT, "Master_Pitch_Averages.xlsx")
# ----------------------------------------

def find_athlete_report_files(root_dir):
    """Find all per-athlete 'Pitch Averages.xlsx' files."""
    report_files = []
    for athlete_folder in os.listdir(root_dir):
        athlete_path = os.path.join(root_dir, athlete_folder)
        if not os.path.isdir(athlete_path):
            continue

        report_folder = os.path.join(athlete_path, "Reports")
        if not os.path.exists(report_folder):
            continue

        for f in os.listdir(report_folder):
            if f.endswith("Pitch Averages.xlsx"):
                report_files.append(os.path.join(report_folder, f))  # ONLY file path
    return report_files

def aggregate_pitch_averages(report_files):
    """Aggregate metrics across all athletes for each pitch type."""
    pitch_data = {}  # key: pitch_type, value: list of dataframes to combine

    for file_path in report_files:
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, index_col=0)
            # df: rows = metrics, columns = dates
            # Flatten to metric:value
            df_values = df.apply(pd.to_numeric, errors='coerce')  # ensure numeric
            if sheet_name not in pitch_data:
                pitch_data[sheet_name] = []
            pitch_data[sheet_name].append(df_values)

    # Compute average per metric per pitch
    pitch_averages = {}
    for pitch, df_list in pitch_data.items():
        combined_df = pd.concat(df_list, axis=1)  # combine all athlete columns
        metric_avg = combined_df.mean(axis=1, skipna=True)  # average across all columns
        pitch_averages[pitch] = metric_avg

    return pitch_averages


def export_master_file(pitch_averages, output_file):
    """Write each pitch type to a separate sheet."""
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for pitch, series in pitch_averages.items():
            df_export = series.reset_index()
            df_export.columns = ["Metric", "Average Value"]
            df_export.to_excel(writer, sheet_name=pitch, index=False)
    print(f"✓ Master file created: {output_file}")

def main():
    report_files = find_athlete_report_files(ATHLETES_ROOT)
    if not report_files:
        raise RuntimeError(f"No athlete reports found under {ATHLETES_ROOT}")

    pitch_averages = aggregate_pitch_averages(report_files)
    export_master_file(pitch_averages, MASTER_FILE)


if __name__ == "__main__":
    main()