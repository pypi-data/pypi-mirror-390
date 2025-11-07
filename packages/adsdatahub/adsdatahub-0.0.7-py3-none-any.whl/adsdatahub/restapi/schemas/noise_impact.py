from enum import Enum


class NoiseImpact(str, Enum):
    """
    LINT.IfChange(ColumnNoiseImpact) Impact of noise on column result confidence for UI warnings.

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/ColumnNoiseImpact
    """

    COLUMN_NOISE_IMPACT_UNSPECIFIED = "COLUMN_NOISE_IMPACT_UNSPECIFIED"
    """
    No noise impact specified.
    """

    NOT_NOISED = "NOT_NOISED"
    """
    Column is not noised.
    """

    LOW_IMPACT = "LOW_IMPACT"
    """
    Noise has a low impact on the column's result confidence.
    """

    HIGH_IMPACT = "HIGH_IMPACT"
    """
    Noise has a high impact on the column's result confidence.
    """
