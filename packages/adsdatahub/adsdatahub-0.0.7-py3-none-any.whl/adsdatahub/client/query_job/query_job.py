from abc import ABC, abstractmethod

import pandas as pd


class QueryJob(ABC):
    @abstractmethod
    def to_dataframe(self) -> pd.DataFrame: ...
