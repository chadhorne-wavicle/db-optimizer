import json
import pandas as pd

# Prints explain plan analysis to stdout
# Takes the file path to the explain plan file
def getExplainPlanAnalysis(file_path):
    global_stats, operations = readExplainPlanFile(file_path)

    print('\nGlobal Stats')
    print(global_stats.to_markdown(index=False))

    print('\nCount of operations')
    print(operations['operation'].value_counts().to_markdown())

    print('\nObjects scanned')
    # print(operations[operations['operation'] == 'TableScan'].explode('objects')['objects'].value_counts().to_markdown())
    print(getValueCounts(column='objects', operation_type='TableScan', df=operations).to_markdown())

    print('\nObject partitions')
    print(operations.explode('objects')[['objects', 'partitionsAssigned', 'partitionsTotal', 'bytesAssigned']] \
        .groupby('objects').agg(['sum']).to_markdown())

    print('\nFilter expressions')
    print(getValueCounts(column='expressions', operation_type='Filter', df=operations).to_markdown())

    print('\nJoinFilter expressions')
    print(getValueCounts(column='expressions', operation_type='JoinFilter', df=operations).to_markdown())

    print('\nInnerJoin expressions')
    print(getValueCounts(column='expressions', operation_type='InnerJoin', df=operations).to_markdown())

    print('\nSort expressions')
    print(getValueCounts(column='expressions', operation_type='Sort', df=operations).to_markdown())


# Helper function to get value counts
def getValueCounts(column, operation_type, df):
    agg_df = df[df['operation'] == operation_type].explode(column)[column].value_counts()
    return agg_df
    
# Parses the Explain Plan json file and returns two dataframes,
# one with the global stats and one with the operations
def readExplainPlanFile(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f, strict=False)

        global_stats_df = pd.json_normalize(data['GlobalStats'])
        operations_df = pd.json_normalize(*data['Operations'])

    return global_stats_df, operations_df
