import json
import pandas as pd

# Parses the Explain Plan json file and returns two dataframes,
# one with the global stats and one with the operations
def readExplainPlanFile(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f, strict=False)

        global_stats_df = pd.json_normalize(data['GlobalStats'])
        operations_df = pd.json_normalize(*data['Operations'])

    return global_stats_df, operations_df
