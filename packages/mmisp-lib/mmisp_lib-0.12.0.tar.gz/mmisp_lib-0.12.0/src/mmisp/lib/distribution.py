from enum import IntEnum


class DistributionLevels(IntEnum):
    OWN_ORGANIZATION = 0
    COMMUNITY = 1
    CONNECTED_COMMUNITIES = 2
    ALL_COMMUNITIES = 3


class GalaxyDistributionLevels(IntEnum):
    OWN_ORGANIZATION = 0
    COMMUNITY = 1
    CONNECTED_COMMUNITIES = 2
    ALL_COMMUNITIES = 3
    SHARING_GROUP = 4


class EventDistributionLevels(IntEnum):
    OWN_ORGANIZATION = 0
    COMMUNITY = 1
    CONNECTED_COMMUNITIES = 2
    ALL_COMMUNITIES = 3
    SHARING_GROUP = 4


class AttributeDistributionLevels(IntEnum):
    OWN_ORGANIZATION = 0
    COMMUNITY = 1
    CONNECTED_COMMUNITIES = 2
    ALL_COMMUNITIES = 3
    SHARING_GROUP = 4
    INHERIT_EVENT = 5
