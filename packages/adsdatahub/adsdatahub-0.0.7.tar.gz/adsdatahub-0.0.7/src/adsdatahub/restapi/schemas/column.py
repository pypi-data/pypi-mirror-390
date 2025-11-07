from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.field_type import FieldTypeModel


class ColumnModel(ExtraAllowModel):
    columnId: str
    columnType: FieldTypeModel
