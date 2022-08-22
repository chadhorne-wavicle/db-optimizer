select query_id,query_text
from table(information_schema.query_history(RESULT_LIMIT=>10000))
where query_type = 'SELECT'
order by start_time desc;
