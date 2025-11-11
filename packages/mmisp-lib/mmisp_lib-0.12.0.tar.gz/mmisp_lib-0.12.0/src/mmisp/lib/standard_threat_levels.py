from mmisp.db.models.threat_level import ThreatLevel


def high() -> ThreatLevel:
    return ThreatLevel(
        id=1,
        name="High",
        description="*high* means sophisticated APT malware or 0-day attack",
        form_description="Sophisticated APT malware or 0-day attack",
    )


def medium() -> ThreatLevel:
    return ThreatLevel(id=2, name="Medium", description="'*medium* means APT malware", form_description="APT malware")


def low() -> ThreatLevel:
    return ThreatLevel(id=3, name="Low", description="'*low* means mass-malware", form_description="Mass-malware")


def undefined() -> ThreatLevel:
    return ThreatLevel(id=4, name="Undefined", description="'*undefined* no risk", form_description="No risk")


def get_standard_threat_level() -> list[ThreatLevel]:
    return [high(), medium(), low(), undefined()]
