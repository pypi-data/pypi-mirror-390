from dataclasses import dataclass


@dataclass
class ObjectTimeInterval:
    start_time: int
    end_time: int
    object_count: int
    max_interval_size: int
