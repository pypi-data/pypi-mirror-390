from typing import Annotated

from pydantic import Field

from adsdatahub.restapi.schemas._model import ExtraAllowModel
from adsdatahub.restapi.schemas.noise_impact import NoiseImpact


class ColumnInfoModel(ExtraAllowModel):
    """
    Metadata of a destination table column.

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/ColumnInfo
    """

    name: str
    """
    The column name
    """

    noise_impact: Annotated[NoiseImpact, Field(alias="noiseImpact")]
    """
    The noise impact message for this column.
    """

    impact_percentage: Annotated[float | None, Field(alias="impactPercentage")] = None
    """
    If applicable, the share this column contributes to the noise impact.
    """
