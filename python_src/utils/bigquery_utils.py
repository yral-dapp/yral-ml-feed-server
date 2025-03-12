import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import json
from utils.config import Config
from recommendation_service.consts import PROJECT_ID, STAGE_PROJECT_ID, use_stage


class BigQueryClient:
    def __init__(self):
        cfg = Config()
        self.logging = cfg.get('logging')
        if self.logging:
            print("Initializing BigQueryClient")
        service_cred = cfg.get('service_cred')
        service_acc_creds = json.loads(service_cred)
        credentials = service_account.Credentials.from_service_account_info(service_acc_creds)
        project_id = STAGE_PROJECT_ID if use_stage else PROJECT_ID
        self.client = bigquery.Client(credentials=credentials, project=project_id)

    def query(self, query):
        if self.logging:
            print(f"Running query: {query}")
        query_job = self.client.query(query)
        results = query_job.result()
        return self._to_dataframe(results)

    def _to_dataframe(self, results):
        rows = [dict(row) for row in results]
        return pd.DataFrame(rows)

if __name__ == '__main__':
    bq = BigQueryClient()
    res_df = bq.query("""
    SELECT
  *
FROM
  region-us.INFORMATION_SCHEMA.JOBS_BY_USER
WHERE
   creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 10 DAY)
--   limit 10;
             
             
             """)
    
    res_df.to_csv('bq_res.csv')