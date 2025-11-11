from mmisp.db.models.blocklist import GalaxyClusterBlocklist


def generate_galaxy_cluster_blocklist(cluster_uuid: str, cluster_orgc: int) -> GalaxyClusterBlocklist:
    return GalaxyClusterBlocklist(
        cluster_uuid=cluster_uuid,
        cluster_info="Test cluster info",
        comment="Test comment",
        cluster_orgc=cluster_orgc,
    )
