from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(
        description="Morning walk",
        duration_minutes=30,
        priority="high",
        time=420,
        pet_name="Buddy",
    )
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Whiskers", species="Cat")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task(
        description="Breakfast feeding",
        duration_minutes=5,
        priority="medium",
        time=450,
        pet_name="Whiskers",
    ))
    assert len(pet.get_tasks()) == 1
