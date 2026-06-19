from datetime import datetime, timedelta
import random
import time

# ==========================================
# STEP 1: GENERATE MOCK DATA
# ==========================================

tasks = []

for i in range(100000):

    priority = random.randint(1, 5)

    future_days = random.randint(0, 365)

    deadline = (
        datetime.now() +
        timedelta(days=future_days)
    ).strftime("%Y-%m-%d")

    tasks.append({
        "name": f"Task_{i}",
        "priority": priority,
        "deadline": deadline
    })

print("Generated:", len(tasks), "tasks")

# ==========================================
# STEP 2: PARSE DATES
# ==========================================

for task in tasks:

    task["deadline"] = datetime.strptime(
        task["deadline"],
        "%Y-%m-%d"
    )

print("Dates parsed successfully")

# ==========================================
# STEP 3: SORT TASKS
# ==========================================

sort_start = time.time()

tasks.sort(
    key=lambda task:
    (
        task["priority"],
        task["deadline"]
    )
)

sort_end = time.time()

print(
    "Sorting Time:",
    round(sort_end - sort_start, 4),
    "seconds"
)

# ==========================================
# STEP 4: FILTER NEXT 3 DAYS
# ==========================================

today = datetime.now()

three_days = today + timedelta(days=3)

upcoming_tasks = []

for task in tasks:

    if today <= task["deadline"] <= three_days:
        upcoming_tasks.append(task)

print(
    "Tasks due within 3 days:",
    len(upcoming_tasks)
)

# ==========================================
# STEP 5: HASH MAP INDEX
# ==========================================

task_index = {}

for task in tasks:
    task_index[task["name"]] = task

print("Dictionary index created")

# ==========================================
# STEP 6: O(1) SEARCH
# ==========================================

search_name = "Task_99999"

lookup_start = time.time()

result = task_index.get(search_name)

lookup_end = time.time()

print("\nTask Found:")
print(result)

print(
    "\nDictionary Lookup Time:",
    lookup_end - lookup_start,
    "seconds"
)