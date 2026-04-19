from d20.db import get_db


def increment_count(owner_id, counter_id):
    db = get_db()
    next_num = db.execute(
        "select coalesce(max(count_idx), 0) + 1 from Counter where owner_id = ? and counter_id = ?",
        (owner_id, counter_id),
    ).fetchone()[0]
    db.execute(
        f"insert into Counter (counter_id, count_idx, owner_id) values (?, ?, ?)",
        (counter_id, next_num, owner_id),
    )
    db.commit()
    return next_num


def get_counts(owner_id, counter_id):
    return (
        get_db()
        .execute(
            "select * from Counter where owner_id = ? and counter_id = ?",
            (owner_id, counter_id),
        )
        .fetchall()
    )


# def create_new_counter(owner_id, counter_id):
#     if counter_exists(owner_id, counter_id):
#         return
#
#
# def counter_exists(owner_id, counter_id):
#     db = get_db()
#     t = db.execute(
#         "select * from Counter where owner_id = ? and counter_id = ?",
#         (owner_id, counter_id),
#     )
#     if len(t) == 0:
#         return False
#     else:
#         return True
