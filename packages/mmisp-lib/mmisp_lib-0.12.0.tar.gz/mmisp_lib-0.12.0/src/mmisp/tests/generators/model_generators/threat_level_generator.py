from mmisp.db.models.threat_level import ThreatLevel
from mmisp.lib.uuid import uuid


def generate_threat_level() -> ThreatLevel:
    return ThreatLevel(
        name=uuid(),
        description="This is a test description",
        form_description="This is a test form description",
    )
