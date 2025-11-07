import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class TestConvertPydanticParamTypes:
    def test_convert_pydantic_parameter_types(self):
        from adsdatahub.client.parameters.pydantic_parameters import (
            convert_pydantic_parameter_types,
        )

        class Params(BaseModel):
            string: str
            integer: int
            float: float
            boolean: bool
            date: datetime.date
            timestamp: datetime.datetime
            list_string: list[str]

        assert convert_pydantic_parameter_types(
            Params(
                string="string",
                integer=1,
                float=1.1,
                boolean=True,
                date=datetime.date.today(),
                timestamp=datetime.datetime.now(),
                list_string=["a", "b", "c"],
            )
        ) == {
            "string": {"type": {"type": "STRING"}},
            "integer": {"type": {"type": "INT64"}},
            "float": {"type": {"type": "FLOAT64"}},
            "boolean": {"type": {"type": "BOOL"}},
            "date": {"type": {"type": "DATE"}},
            "timestamp": {"type": {"type": "TIMESTAMP"}},
            "list_string": {
                "type": {
                    "arrayType": {
                        "type": "STRING",
                    }
                }
            },
        }

    def test_convert_pydantic_parameter_types_with_default(self):
        from adsdatahub.client.parameters.pydantic_parameters import (
            convert_pydantic_parameter_types,
        )

        now = datetime.datetime.now()

        class Params(BaseModel):
            string: Annotated[str, Field(default="default")]
            integer: int = 0
            real: float = 1.1
            boolean: bool = True
            date: Annotated[datetime.date, Field(default_factory=datetime.date.today)]
            timestamp: datetime.datetime = Field(default_factory=lambda: now)
            list_empty_string: Annotated[list[str], Field(default_factory=list)]
            list_some_float: Annotated[
                list[float], Field(default_factory=lambda: [1.1, 2.2, 3.3])
            ]
            # optional: Annotated[str | None, Field(default=None)]

        assert convert_pydantic_parameter_types(
            Params(
                string="string",
                integer=1,
                real=1.1,
                boolean=True,
                date=datetime.date.today(),
                timestamp=datetime.datetime.now(),
                list_empty_string=["a", "b", "c"],
                list_some_float=[],
                # optional=None,
            )
        ) == {
            "string": {
                "type": {"type": "STRING"},
                "defaultValue": {"value": "default"},
            },
            "integer": {"type": {"type": "INT64"}, "defaultValue": {"value": "0"}},
            "real": {"type": {"type": "FLOAT64"}, "defaultValue": {"value": "1.1"}},
            "boolean": {"type": {"type": "BOOL"}, "defaultValue": {"value": "TRUE"}},
            "date": {
                "type": {"type": "DATE"},
                "defaultValue": {"value": datetime.date.today().isoformat()},
            },
            "timestamp": {
                "type": {"type": "TIMESTAMP"},
                "defaultValue": {"value": now.isoformat()},
            },
            "list_empty_string": {
                "type": {"arrayType": {"type": "STRING"}},
                "defaultValue": {"arrayValue": {"values": []}},
            },
            "list_some_float": {
                "type": {"arrayType": {"type": "FLOAT64"}},
                "defaultValue": {
                    "arrayValue": {
                        "values": [{"value": "1.1"}, {"value": "2.2"}, {"value": "3.3"}]
                    }
                },
            },
            # "optional": {
            #     "type": {"type": "STRING"},
            #     "defaultValue": {"value": "NULL"},
            # },
        }
