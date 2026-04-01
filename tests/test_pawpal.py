from datetime import timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def make_task(description="Task", time=420, duration=30, priority="high",
              pet_name="Buddy", frequency="daily"):
    return Task(
        description=description,
        duration_minutes=duration,
        priority=priority,
        time=time,
        pet_name=pet_name,
        frequency=frequency,
    )


def make_owner_with_tasks(*tasks, available=240):
    owner = Owner(name="Alex", daily_time_available=available)
    pet = Pet(name="Buddy", species="Dog")
    for t in tasks:
        pet.add_task(t)
    owner.add_pet(pet)
    return owner


# ─────────────────────────────────────────────
# Existing tests (kept)
# ─────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Whiskers", species="Cat")
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task(pet_name="Whiskers"))
    assert len(pet.get_tasks()) == 1


# ─────────────────────────────────────────────
# 1. Sorting correctness
# ─────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order must come back earliest-first."""
    scheduler = Scheduler()
    tasks = [
        make_task("Evening", time=18 * 60),
        make_task("Morning", time=7 * 60),
        make_task("Noon", time=12 * 60),
    ]
    result = scheduler.sort_by_time(tasks)
    times = [t.time for t in result]
    assert times == sorted(times)


def test_sort_by_time_tiebreaker_priority():
    """At the same start time, higher priority should come first."""
    scheduler = Scheduler()
    low = make_task("Low task", time=420, priority="low")
    high = make_task("High task", time=420, priority="high")
    result = scheduler.sort_by_time([low, high])
    assert result[0].description == "High task"


def test_sort_by_time_empty_list():
    """Sorting an empty list should return an empty list."""
    assert Scheduler().sort_by_time([]) == []


# ─────────────────────────────────────────────
# 2. Filtering
# ─────────────────────────────────────────────

def test_filter_by_pet_returns_only_matching_pet():
    scheduler = Scheduler()
    buddy_task = make_task("Walk", pet_name="Buddy")
    whiskers_task = make_task("Feed", pet_name="Whiskers")
    result = scheduler.filter_by_pet([buddy_task, whiskers_task], "Buddy")
    assert all(t.pet_name == "Buddy" for t in result)
    assert len(result) == 1


def test_filter_by_pet_no_match_returns_empty():
    scheduler = Scheduler()
    tasks = [make_task(pet_name="Buddy")]
    assert scheduler.filter_by_pet(tasks, "Nemo") == []


def test_filter_by_completed_pending_only():
    scheduler = Scheduler()
    done = make_task("Done")
    done.mark_complete()
    pending = make_task("Pending")
    result = scheduler.filter_by_completed([done, pending], completed=False)
    assert result == [pending]


def test_filter_by_completed_done_only():
    scheduler = Scheduler()
    done = make_task("Done")
    done.mark_complete()
    pending = make_task("Pending")
    result = scheduler.filter_by_completed([done, pending], completed=True)
    assert result == [done]


# ─────────────────────────────────────────────
# 3. Recurring task logic
# ─────────────────────────────────────────────

def test_daily_task_creates_next_occurrence_after_completion():
    """Completing a daily task must add one new task due tomorrow."""
    owner = make_owner_with_tasks(make_task(frequency="daily"))
    pet = owner.pets[0]
    task_number = pet.tasks[0].number
    today = pet.tasks[0].due_date

    Scheduler().mark_task_complete(owner, task_number)

    assert len(pet.tasks) == 2
    next_task = pet.tasks[1]
    assert next_task.completed is False
    assert next_task.due_date == today + timedelta(days=1)


def test_weekly_task_creates_next_occurrence_seven_days_out():
    owner = make_owner_with_tasks(make_task(frequency="weekly"))
    pet = owner.pets[0]
    task_number = pet.tasks[0].number
    today = pet.tasks[0].due_date

    Scheduler().mark_task_complete(owner, task_number)

    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_date == today + timedelta(days=7)


def test_monthly_task_creates_next_occurrence_thirty_days_out():
    owner = make_owner_with_tasks(make_task(frequency="monthly"))
    pet = owner.pets[0]
    task_number = pet.tasks[0].number
    today = pet.tasks[0].due_date

    Scheduler().mark_task_complete(owner, task_number)

    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_date == today + timedelta(days=30)


