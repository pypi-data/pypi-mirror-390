from typing import TypeAlias

from httpx._types import TimeoutTypes as TimeoutTypes
from httpx._types import URLTypes as URLTypes

CustomerId: TypeAlias = str
"""
クエリを実行する顧客のID。基本的には数値の文字列だが、"global" という文字列が変えることもある。

ex. "1234567890", "global"
"""

AnalysisQueryId: TypeAlias = str
"""
クエリのリソースID。

ex. "00d30ae989fa487d9a96e15afc244770"
"""

OperationId: TypeAlias = str
"""
オペレーションの一意なID。

ex. "e3646136d4b14f92b5560286c20306f0"
"""
