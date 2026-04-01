from dataclasses import dataclass, field
from typing import List, Tuple, ClassVar, Union
from datetime import date, timedelta
import json
from pathlib import Path


# -------------------------
# Data Models
# -------------------------

@dataclass
class Task:
    description: str
    duration_minutes: int
    priority: str  # low, medium, high
    time: int       # minutes since midnight
    pet_name: str
    frequency: str = "daily"  # daily, weekly, monthly
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    number: int = field(init=False)
    _counter: ClassVar[int] = 0
    _PRIORITY_RANKS: ClassVar[dict[str, int]] = {"low": 1, "medium": 2, "high": 3}

    def __post_init__(self) -> None:
        Task._counter += 1
        self.number = self._counter

    @property
    def priority_rank(self) -> int:
        pass

    @property
    def priority_label(self) -> str:
        pass

    def mark_complete(self) -> None:
        pass

    def mark_incomplete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_number: int) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass


@dataclass
class Owner:
    name: str
    daily_time_available: int  # minutes
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> List[Task]:
        pass

    def get_all_tasks_by_pet(self) -> dict:
        pass

    @classmethod
    def save_to_json(cls, owners: List["Owner"], file_path: str = "data.json") -> None:
        pass

    @classmethod
    def load_from_json(cls, file_path: str = "data.json") -> List["Owner"]:
        pass


# -------------------------
# Scheduling Logic
# -------------------------

class Scheduler:
    def generate_plan(self, owner: Owner) -> Tuple[List[Task], List[str]]:
        """Returns selected tasks for today and explanations for each decision."""
        pass

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        pass

    def filter_by_completed(self, tasks: List[Task], completed: bool) -> List[Task]:
        pass

    def mark_task_complete(self, owner: Owner, task_number: int) -> bool:
        """Marks a task complete and creates the next occurrence if recurring."""
        pass

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Returns warning messages for any overlapping tasks."""
        pass
