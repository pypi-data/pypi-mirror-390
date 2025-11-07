from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.column import ColumnModel
from adsdatahub.restapi.schemas.query_type import QueryType


class TempTableModel(ExtraAllowModel):
    """
    Ads Data Hub クエリによって作成された一時テーブルを定義します。
    一時テーブルは、Ads Data Hub クエリで CREATE TABLE temp_table AS (...) を使用して作成されます。
    一時テーブルは、更新が必要になるまで 72 時間アクティブ状態が維持されます。

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/customers.tempTables?hl=ja#TempTable
    """

    name: str
    """
    テーブルを一意に識別する名前。

    形式は customer/[お客様 ID]/tempTables/[analysis_query_id] です。
    リソース ID はサーバーによって生成されます。
    """

    tablePath: str
    """
    完全修飾されたテーブルパス。例: 'tmp.table'
    """

    adsDataCustomerId: str
    """
    リンクされた一時 Data Hub のお客様 ID（元の一時テーブルのクエリの実行時に使用）。
    """

    matchDataCustomerId: str
    """
    リンクされた一時 Data Hub のお客様 ID（元の一時テーブルのクエリの実行時に使用）。
    """

    queryType: QueryType
    """
    テーブルを作成したクエリのタイプ。

    一時テーブルにアクセスできるのは、usageQueryTypes が設定されていない限り、同じタイプのクエリに限られます。
    """

    usableQueryTypes: list[QueryType]
    """
    この一時テーブルにアクセスできるクエリの種類。

    空の場合、この一時テーブルにはその queryType と同じ型のクエリのみがアクセスできます。
    """

    columns: list[ColumnModel]
    """
    テーブル列のリスト。
    """

    createTime: str
    """
    一時テーブルが作成されたときのタイムスタンプ（マイクロ単位）。

    RFC3339 UTC の Zulu 形式のタイムスタンプ。
    ナノ秒単位で、小数点以下は 9 桁までとなります。
    （例: "2014-10-02T15:01:23Z"、"2014-10-02T15:01:23.045123456Z"）。
    """

    operation: str
    """
    一時テーブルを作成したオペレーション。

    形式: operations/[jobId]
    """
