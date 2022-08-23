import json
import numpy as np
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
    print(getValueCounts(column='objects', operation_type='TableScan', df=operations).to_markdown())

    print('\nObject partitions')
    print(operations.explode('objects')[['objects', 'partitionsAssigned', 'partitionsTotal', 'bytesAssigned']] \
        .groupby('objects').agg(['max']).to_markdown())

    # Filter info
    print('\nFilter details')
    filter_expressions = operations[operations['operation'] == 'Filter'].explode('expressions')
    child_ops = pd.merge(filter_expressions, operations, how='left', left_on='id', right_on='parent', suffixes=['', '_child'])
    grandchild_ops = pd.merge(child_ops, operations, how='left', left_on='id_child', right_on='parent', suffixes=['', '_grandchild'])

    filter_ops = grandchild_ops[['id', 'operation', 'expressions', 'objects_child', 'objects_grandchild', 'expressions_child', 'expressions_grandchild']]
    filter_ops = filter_ops.explode('objects_child') \
        .explode('objects_grandchild') \
        .explode('expressions_child') \
        .explode('expressions_grandchild')

    filter_ops['table'] = filter_ops['objects_child'].combine_first(filter_ops['objects_grandchild'])
    filter_ops['column'] = np.where(filter_ops['expressions_child'].str.contains('joinKey:'), 
                                        filter_ops['expressions_grandchild'], filter_ops['expressions_child'])
    filter_ops['filter_type'] = np.where(filter_ops['expressions'].str.contains(' IN '), 'IN',
                                np.where(filter_ops['expressions'].str.contains('NOT\('), 'NOT',
                                np.where(filter_ops['expressions'].str.contains('CONTAINS\('), 'CONTAINS', 'NA')))

    print(filter_ops[['expressions', 'table', 'column', 'filter_type']].to_markdown())

    # print('\nFiltered columns')
    # print(operations[operations['operation'] == 'TableScan'].explode('objects').explode('expressions')[['objects', 'expressions']] \
    #     .groupby(['objects']).agg(
    #         columns=('expressions', set)
    #     ).to_markdown())

    # print('\nFilter expressions')
    # print(getValueCounts(column='expressions', operation_type='Filter', df=operations).to_markdown())

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
