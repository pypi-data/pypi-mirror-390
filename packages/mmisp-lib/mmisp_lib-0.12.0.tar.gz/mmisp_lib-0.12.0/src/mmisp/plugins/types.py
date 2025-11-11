from enum import StrEnum


class PluginType(StrEnum):
    """
    Enum encapsulating possible plugin types.
    """

    CORRELATION = "correlation"
    """Type for plugins specifically made for correlation jobs."""
    ENRICHMENT = "enrichment"
    """Type for plugins specifically made for enrichment jobs."""


class CorrelationPluginType(StrEnum):
    """
    Enum for the type of correlation plugin.
    """

    ALL_CORRELATIONS = "all"
    SELECTED_CORRELATIONS = "selected"
    OTHER = "other"


class EnrichmentPluginType(StrEnum):
    """
    Enum describing all possible enrichment plugin types.
    """

    EXPANSION = "expansion"
    """Enrichment Plugins of this type generate new attributes that can be attached to a MISP-Event
    to add additional information permanently."""
    HOVER = "hover"
    """Enrichment Plugins of this type generate information that is usually only displayed once
    and should not be stored permanently in the database."""
