from dataclasses import dataclass


@dataclass
class KBIteratorConfig:
    max_total_count: int = 1000
    earliest_created_time: int = 1609448400  # Fri Jan 01 2021 00:00:00 GMT+0300
