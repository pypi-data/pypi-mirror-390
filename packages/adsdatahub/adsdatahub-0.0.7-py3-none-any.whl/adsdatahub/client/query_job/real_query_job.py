import pandas as pd
from adsdatahub.client.query_job.query_job import QueryJob
from google.cloud import bigquery


class RealQueryJob(QueryJob):
    def __init__(self, job: bigquery.QueryJob) -> None:
        self._job = job

    def to_dataframe(self) -> pd.DataFrame:
        return self._job.to_dataframe()
