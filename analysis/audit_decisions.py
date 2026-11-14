
import json
from pathlib import Path
from collections import Counter, defaultdict

path = Path("decisions_quickstart.jsonl")
decisions = [
    json.loads(line)
    for line in path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]

print("TOTAL DECISIONS:", len(decisions))

print("\n=== ACTIONS BY SCENARIO ===")
counts = Counter(
    (d.get("issue_type"), d.get("action"))
    for d in decisions
)

for (issue, action), count in sorted(counts.items()):
    print(f"{issue:26} {action:26} {count}")

print("\n=== EPISODES WITH MOST DECISIONS ===")
episodes = defaultdict(list)

for d in decisions:
    episodes[d.get("episode_id")].append(d)

for episode, items in sorted(
    episodes.items(),
    key=lambda x: len(x[1]),
    reverse=True
)[:15]:
    print(
        f"{str(episode):48} "
        f"{len(items)} decisions: "
        f"{dict(Counter(d.get('action') for d in items))}"
    )

print("\n=== EQUIPMENT DECISIONS ===")
for d in decisions:
    if d.get("issue_type") in (
        "heating_plant",
        "ventilation_maintenance",
    ):
        print(json.dumps(d, indent=2))

print("\n=== DEPENDENCY CHECK ===")
ids = {d.get("event_id") for d in decisions}
missing = []

for d in decisions:
    for dependency in d.get("dependencies", []) or []:
        if dependency not in ids:
            missing.append((d.get("event_id"), dependency))

print("Missing dependencies:", len(missing))
for item in missing[:10]:
    print(item)
