
import json
from collections import Counter

with open("decisions_quickstart.jsonl", encoding="utf-8") as f:
    decisions = [json.loads(line) for line in f if line.strip()]

by_id = {d["event_id"]: d for d in decisions}
releases = [d for d in decisions if d["action"] == "release_room"]

print("TOTAL RELEASES:", len(releases))

problems = []

for d in releases:
    deps = [by_id[x] for x in d.get("dependencies", []) if x in by_id]
    evidence = d.get("evidence", [])

    print(f"\n{d['episode_id']}")
    print("  Room:", d["affected_assets"])
    print("  Timestamp:", d["timestamp_utc"])
    print("  Evidence:", evidence)
    print("  Dependencies:", [(x["action"], x["event_id"]) for x in deps])
    print("  Human approval:", d["requires_human_approval"])

    if not evidence:
        problems.append((d["episode_id"], "Missing evidence"))

    if d.get("requires_human_approval"):
        problems.append((d["episode_id"], "Release requires approval"))

    if any(x["action"] == "request_human_approval" for x in deps):
        problems.append((d["episode_id"], "Depends on unapproved request"))

    if any(x not in by_id for x in d.get("dependencies", [])):
        problems.append((d["episode_id"], "Missing dependency"))

print("\n=== SUMMARY ===")
print("Release count:", len(releases))
print("Dependency actions:", Counter(
    by_id[x]["action"]
    for d in releases
    for x in d.get("dependencies", [])
    if x in by_id
))

print("Potential problems:", len(problems))
for episode, problem in problems:
    print(f"  {episode}: {problem}")
