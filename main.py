# The functions defined in this script aim to provide the following functionality:

# 1.	Find out all the SELECT queries running in snowflake(Query History.sql)
# 2.	Find out and group, similar queries from it. (We also created a python script if you want to have a look -- Python-SimilarQueries_v2.ipynb)
# 3.	Generate the json readable format from explain plan (Explain Plan_Query.sql) 
# 4.	Find out tables, filters conditions, stats, etc from the explain plan so generated (Explain Plan generated.json)
# 5.	Suggest Wide table creation for the similar queries 

import os
import sys
import argparse
from dotenv import load_dotenv

from src import functions as fx

# Define arguments
arg_parser = argparse.ArgumentParser(prog='db-optimizer',
    description='Analyze query history and identify opportunities to improve performance')

arg_parser.add_argument('ExplainPlanFilePath',
                        metavar='explain_plan_file_path',
                        type=str,
                        help='the path to the explain plan file')

# Parse arguments
args = arg_parser.parse_args()
explain_plan_file_path = args.ExplainPlanFilePath

if not os.path.isfile(explain_plan_file_path):
    print('The file does not exist')
    sys.exit()

# Get environment variables
load_dotenv()
ACCOUNT = os.environ.get('ACCOUNT')
USER = os.environ.get('USER')
PASSWORD = os.environ.get('PASSWORD')
WAREHOUSE = os.environ.get('WAREHOUSE')
DATABASE = os.environ.get('DATABASE')
SCHEMA = os.environ.get('SCHEMA')

# Pull query history from Snowflake DW
query_history = fx.getQueryHistory(account=ACCOUNT,
                                    user=USER,
                                    password=PASSWORD,
                                    warehouse=WAREHOUSE,
                                    database=DATABASE,
                                    schema=SCHEMA)

#TODO Identify similar queries from query history results

#TODO Generate the Explain Plan file for a given query

# Analyze the Explain Plan
# fx.getExplainPlanAnalysis(file_path=explain_plan_file_path)
