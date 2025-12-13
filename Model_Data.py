import pandas as pd

def collect_fastballs(dfs):
    fastballs = []

    for pitch_dict in dfs.items():
        if "FB" in pitch_dict:
            for entry in pitch_dict["FB"]:
                fastballs.append(entry["summary"])  # or entry["data"]

    if not fastballs:
        return pd.DataFrame()

    return pd.concat([fastballs[fastballs['pitch_code'] == 'FB'] for df in dfs.values()], ignore_index=True) 
