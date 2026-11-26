import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

SEED = 2026
HISTORY_DAYS = 90


@dataclass
class SeedContext:
    rng: random.Random
    now: datetime
    start: datetime
    users: list = field(default_factory=list)
    drivers: list = field(default_factory=list)
    alerts: list = field(default_factory=list)
    vehicles: list = field(default_factory=list)
    devices: list = field(default_factory=list)
    services: list = field(default_factory=list)
    locations: list = field(default_factory=list)
    trips: list = field(default_factory=list)
    positions: list = field(default_factory=list)


def new_context() -> SeedContext:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return SeedContext(
        rng=random.Random(SEED),
        now=now,
        start=now - timedelta(days=HISTORY_DAYS),
    )


def random_between(rng: random.Random, start: datetime, end: datetime) -> datetime:
    seconds = (end - start).total_seconds()
    return (start + timedelta(seconds=rng.uniform(0, seconds))).replace(microsecond=0)