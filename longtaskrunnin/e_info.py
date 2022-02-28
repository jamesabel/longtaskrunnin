import uuid
from dataclasses import dataclass


@dataclass
class EInfo:
    """
    Information on the calculation of "e" (the natural log).
    """
    uuid: str = str(uuid.uuid4())  # this will be the UUID of the "global" instance
    e_value: float = 0.0
    duration: float = 0.0
    iterations: int = 0
