# The functions defined in this script aim to provide the following functionality:

# 1.	Find out all the SELECT queries running in snowflake(Query History.sql)
# 2.	Find out and group, similar queries from it. (We also created a python script if you want to have a look -- Python-SimilarQueries_v2.ipynb)
# 3.	Generate the json readable format from explain plan (Explain Plan_Query.sql) 
# 4.	Find out tables, filters conditions, stats, etc from the explain plan so generated (Explain Plan generated.json)
# 5.	Suggest Wide table creation for the similar queries 

import sys
from src import functions as fx

file_path_argument = sys.argv[1]
fx.getExplainPlanAnalysis(file_path=file_path_argument)
