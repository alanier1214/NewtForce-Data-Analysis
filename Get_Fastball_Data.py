import Read_Files as rf

# Assuming fb_df contains all athletes fastball data
# If you already have a combined DataFrame, use that
# fb_df = pd.concat(all_fastballs, ignore_index=True)  # if needed

# Specify the output CSV file path
output_file = "all_athletes_fastballs.csv"

root_dir = "./Athletes"

athlete_folders = rf.resolve_athlete_folders(root_dir)

fb_df = rf.get_fastball_data(athlete_folders)

# Export to CSV
fb_df.to_csv(output_file, index=False)

print(f"✓ All athlete fastball data exported to {output_file}")