from datetime import datetime

from mmisp.db.models.post import Post


def generate_post() -> Post:
    return Post(
        date_created=datetime(2023, 11, 16, 0, 33, 46),
        date_modified=datetime(2023, 11, 16, 0, 33, 47),
        user_id=1,
        contents="my comment",
        post_id=0,
        thread_id=1,
    )
