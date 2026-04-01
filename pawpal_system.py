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
        """Assign a unique auto-incrementing number to each task on creation."""
        Task._counter += 1
        self.number = self._counter

    @property
    def priority_rank(self) -> int:
        """Return the numeric rank of this task's priority (1=low, 2=medium, 3=high)."""
        return self._PRIORITY_RANKS[self.priority]

    @property
    def priority_label(self) -> str:
        """Return the priority as a title-cased string (e.g. 'High')."""
        return self.priority.title()

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_number: int) -> None:
        """Remove the task matching the given task number from this pet's list."""
        for task in self.tasks:
            if task.number == task_number:
                self.tasks.remove(task)
                return

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks


@dataclass
class Owner:
    name: str
    daily_time_available: int  # minutes
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of every task across all of this owner's pets."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_all_tasks_by_pet(self) -> dict:
        """Return a dict mapping each pet's name to its list of tasks."""
        tasks_by_pet = {}
        for pet in self.pets:
            tasks_by_pet[pet.name] = pet.get_tasks()
        return tasks_by_pet

    @classmethod
    def save_to_json(cls, owners: List["Owner"], file_path: str = "data.json") -> None:
        """Serialize a list of owners (with their pets and tasks) to a JSON file."""
        data = {"owners": []}
        for owner in owners:
            owner_payload = {
                "name": owner.name,
                "daily_time_available": owner.daily_time_available,
                "pets": [],
            }
            for pet in owner.pets:
                pet_payload = {
                    "name": pet.name,
                    "species": pet.species,
                    "tasks": [],
                }
                for task in pet.tasks:
                    pet_payload["tasks"].append({
                        "number": task.number,
                        "description": task.description,
                        "duration_minutes": task.duration_minutes,
                        "priority": task.priority,
                        "time": task.time,
                        "pet_name": task.pet_name,
                        "frequency": task.frequency,
                        "completed": task.completed,
                        "due_date": task.due_date.isoformat(),
                    })
                owner_payload["pets"].append(pet_payload)
            data["owners"].append(owner_payload)

        Path(file_path).write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load_from_json(cls, file_path: str = "data.json") -> List["Owner"]:
        """Load and reconstruct a list of owners from a JSON file, restoring task counters."""
        path = Path(file_path)
        if not path.exists():
            return []

        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return []

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return []

        owners: List[Owner] = []
        max_task_number = 0

        for owner_data in payload.get("owners", []):
            owner = Owner(
                name=owner_data.get("name", ""),
                daily_time_available=int(owner_data.get("daily_time_available", 0)),
            )
            for pet_data in owner_data.get("pets", []):
                pet = Pet(
                    name=pet_data.get("name", ""),
                    species=pet_data.get("species", "Other"),
                )
                for task_data in pet_data.get("tasks", []):
                    due_date_raw = task_data.get("due_date", date.today().isoformat())
                    try:
                        due_date_value = date.fromisoformat(due_date_raw)
                    except ValueError:
                        due_date_value = date.today()

                    task = Task(
                        description=task_data.get("description", ""),
                        duration_minutes=int(task_data.get("duration_minutes", 0)),
                        priority=task_data.get("priority", "low"),
                        time=int(task_data.get("time", 0)),
                        pet_name=task_data.get("pet_name", pet.name),
                        frequency=task_data.get("frequency", "daily"),
                        completed=bool(task_data.get("completed", False)),
                        due_date=due_date_value,
                    )
                    task.number = int(task_data.get("number", task.number))
                    max_task_number = max(max_task_number, task.number)
                    pet.add_task(task)
                owner.add_pet(pet)
            owners.append(owner)

        Task._counter = max(Task._counter, max_task_number)
        return owners


# -------------------------
# Scheduling Logic
# -------------------------

class Scheduler:
    def generate_plan(self, owner: Owner) -> Tuple[List[Task], List[str]]:
        """
        Returns:
        - plan: tasks selected for today
        - explanation: reasons why tasks were selected or skipped
        """
        available_minutes = owner.daily_time_available
        explanation: List[str] = []
        selected: List[Task] = []

        tasks = owner.get_all_tasks()
        # Sort by priority (high to low), then by start time (earlier first)
        tasks.sort(key=lambda t: (-t.priority_rank, t.time))

        for task in tasks:
            if task.completed:
                explanation.append(f"Skipped '{task.description}' (already completed).")
                continue
            if task.duration_minutes > available_minutes:
                explanation.append(f"Skipped '{task.description}' (not enough time).")
                continue
            selected.append(task)
            available_minutes -= task.duration_minutes
            explanation.append(f"Scheduled '{task.description}' (priority {task.priority_label}).")

        return selected, explanation

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by start time (earliest first)."""
        return sorted(tasks, key=lambda t: t.time)

    def filter_by_completed(self, tasks: List[Task], completed: bool) -> List[Task]:
        """Return only tasks whose completed status matches the given value."""
        return [t for t in tasks if t.completed == completed]

    def mark_task_complete(self, owner: Owner, task_number: int) -> bool:
        """
        Marks a task complete by task_number.
        If the task is daily or weekly, creates the next occurrence on the same pet.
        Returns True if found and marked; False otherwise.
        """
        for pet in owner.pets:
            for task in pet.tasks:
                if task.number == task_number:
                    task.mark_complete()

                    # Schedule next occurrence for recurring tasks
                    if task.frequency in ("daily", "weekly"):
                        days = 1 if task.frequency == "daily" else 7
                        next_due = task.due_date + timedelta(days=days)

                        next_task = Task(
                            description=task.description,
                            duration_minutes=task.duration_minutes,
                            priority=task.priority,
                            time=task.time,
                            pet_name=task.pet_name,
                            frequency=task.frequency,
                            completed=False,
                            due_date=next_due,
                        )
                        pet.add_task(next_task)

                    return True
        return False

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """
        Returns warning messages for any overlapping tasks.
        Does not raise errors or stop execution.
        """
        warnings: List[str] = []
        tasks_sorted = sorted(tasks, key=lambda t: t.time)

        for i in range(len(tasks_sorted) - 1):
            current = tasks_sorted[i]
            nxt = tasks_sorted[i + 1]

            current_end = current.time + current.duration_minutes
            if nxt.time < current_end:
                warnings.append(
                    f"Time conflict: '{current.description}' ({current.pet_name}) "
                    f"overlaps with '{nxt.description}' ({nxt.pet_name})."
                )

        return warnings
