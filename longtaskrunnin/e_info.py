import uuid
from dataclasses import dataclass

# these should work identically in our program

@dataclass
class EInfo:
    uuid: str = str(uuid.uuid4())  # this will be the UUID of the "global" instance
    e_value: float = 0.0
    duration: float = 0.0
    iterations: int = 0


# class EInfo:
#     def __init__(self):
#         self.uuid: str = str(uuid.uuid4())  # this will be the UUID of the "global" instance
#         self.e_value: float = 0.0
#         self.duration: float = 0.0
#         self.iterations: int = 0
#
#     def __repr__(self):
#         return f"{self.uuid=},{self.e_value=},{self.duration=},{self.iterations=}"
