import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

DATA_FILE = "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session State Initialization ---
# Each key is only created once per browser session; reruns skip these blocks.
if "owner" not in st.session_state:
    # Load persisted data on first run; fall back to None if file is missing/empty.
    loaded = Owner.load_from_json(DATA_FILE)
    st.session_state.owner = loaded[0] if loaded else None

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

# -------------------------
# Step 1: Create Owner
# -------------------------
st.subheader("Owner Setup")

owner_name = st.text_input("Owner name", value="Jordan")
daily_minutes = st.number_input("Minutes available today", min_value=10, max_value=480, value=120)

if st.button("Save Owner"):
    # Build a fresh Owner and store it in the session vault.
    st.session_state.owner = Owner(name=owner_name, daily_time_available=int(daily_minutes))
    Owner.save_to_json([st.session_state.owner], DATA_FILE)
    st.success(f"Owner '{owner_name}' saved with {daily_minutes} minutes available.")

if st.session_state.owner is None:
    st.info("Save an owner above to continue.")
    st.stop()

owner: Owner = st.session_state.owner

# -------------------------
# Step 2: Add a Pet
# -------------------------
st.divider()
st.subheader("Add a Pet")

col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])

if st.button("Add Pet"):
    # Check the owner's existing pets to avoid duplicates.
    existing_names = [p.name for p in owner.pets]
    if pet_name in existing_names:
        st.warning(f"'{pet_name}' is already on the list.")
    else:
        # Pet.add_task / Owner.add_pet are the class methods that handle this.
        new_pet = Pet(name=pet_name, species=species)
        owner.add_pet(new_pet)          # <-- Owner.add_pet() stores the Pet object
        Owner.save_to_json([owner], DATA_FILE)
        st.success(f"Added {species} '{pet_name}'.")

# Show current pets so the UI reflects the change immediately.
if owner.pets:
    st.write("**Your pets:**", ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets added yet.")
    st.stop()

# -------------------------
# Step 3: Add a Task
# -------------------------
st.divider()
st.subheader("Add a Task")

pet_options = [p.name for p in owner.pets]

col1, col2, col3 = st.columns(3)
with col1:
    task_pet = st.selectbox("For which pet?", pet_options)
with col2:
    task_title = st.text_input("Task description", value="Morning walk")
with col3:
    task_priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    task_hour = st.number_input("Start hour (0–23)", min_value=0, max_value=23, value=7)
with col5:
    task_minute = st.number_input("Start minute", min_value=0, max_value=59, value=0, step=15)
with col6:
    task_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)

task_frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])

if st.button("Add Task"):
    # Find the selected Pet object, then call Pet.add_task() to store the Task.
    target_pet = next(p for p in owner.pets if p.name == task_pet)

    new_task = Task(
        description=task_title,
        duration_minutes=int(task_duration),
        priority=task_priority,
        time=int(task_hour) * 60 + int(task_minute),   # convert to minutes since midnight
        pet_name=task_pet,
        frequency=task_frequency,
    )
    target_pet.add_task(new_task)       # <-- Pet.add_task() appends to the pet's task list
    Owner.save_to_json([owner], DATA_FILE)
    st.success(f"Task '{task_title}' added to {task_pet}.")

# Show all current tasks grouped by pet.
tasks_by_pet = owner.get_all_tasks_by_pet()   # <-- Owner.get_all_tasks_by_pet() returns the dict
for pet_name_key, task_list in tasks_by_pet.items():
    if task_list:
        with st.expander(f"{pet_name_key}'s tasks ({len(task_list)})", expanded=True):
            for t in task_list:
                hour, minute = divmod(t.time, 60)
                status = "✅" if t.completed else "⬜"
                st.write(f"{status} **{t.description}** — {hour}:{minute:02d}, "
                         f"{t.duration_minutes} min, {t.priority_label} priority")

# -------------------------
# Step 4: Generate Schedule
# -------------------------
st.divider()
st.subheader("Generate Today's Schedule")

if st.button("Generate Schedule"):
    all_tasks = owner.get_all_tasks()

    if not all_tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler: Scheduler = st.session_state.scheduler

        # detect_conflicts() returns warnings for overlapping tasks.
        conflicts = scheduler.detect_conflicts(all_tasks)
        if conflicts:
            for warning in conflicts:
                st.warning(f"⚠️ {warning}")

        # generate_plan() selects tasks that fit within daily_time_available,
        # sorted by priority, and returns an explanation for each decision.
        plan, explanation = scheduler.generate_plan(owner)

        st.markdown("### 📋 Today's Plan")
        if not plan:
            st.info("No tasks could be scheduled. Try increasing available time or reducing task durations.")
        else:
            for task in sorted(plan, key=lambda t: t.time):
                hour_s, min_s = divmod(task.time, 60)
                hour_e, min_e = divmod(task.time + task.duration_minutes, 60)
                st.markdown(
                    f"**{hour_s}:{min_s:02d} – {hour_e}:{min_e:02d}** &nbsp;|&nbsp; "
                    f"{task.pet_name} &nbsp;|&nbsp; {task.description} &nbsp;|&nbsp; "
                    f"_{task.priority_label} priority, {task.duration_minutes} min_"
                )

        with st.expander("Scheduler notes"):
            for note in explanation:
                st.write(f"- {note}")