def test_recurring_next_task_preserves_description_and_time():
    """The spawned task must be an exact copy except for due_date and completed."""
    original = make_task("Morning walk", time=7 * 60, duration=30,
                         priority="high", frequency="daily")
    owner = make_owner_with_tasks(original)
    task_number = owner.pets[0].tasks[0].number

    Scheduler().mark_task_complete(owner, task_number)

    next_task = owner.pets[0].tasks[1]
    assert next_task.description == "Morning walk"
    assert next_task.time == 7 * 60
    assert next_task.duration_minutes == 30
    assert next_task.priority == "high"
    assert next_task.frequency == "daily"


def test_mark_task_complete_returns_false_for_unknown_number():
    owner = make_owner_with_tasks(make_task())
    result = Scheduler().mark_task_complete(owner, task_number=99999)
    assert result is False


# ─────────────────────────────────────────────
# 4. Conflict detection
# ─────────────────────────────────────────────

def test_detect_conflicts_flags_exact_same_start_time():
    """Two tasks starting at the same minute must trigger a warning."""
    t1 = make_task("Walk", time=420, duration=30)
    t2 = make_task("Feed", time=420, duration=10)
    warnings = Scheduler().detect_conflicts([t1, t2])
    assert len(warnings) >= 1


def test_detect_conflicts_flags_partial_overlap():
    """Task A (7:00–7:30) overlapping task B starting at 7:15 must warn."""
    t1 = make_task("Walk", time=7 * 60, duration=30)
    t2 = make_task("Feed", time=7 * 60 + 15, duration=10)
    warnings = Scheduler().detect_conflicts([t1, t2])
    assert len(warnings) >= 1


def test_detect_conflicts_catches_non_adjacent_overlap():
    """A overlaps C even when short task B sits between them in sort order."""
    # A: 7:00–9:00, B: 7:30–7:45, C: 8:30–9:30
    a = make_task("Long task A", time=7 * 60, duration=120)
    b = make_task("Short task B", time=7 * 60 + 30, duration=15)
    c = make_task("Task C", time=8 * 60 + 30, duration=60)
    warnings = Scheduler().detect_conflicts([a, b, c])
    descriptions = " ".join(warnings)
    assert "Long task A" in descriptions and "Task C" in descriptions


def test_detect_conflicts_no_warning_for_sequential_tasks():
    """Tasks that end exactly when the next one starts must not conflict."""
    t1 = make_task("Walk", time=420, duration=30)   # 7:00–7:30
    t2 = make_task("Feed", time=450, duration=10)   # 7:30–7:40
    warnings = Scheduler().detect_conflicts([t1, t2])
    assert warnings == []


def test_detect_conflicts_empty_list():
    assert Scheduler().detect_conflicts([]) == []


def test_detect_conflicts_single_task():
    assert Scheduler().detect_conflicts([make_task()]) == []


# ─────────────────────────────────────────────
# 5. Scheduler.generate_plan edge cases
# ─────────────────────────────────────────────

def test_generate_plan_skips_completed_tasks():
    done = make_task("Done task")
    done.mark_complete()
    owner = make_owner_with_tasks(done)
    plan, _ = Scheduler().generate_plan(owner)
    assert all(not t.completed for t in plan)


def test_generate_plan_respects_time_budget():
    """Total duration of scheduled tasks must not exceed owner's available time."""
    owner = make_owner_with_tasks(
        make_task("Task 1", duration=60),
        make_task("Task 2", duration=60),
        make_task("Task 3", duration=60),
        available=90,
    )
    plan, _ = Scheduler().generate_plan(owner)
    assert sum(t.duration_minutes for t in plan) <= 90


def test_generate_plan_empty_when_no_tasks():
    owner = Owner(name="Alex", daily_time_available=120)
    owner.add_pet(Pet(name="Buddy", species="Dog"))
    plan, _ = Scheduler().generate_plan(owner)
    assert plan == []


def test_generate_plan_prioritizes_high_over_low():
    """With limited time, high-priority tasks must be scheduled before low ones."""
    high = make_task("High priority", duration=80, priority="high")
    low = make_task("Low priority", duration=80, priority="low")
    owner = make_owner_with_tasks(high, low, available=100)
    plan, _ = Scheduler().generate_plan(owner)
    descriptions = [t.description for t in plan]
    assert "High priority" in descriptions
    assert "Low priority" not in descriptions
