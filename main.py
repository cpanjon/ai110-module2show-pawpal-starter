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


def main():
    # --- Setup ---
    owner = Owner(name="Alex", daily_time_available=120)

    buddy = Pet(name="Buddy", species="Dog")
    whiskers = Pet(name="Whiskers", species="Cat")

    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    # --- Tasks for Buddy ---
    buddy.add_task(Task(
        description="Morning walk",
        duration_minutes=30,
        priority="high",
        time=7 * 60,          # 7:00 AM
        pet_name="Buddy",
        frequency="daily",
    ))
    buddy.add_task(Task(
        description="Breakfast feeding",
        duration_minutes=10,
        priority="high",
        time=7 * 60 + 30,     # 7:30 AM
        pet_name="Buddy",
        frequency="daily",
    ))
    buddy.add_task(Task(
        description="Flea medication",
        duration_minutes=5,
        priority="medium",
        time=9 * 60,          # 9:00 AM
        pet_name="Buddy",
        frequency="weekly",
    ))

    # --- Tasks for Whiskers ---
    whiskers.add_task(Task(
        description="Breakfast feeding",
        duration_minutes=5,
        priority="high",
        time=7 * 60 + 15,     # 7:15 AM
        pet_name="Whiskers",
        frequency="daily",
    ))
    whiskers.add_task(Task(
        description="Vet appointment",
        duration_minutes=60,
        priority="high",
        time=10 * 60,         # 10:00 AM
        pet_name="Whiskers",
        frequency="monthly",
    ))
    whiskers.add_task(Task(
        description="Playtime",
        duration_minutes=20,
        priority="low",
        time=18 * 60,         # 6:00 PM
        pet_name="Whiskers",
        frequency="daily",
    ))

    # --- Generate and print schedule ---
    scheduler = Scheduler()
    plan, explanation = scheduler.generate_plan(owner)

    conflicts = scheduler.detect_conflicts(plan)
    if conflicts:
        print("\n  *** Conflict Warnings ***")
        for warning in conflicts:
            print(f"  ! {warning}")

    print_schedule(plan, explanation)


if __name__ == "__main__":
    main()
