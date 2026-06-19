import random
import json
from datetime import datetime, timedelta


# ── 1. DATETIME PARSING ───────────────────────────────────────────────────────

DATE_FORMAT = "%Y-%m-%d"   # The agreed format across the whole team

def parse_date(date_str: str) -> datetime:
    """
    Convert a date string (e.g. '2026-06-20') into a datetime object.

    Why datetime and not just a string?
      - Strings sort lexicographically, which only works if the format is
        strictly ISO-8601 (YYYY-MM-DD). Using datetime makes the intent
        explicit and lets other team members use timedelta arithmetic
        (Person 3's filter) without any extra conversion step.

    Args:
        date_str: A date string in YYYY-MM-DD format.

    Returns:
        A datetime object representing midnight on that date.

    Raises:
        ValueError: If the string doesn't match the expected format.
    """
    return datetime.strptime(date_str, DATE_FORMAT)


def format_date(dt: datetime) -> str:
    """Round-trip helper: datetime → string (used when saving to JSON)."""
    return dt.strftime(DATE_FORMAT)


# ── 2. MOCK DATA GENERATION ───────────────────────────────────────────────────

# Configuration knobs — change these to tweak the generated dataset
NUM_TASKS      = 100_000
PRIORITY_RANGE = (1, 5)        # 1 = highest priority, 5 = lowest
DATE_RANGE_DAYS = 30           # deadlines spread across the next 30 days
RANDOM_SEED    = 42            # fixed seed → reproducible dataset

# A small pool of realistic-sounding task name prefixes and suffixes so names
# look meaningful instead of just "Task_00001".
_PREFIXES = [
    "Review", "Deploy", "Fix", "Test", "Update",
    "Refactor", "Document", "Analyse", "Ship", "Monitor",
]
_SUFFIXES = [
    "API", "Database", "UI", "Pipeline", "Report",
    "Dashboard", "Auth", "Cache", "Queue", "Schema",
]


def _make_task_name(index: int) -> str:
    """
    Build a unique, human-readable task name.

    Format: '<Prefix>_<Suffix>_<zero-padded index>'
    Example: 'Deploy_Cache_00042'

    The index suffix guarantees uniqueness across all 100 k tasks, which is
    critical for Person 4's O(1) dictionary lookup (keys must be unique).
    """
    prefix = _PREFIXES[index % len(_PREFIXES)]
    suffix = _SUFFIXES[(index // len(_PREFIXES)) % len(_SUFFIXES)]
    return f"{prefix}_{suffix}_{index:06d}"


def generate_tasks(
    num_tasks: int = NUM_TASKS,
    seed: int = RANDOM_SEED,
) -> list[dict]:
    """
    Generate a list of *num_tasks* task dictionaries with **parsed** datetime
    objects (not raw strings).

    Each task dict has:
        name     (str)      – unique human-readable identifier
        priority (int)      – 1 (highest) … 5 (lowest)
        deadline (datetime) – parsed datetime object

    Args:
        num_tasks: How many tasks to generate.
        seed:      Random seed for reproducibility.

    Returns:
        List of task dicts, in insertion order (unsorted — sorting is
        Person 2's job).
    """
    random.seed(seed)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    tasks = []
    for i in range(num_tasks):
        days_offset = random.randint(0, DATE_RANGE_DAYS)
        deadline_dt = today + timedelta(days=days_offset)

        task = {
            "name":     _make_task_name(i),
            "priority": random.randint(*PRIORITY_RANGE),
            "deadline": deadline_dt,          # ← already a datetime object
        }
        tasks.append(task)

    return tasks


# ── 3. SERIALISATION HELPERS (for handing data to teammates) ─────────────────

def save_tasks_to_json(tasks: list[dict], filepath: str) -> None:
    
    serialisable = [
        {**t, "deadline": format_date(t["deadline"])}
        for t in tasks
    ]
    with open(filepath, "w") as f:
        json.dump(serialisable, f, indent=2)
    print(f"[Person 1] Saved {len(tasks):,} tasks → {filepath}")


def load_tasks_from_json(filepath: str) -> list[dict]:
    """
    Load tasks from a JSON file and parse deadline strings back to datetime.

    This is the function your teammates call — they get datetime objects, not
    strings, so they can do arithmetic (Person 3) or comparisons (Person 2)
    immediately.
    """
    with open(filepath) as f:
        raw = json.load(f)

    tasks = [
        {**t, "deadline": parse_date(t["deadline"])}
        for t in raw
    ]
    print(f"[Person 1] Loaded & parsed {len(tasks):,} tasks ← {filepath}")
    return tasks



if __name__ == "__main__":
    print("=" * 60)
    print("  PERSON 1 — Data Generation & Datetime Parsing")
    print("=" * 60)

    # --- ) Generate the full 100 k dataset ---
    print(f"\n[B] Generating {NUM_TASKS:,} tasks …")
    import time
    t0 = time.perf_counter()
    tasks = generate_tasks()
    elapsed = time.perf_counter() - t0
    print(f"    Done in {elapsed:.3f}s")

    # --- ) Inspect a few rows ---
    print("\n[C] First 5 tasks (already have datetime deadlines):")
    for task in tasks[:5]:
        print(f"  {task}")

    # --- ) Quick sanity checks ---
    print("\n[D] Sanity checks:")
    priorities = [t["priority"] for t in tasks]
    print(f"  Priority range : {min(priorities)} – {max(priorities)}")

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    deadlines = [t["deadline"] for t in tasks]
    print(f"  Earliest deadline : {min(deadlines).date()}")
    print(f"  Latest deadline   : {max(deadlines).date()}")
    print(f"  All deadlines are datetime? "
          f"{all(isinstance(t['deadline'], datetime) for t in tasks)}")

    # --- ) Save & reload (round-trip test) ---
    print("\n[E] Round-trip save → load:")
    out_path = "tasks.json"
    save_tasks_to_json(tasks, out_path)
    reloaded = load_tasks_from_json(out_path)
    assert reloaded[0]["deadline"] == tasks[0]["deadline"], "Round-trip mismatch!"
    print("  Round-trip OK ✓")

    
