from mmisp.db.models.blocklist import OrgBlocklist


def generate_org_blocklist(org_uuid: str, org_name: str) -> OrgBlocklist:
    return OrgBlocklist(
        org_uuid=org_uuid,
        org_name=org_name,
        comment="auto-generated org blocklist",
    )
