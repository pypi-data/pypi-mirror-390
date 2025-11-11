from mmisp.db.models.blocklist import EventBlocklist


def generate_event_blocklist(event_uuid: str, event_info: str, event_orgc: int) -> EventBlocklist:
    return EventBlocklist(
        event_uuid=event_uuid,
        event_info=event_info,
        comment="This is a test comment",
        event_orgc=event_orgc,
    )
