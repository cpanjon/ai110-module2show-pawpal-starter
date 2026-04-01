from pawpal_system import Task, Pet, Owner, Scheduler


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to a readable 12-hour time string."""
    hour = minutes // 60
    minute = minutes % 60
    period = "AM" if hour < 12 else "PM"
    if hour == 0:
        hour = 12
    elif hour > 12:
        hour -= 12
    return f"{hour}:{minute:02d} {period}"


def print_schedule(plan, explanation):
    print("=" * 45)
    print("         PawPal+ | Today's Schedule")
    print("=" * 45)

    if not plan:
        print("  No tasks scheduled for today.")
    else:
        for task in plan:
            start = minutes_to_time(task.time)
            end = minutes_to_time(task.time + task.duration_minutes)
            status = "[x]" if task.completed else "[ ]"
            print(f"  {status} {start} - {end}  |  {task.pet_name}")
            print(f"       {task.description}  ({task.priority_label} priority, {task.duration_minutes} min)")
            print()

    print("-" * 45)
    print("  Scheduler Notes:")
    for note in explanation:
        print(f"  - {note}")
    print("=" * 45)


def print_task_list(title: str, tasks: list) -> None:
    """Print a labeled list of tasks in a simple table format."""
    print(f"\n--- {title} ---")
    if not tasks:
        print("  (none)")
        return
    for t in tasks:
        status = "[x]" if t.completed else "[ ]"
        due = t.due_date.isoformat()
        print(f"  {status} #{t.number}  {minutes_to_time(t.time):10s}  {t.pet_name:10s}  "
              f"{t.description:25s}  ({t.priority_label}, {t.frequency}, due {due})")


def main():
    # --- Setup ---
    owner = Owner(name="Alex", daily_time_available=180)

    buddy = Pet(name="Buddy", species="Dog")
    whiskers = Pet(name="Whiskers", species="Cat")

    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    # --- Tasks added OUT OF ORDER intentionally ---
    whiskers.add_task(Task(
        description="Playtime",
        duration_minutes=20,
        priority="low",
        time=18 * 60,
        pet_name="Whiskers",
        frequency="daily",
    ))
    buddy.add_task(Task(
        description="Flea medication",
        duration_minutes=5,
        priority="medium",
        time=9 * 60,
        pet_name="Buddy",
        frequency="weekly",
    ))
    whiskers.add_task(Task(
        description="Vet appointment",
        duration_minutes=60,
        priority="high",
        time=10 * 60,
        pet_name="Whiskers",
        frequency="monthly",
    ))
    buddy.add_task(Task(
        description="Breakfast feeding",
        duration_minutes=10,
        priority="high",
        time=7 * 60 + 30,
        pet_name="Buddy",
        frequency="daily",
    ))
    whiskers.add_task(Task(
        description="Breakfast feeding",
        duration_minutes=5,
        priority="high",
        time=7 * 60 + 15,
        pet_name="Whiskers",
        frequency="daily",
    ))
    buddy.add_task(Task(
        description="Morning walk",
        duration_minutes=30,
        priority="high",
        time=7 * 60,
        pet_name="Buddy",
        frequency="daily",
    ))

    # --- Two tasks that INTENTIONALLY overlap for conflict detection demo ---
    # Both start at 9:00 AM and run 20 min — will trigger conflict warning
    buddy.add_task(Task(
        description="Bath time",
        duration_minutes=20,
        priority="medium",
        time=9 * 60,          # same start as Flea medication above
        pet_name="Buddy",
        frequency="weekly",
    ))

    scheduler = Scheduler()
    all_tasks = owner.get_all_tasks()

    # --- Demo: sort_by_time ---
    sorted_tasks = scheduler.sort_by_time(all_tasks)
    print_task_list("All Tasks Sorted by Time (before any completions)", sorted_tasks)

    # =========================================================
    # Demo: Recurring task — mark Buddy's morning walk complete
    # A new instance should appear with due_date = today + 1
    # =========================================================
    walk_number = next(t.number for t in buddy.tasks if t.description == "Morning walk")
    print(f"\n>>> Marking task #{walk_number} ('Morning walk') complete...")
    scheduler.mark_task_complete(owner, walk_number)

    buddy_tasks_after = scheduler.sort_by_time(scheduler.filter_by_pet(owner.get_all_tasks(), "Buddy"))
    print_task_list("Buddy's Tasks After Marking Walk Complete (next occurrence created)", buddy_tasks_after)

    # Also mark the monthly vet appointment complete — should spawn a new one 30 days out
    vet_number = next(t.number for t in whiskers.tasks if t.description == "Vet appointment")
    print(f"\n>>> Marking task #{vet_number} ('Vet appointment') complete...")
    scheduler.mark_task_complete(owner, vet_number)

    whiskers_tasks_after = scheduler.sort_by_time(scheduler.filter_by_pet(owner.get_all_tasks(), "Whiskers"))
    print_task_list("Whiskers's Tasks After Marking Vet Appt Complete (next occurrence created)", whiskers_tasks_after)

    # =========================================================
    # Demo: Conflict detection
    # =========================================================
    all_tasks_now = owner.get_all_tasks()
    pending = scheduler.filter_by_completed(all_tasks_now, completed=False)
    conflicts = scheduler.detect_conflicts(pending)

    print("\n--- Conflict Detection Results ---")
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts detected.")

    # --- Generate and print schedule ---
    plan, explanation = scheduler.generate_plan(owner)
    plan_sorted = scheduler.sort_by_time(plan)
    print_schedule(plan_sorted, explanation)


if __name__ == "__main__":
    main()
