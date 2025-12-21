import pandas as pd

def collect_fastballs(dfs):
    fastballs = []

    for date_str, pitch_dict in dfs.items():
        if "FB" in pitch_dict:
            for entry in pitch_dict["FB"]:
                if "summary" in entry and entry["summary"] is not None:
                    
                    summary_obj = entry["summary"]

                    if callable(summary_obj):
                        summary_df = summary_obj()
                    else:
                        summary_df = summary_obj

                    if isinstance(summary_df, pd.DataFrame) and not summary_df.empty:
                        df = summary_df.copy()
                        df["date"] = date_str
                        fastballs.append(df) 

    if not fastballs:
        return pd.DataFrame()

    return pd.concat(fastballs, ignore_index=True) 
