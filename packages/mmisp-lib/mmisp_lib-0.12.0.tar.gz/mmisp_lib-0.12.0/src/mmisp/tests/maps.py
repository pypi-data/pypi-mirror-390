from collections import Counter, defaultdict
from itertools import product

access_test_objects_orgs = [f"org{i}" for i in range(1, 4)]

access_test_objects_users = [f"user_org{i}_{role}" for i in range(1, 4) for role in ["publisher", "read_only", "user"]]
access_test_objects_users.append("site_admin_user")

access_test_objects_user_by_org = {
    f"org{i}": [f"user_org{i}_{role}" for role in ["publisher", "read_only", "user"]] for i in range(1, 4)
}

access_test_objects_sg_by_org = {
    "org1": ["sg_org1_org2", "sg_org1_org3"],
    "org2": ["sg_org1_org2", "sg_org2_org3"],
    "org3": ["sg_org1_org3", "sg_org2_org3"],
}


def event_distribution_by_org(org):
    for i in range(0, 4):
        yield i
    for sg in access_test_objects_sg_by_org[org]:
        yield f"4_{sg}"


#    "attribute_org3_4_sg_org2_org3_published_5"
def attributes_by_event(eventkey):
    suffix = eventkey[len("event_") :]
    for i in range(0, 4):
        yield f"attribute_{suffix}_{i}"
    yield f"attribute_{suffix}_5"

    org = eventkey[6:10]
    for sg in access_test_objects_sg_by_org[org]:
        yield f"attribute_{suffix}_4_{sg}"


def user_in_asg(user, attribute):
    start_asg = attribute.rfind("_4_") + 3
    user_org = user[5:9]
    asg = attribute[start_asg:]

    return user_org in asg


def user_access_to_attribute(user, attribute):
    if user == "site_admin_user":
        return True

    user_org = user[5:9]
    event_org = attribute[10:14]
    if user_org == event_org:
        return True
    if attribute[-1] == "0":
        return False
    if attribute[-2:] in ["_1", "_2", "_3"]:
        return "unpublished" not in attribute
    if attribute[-1] == "5":
        return True  # assume user has access to event
    else:
        return user_in_asg(user, attribute)


access_test_objects_event_by_org = {
    f"org{i}": [
        f"event_org{i}_{edl}_{pub}published" for edl in event_distribution_by_org(f"org{i}") for pub in ["", "un"]
    ]
    for i in range(1, 3)
}
access_test_objects_event_by_org["org3"] = []


site_admin_access = [
    ("site_admin_user", event) for event_list in access_test_objects_event_by_org.values() for event in event_list
]

public_events = [
    event
    for event_list in access_test_objects_event_by_org.values()
    for event in event_list
    if any(f"_{dl}_published" in event for dl in range(1, 4))
]

all_possible_user_event_pairs = set(
    (user, event)
    for user in access_test_objects_users
    for event_list in access_test_objects_event_by_org.values()
    for event in event_list
)
all_possible_user_attribute_pairs = set(
    (user, attribute) for (user, event) in all_possible_user_event_pairs for attribute in attributes_by_event(event)
)

access_test_objects_shared_events_by_org = {
    org: [
        event
        for other_org in ["org1", "org2"]
        if other_org != org
        for event in access_test_objects_event_by_org[other_org]
        if any(sg in event for sg in access_test_objects_sg_by_org.get(org, []))
        if "unpublished" not in event
    ]
    for org in ["org1", "org2"]
}

access_test_object_user_event_sharing_group = [
    (user, event)
    for org, events in access_test_objects_shared_events_by_org.items()
    for user, event in product(access_test_objects_user_by_org[org], events)
]

access_test_object_user_event_own_org = [
    (user, event)
    for org, users in access_test_objects_user_by_org.items()
    for user in users
    for event in access_test_objects_event_by_org[org]
]

access_test_objects_public_user_event = [(user, event) for user in access_test_objects_users for event in public_events]

### Unfiltered lists

user_event_access_expect_granted = list(
    set(
        access_test_object_user_event_sharing_group
        + access_test_object_user_event_own_org
        + site_admin_access
        + access_test_objects_public_user_event
    )
)
user_event_access_expect_denied = list(all_possible_user_event_pairs - set(user_event_access_expect_granted))

