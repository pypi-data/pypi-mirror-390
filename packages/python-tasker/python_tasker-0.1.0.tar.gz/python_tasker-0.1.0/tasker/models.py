from enum import IntEnum
from dataclasses import dataclass

class Prio(IntEnum):
  HIGH = 1
  MEDIUM = 2
  LOW = 3

@dataclass
class Task:
  task: str
  prio: Prio = Prio.MEDIUM
  archived: bool = False

