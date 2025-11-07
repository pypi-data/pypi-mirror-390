import pandas as pd
from adsdatahub.client.query_job.query_job import QueryJob


class MockQueryJob(QueryJob):
    def __init__(self, dataframe: pd.DataFrame):
        self._dataframe = dataframe

    def to_dataframe(self) -> pd.DataFrame:
        return self._dataframe
