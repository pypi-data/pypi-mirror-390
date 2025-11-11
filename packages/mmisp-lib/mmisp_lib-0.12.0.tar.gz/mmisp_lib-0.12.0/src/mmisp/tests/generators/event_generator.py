import datetime
import random
from time import time_ns

from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.lib import uuid
from mmisp.tests.generators.feed_generator import random_string


def generate_valid_random_create_event_data(orgc_id: int, org_id: int) -> AddEditGetEventDetails:
    return AddEditGetEventDetails(
        orgc_id=orgc_id,
        org_id=org_id,
        date=datetime.date(
            year=random.randint(2000, 2024), month=random.randint(1, 12), day=random.randint(1, 28)
        ).strftime("%Y-%m-%d"),
        threat_level_id=random.randint(1, 4),
        info="test event " + random_string(20),
        published=False,
        uuid=uuid.uuid(),
        attribute_count=random.randint(1, 50),
        analysis=random.randint(0, 2),
        distribution=3,
        proposal_email_lock=False,
        locked=False,
        sharing_group_id=1,
        disable_correlation=False,
        event_creator_email=f"generated-user+{time_ns()}@test.com",
        protected=False,
    )