user_event_edit_expect_granted = [
    (user, event) for user, event in access_test_object_user_event_own_org if "read_only" not in user
]
user_event_edit_expect_granted.extend(site_admin_access)
user_event_edit_expect_denied = list(all_possible_user_event_pairs - set(user_event_edit_expect_granted))

user_event_publish_expect_granted = [
    (user, event) for user, event in access_test_object_user_event_own_org if "publisher" in user
]
user_event_publish_expect_granted.extend(site_admin_access)
user_event_publish_expect_denied = list(all_possible_user_event_pairs - set(user_event_publish_expect_granted))


user_attribute_access_expect_granted = [
    (user, attribute)
    for (user, event) in user_event_access_expect_granted
    for attribute in attributes_by_event(event)
    if user_access_to_attribute(user, attribute)
]

user_attribute_access_expect_denied = list(
    all_possible_user_attribute_pairs - set(user_attribute_access_expect_granted)
)

user_attribute_edit_expect_granted = [
    (user, attribute)
    for (user, event) in user_event_edit_expect_granted
    for attribute in attributes_by_event(event)
    if user_access_to_attribute(user, attribute)
]

user_attribute_edit_expect_denied = list(all_possible_user_attribute_pairs - set(user_attribute_edit_expect_granted))

user_to_event_count = list(Counter(user for user, event in user_event_access_expect_granted).items())
user_to_event_count.sort()

grouped = defaultdict(list)
for user, event in user_event_access_expect_granted:
    grouped[user].append(event)

user_to_events = list(grouped.items())
user_to_events.sort()

grouped = defaultdict(list)
for user, attribute in user_attribute_access_expect_granted:
    grouped[user].append(attribute)

user_to_attributes = list(grouped.items())
user_to_attributes.sort()


### Filter List:
def user_filter(elem):
    user, _ = elem
    if user.startswith("user_org1"):
        return True
    if user == "site_admin_user":
        return True
    return False


def event_filter(elem):
    user, event = elem
    if user.startswith("user_org1"):
        if event.startswith("event_org1"):
            return True
        if event.startswith("event_org2"):
            return True
    if user == "site_admin_user":
        if event.startswith("event_org1"):
            return True
    return False


def attribute_filter(elem):
    user, attribute = elem
    if user.startswith("user_org1"):
        if attribute.startswith("attribute_org1"):
            return True
        if attribute.startswith("attribute_org2"):
            return True
    if user == "site_admin_user":
        if attribute.startswith("attribute_org1"):
            return True
    return False


user_to_events = list(filter(user_filter, user_to_events))
user_to_events.sort()

user_to_attributes = list(filter(user_filter, user_to_attributes))
user_to_attributes.sort()

access_test_objects_user_event_access_expect_granted = list(filter(event_filter, user_event_access_expect_granted))
access_test_objects_user_event_access_expect_granted.sort()

access_test_objects_user_event_access_expect_denied = list(filter(event_filter, user_event_access_expect_denied))
access_test_objects_user_event_access_expect_denied.sort()

access_test_objects_user_event_edit_expect_granted = list(filter(event_filter, user_event_edit_expect_granted))
access_test_objects_user_event_edit_expect_granted.sort()

access_test_objects_user_event_edit_expect_denied = list(filter(event_filter, user_event_edit_expect_denied))
access_test_objects_user_event_edit_expect_denied.sort()

access_test_objects_user_event_publish_expect_granted = list(filter(event_filter, user_event_publish_expect_granted))
access_test_objects_user_event_publish_expect_granted.sort()

access_test_objects_user_event_publish_expect_denied = list(filter(event_filter, user_event_publish_expect_denied))
access_test_objects_user_event_publish_expect_denied.sort()

access_test_objects_user_attribute_access_expect_granted = list(
    filter(attribute_filter, user_attribute_access_expect_granted)
)
access_test_objects_user_attribute_access_expect_granted.sort()

access_test_objects_user_attribute_access_expect_denied = list(
    filter(attribute_filter, user_attribute_access_expect_denied)
)
access_test_objects_user_attribute_access_expect_denied.sort()


access_test_objects_user_attribute_edit_expect_granted = list(
    filter(attribute_filter, user_attribute_edit_expect_granted)
)
access_test_objects_user_attribute_edit_expect_granted.sort()

access_test_objects_user_attribute_edit_expect_denied = list(
    filter(attribute_filter, user_attribute_edit_expect_denied)
)
access_test_objects_user_attribute_edit_expect_denied.sort()
