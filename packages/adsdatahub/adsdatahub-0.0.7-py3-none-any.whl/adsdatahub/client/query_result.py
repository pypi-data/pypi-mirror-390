from functools import cache

from adsdatahub.client.query_job.query_job import QueryJob
from adsdatahub.exceptions import AdsDataHubDestinationTableInfoNotFound
from adsdatahub.restapi.schemas.analysis_query_metadata import (
    AnalysisQueryMetadataModel,
)
from adsdatahub.restapi.schemas.destination_table_info import DestinationTableInfoModel
from adsdatahub.restapi.schemas.operation import (
    OperationModel,
)


class QueryResult:
    def __init__(
        self,
        *,
        dest_table: str,
        operation: OperationModel[AnalysisQueryMetadataModel],
        job: QueryJob,
    ) -> None:
        self.dest_table = dest_table
        self.operation = operation
        self.job = job

    @property
    @cache
    def table_info(self) -> DestinationTableInfoModel:
        if response := self.operation.response:
            for table in response.destination_tables:
                if table.table_path == self.dest_table:
                    return table

        raise AdsDataHubDestinationTableInfoNotFound(
            operation_id=self.operation.name.operation_id
        )
