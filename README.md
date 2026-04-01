# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler was extended with four algorithmic improvements beyond the basic plan generator:

- **Sort by time** — `Scheduler.sort_by_time()` orders tasks by start time, with priority and pet name as tiebreakers so the output is always deterministic.
- **Filter by pet or status** — `filter_by_pet()` and `filter_by_completed()` let you slice the task list without modifying it, making it easy to show only one pet's tasks or only pending work.
- **Recurring task auto-spawn** — when `mark_task_complete()` is called on a daily, weekly, or monthly task, a new instance is automatically created with the next due date calculated using Python's `timedelta`. Monthly tasks advance 30 days; daily tasks advance 1 day.
- **Full conflict detection** — `detect_conflicts()` compares every task pair (not just adjacent ones) so overlaps are never silently missed. Warnings include readable time ranges (e.g. `7:00 AM–7:30 AM`) and do not crash the program, letting the owner decide how to resolve them.

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest tests/test_pawpal.py -v
```

**What the tests cover (24 tests total):**

| Area | Tests |
|---|---|
| Sorting | Chronological order, priority tiebreaker, empty list |
| Filtering | By pet name, by completion status, no-match edge cases |
| Recurring tasks | Daily (+1 day), weekly (+7 days), monthly (+30 days), field preservation, unknown task number |
| Conflict detection | Exact same time, partial overlap, non-adjacent overlap, sequential (no false positive), empty/single list |
| Schedule generation | Skips completed tasks, respects time budget, empty pet, priority ordering |

**Confidence level: ★★★★☆**

Core scheduling logic is well covered. The main gap is the Streamlit UI layer (`app.py`), which is not tested — UI interactions would require an integration testing tool like Playwright.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
