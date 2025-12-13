import pandas as pd

def collect_fastballs(dfs):
    fastballs = []

    for date_str, pitch_dict in dfs.items():
        if "FB" in pitch_dict:
            for entry in pitch_dict["FB"]:
                if "summary" in entry and not entry["summary"].empty:
                    fastballs.append(entry["summary"]) 

    if not fastballs:
        return pd.DataFrame()

    return pd.concat(fastballs, ignore_index=True) 
