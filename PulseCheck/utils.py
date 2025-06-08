import string
import random
from datetime import datetime, timedelta
from functools import wraps

from flask import abort
from flask_login import current_user


def generate_invite(length=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))



def seed_mock_activities(team):
    from models import Activity, db
    from datetime import datetime, timedelta
    import random

    categories = ['Commit', 'Message', 'Pull Request', 'Blocker']

    for user in team.members:
        for i in range(7):  # simulate past 7 days
            for _ in range(random.randint(1, 4)):  # simulate 1–4 activities per day
                # Generate a datetime within the past i-th day, capped at now
                day = datetime.utcnow().date() - timedelta(days=i)
                random_time = timedelta(
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )
                generated_timestamp = datetime.combine(day, datetime.min.time()) + random_time
                now = datetime.utcnow()
                if generated_timestamp > now:
                    generated_timestamp = now - timedelta(minutes=random.randint(1, 10))  # ensure always in the past

                act = Activity(
                    user=user,
                    team=team,
                    timestamp=generated_timestamp,
                    category=random.choice(categories),
                    description="Simulated activity"
                )
                db.session.add(act)

    db.session.commit()


def creator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        team = current_user.team
        if current_user.id != team.creator_id:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

