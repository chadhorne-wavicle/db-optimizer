import os
import json
import numpy as np
import pandas as pd

# from dotenv import load_dotenv
from snowflake.snowpark.session import Session

# Prints explain plan analysis to stdout
# Takes the file path to the explain plan file
def getExplainPlanAnalysis(file_path):
    global_stats, operations = readExplainPlanFile(file_path)

    print('\nGlobal Stats')
    print(global_stats.to_markdown(index=False))

    # Number of each operation type
    operation_summary = operations['operation'].value_counts()
    print('\nCount of operations')
    print(operation_summary.to_markdown())

    # Get number of table scans for wide table suggestion
    num_tablescans = operation_summary[operation_summary.index == 'TableScan'][0]

    if (num_tablescans > 4):
        print(f'\n***There were {num_tablescans} tables scanned during this query*** \
        \n***Consider joining them into a wide table to improve query performance***')

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
                                np.where(filter_ops['expressions'].str.contains(' = '), 'EQUALS',
                                np.where(filter_ops['expressions'].str.contains('CONTAINS\('), 'CONTAINS', 'OTHER'))))

    print(filter_ops[['expressions', 'table', 'column', 'filter_type']].to_markdown())

    print('\nSort expressions')
    print(getValueCounts(column='expressions', operation_type='Sort', df=operations).to_markdown())


# Returns history of select queries from Snowflake
def getQueryHistory(account, user, password, warehouse, database, schema):
    #TODO Get query history from Snowflake DW
    
    # Set Snowflake credentials
    snowflake_params =  {
        'account': account,
        'user': user,
        'password': password,
        'warehouse': warehouse,
        'database': database,
        'schema': schema
    }

    # Get Snowflake query history
    query_string = """
    select query_id,query_text
    from table(information_schema.query_history(RESULT_LIMIT=>10000))
    where query_type = 'SELECT'
    order by start_time desc;
    """
    session = Session.builder.configs(snowflake_params).create()

    query_history_df = session.sql(query_string)

    return query_history_df

# Get queries that are similar and group together
def getSimilarQueries(df):
    #TODO Research SQL analysis libraries for this
    df['QUERY_TEXT_New'] = df['QUERY_TEXT'].replace(r'\r+|\n+|\t+|\s+',' ', regex=True)
    df['QUERY_TEXT_New'] = df['QUERY_TEXT_New'].replace(r'"','', regex=True) # as separate  as replacing it with no space
    df['QUERY_TEXT_New'] = df['QUERY_TEXT_New'].replace(r' +',' ', regex=True) # as separate cmd as relacing it no space
    df['QUERY_TEXT_New2'] = df['QUERY_TEXT_New'].replace(r"'.*?'", "''", regex=True)
    

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
