from email.policy import strict
import os
import json
import pandas as pd

# current_directory = os.path.dirname(__file__)
# file_path = os.path.join(current_directory, '..\\Explain Plan generated.JSON')

# with open(file_path, 'r') as f:
#     data = json.load(f, strict=False)

# print(data)

def readExplainPlanFile(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f, strict=False)

        global_stats_df = pd.json_normalize(data['GlobalStats'])
        operations_df = pd.json_normalize(*data['Operationts'])

    return global_stats_df, operations_df
