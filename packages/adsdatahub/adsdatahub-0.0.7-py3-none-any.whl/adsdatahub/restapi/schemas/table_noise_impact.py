from enum import Enum


class TableNoiseImpact(str, Enum):
    """
    Impact of noise on table result confidence for UI warnings

    Reference: https://developers.google.com/ads-data-hub/reference/rest/v1/TableNoiseImpact
    """

    TABLE_NOISE_IMPACT_UNSPECIFIED = "TABLE_NOISE_IMPACT_UNSPECIFIED"
    """
    No noise impact specified
    """

    NOT_NOISED = "NOT_NOISED"
    """
    Table is not noised.
    """

    LOW_IMPACT = "LOW_IMPACT"
    """
    Noise has a low impact on the table's result confidence.
    """

    HIGH_IMPACT = "HIGH_IMPACT"
    """
    Noise has a high impact on the table's result confidence.
    """

    LOW_MEDIUM_IMPACT = "LOW_MEDIUM_IMPACT"
    """
    Noise has a low to medium impact on the table's result confidence.
    """

    MEDIUM_IMPACT = "MEDIUM_IMPACT"
    """
    Noise has a medium impact on the table's result confidence.
    """

    VERY_HIGH_IMPACT = "VERY_HIGH_IMPACT"
    """
    Noise has a very high impact on the table's result confidence.
    """
