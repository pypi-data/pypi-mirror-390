import importlib.metadata

from .client import Client as Client
from .client import MockClient as MockClient
from .client import RealClient as RealClient
from .client.customer.customer import CustomerClient as CustomerClient
from .client.query_job.query_job import QueryJob as QueryJob
from .client.query_result import QueryResult as QueryResult

__version__ = importlib.metadata.version(__name__)
