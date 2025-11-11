import random
import string

from mmisp.api_schemas.feeds import FeedCreateBody


def generate_number_as_str() -> str:
    number = random.randint(1, 4)
    return str(number)


def generate_ids_as_str() -> str:
    id_str = random.randint(1, 10)
    return str(id_str)


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_valid_required_feed_data() -> FeedCreateBody:
    return FeedCreateBody(
        name="gvrfd_" + random_string(),
        provider=random_string(),
        url=f"http://{random_string()}.com",
    )


def generate_random_ipv4() -> str:
    return ".".join(str(random.randint(0, 255)) for _ in range(4))


def generate_valid_feed_data() -> FeedCreateBody:
    return FeedCreateBody(
        name="gvfd_" + random_string(),
        provider=random_string(),
        url=f"http://{random_string()}.com",
        rules=random_string(),
        enabled=random.choice([True, False]),
        distribution=1,
        sharing_group_id=0,
        tag_id=0,
        default=random.choice([True, False]),
        source_format=random_string(),
        fixed_event=random.choice([True, False]),
        delta_merge=random.choice([True, False]),
        event_id=0,
        publish=random.choice([True, False]),
        override_ids=random.choice([True, False]),
        settings=random_string(),
        input_source=random_string(),
        delete_local_file=random.choice([True, False]),
        lookup_visible=random.choice([True, False]),
        headers=random_string(),
        caching_enabled=random.choice([True, False]),
        force_to_ids=random.choice([True, False]),
        orgc_id=0,
    )


def generate_random_valid_feed_data() -> FeedCreateBody:
    return FeedCreateBody(
        name="grvfd_" + random_string(),
        provider=random_string(),
        url=f"http://{random_string()}.com",
        enabled=True,
        distribution=1,
        sharing_group_id=0,
        tag_id=0,
    )
