"""Time-aware staff/robot reservations with absence and overlap checks."""
import pandas as pd

ABSENT = {'sick', 'vacation', 'out_of_service', 'absent'}

class Scheduler:
    def __init__(self, roster):
        self.roster = roster.copy()
        self.reservations = []

    def available(self, role, start, end, known_at):
        r = self.roster
        needed = {'role', 'start_utc', 'end_utc', 'resource_id'}
        if r.empty or not needed.issubset(r.columns):
            return []
        start, end, known_at = map(pd.Timestamp, (start, end, known_at))
        if end <= start:
            return []
        # Scheduled shifts must cover the entire requested interval.
        shifts = r[(r.role == role) & (r.start_utc <= start) & (r.end_utc >= end)]
        if 'status' in r.columns:
            shifts = shifts[shifts.status.isin({'scheduled', 'available'})]
        ids = set(shifts.resource_id.dropna().astype(str))
        # Absence records may be separate rows from scheduled shifts.
        if {'status', 'status_known_utc'}.issubset(r.columns):
            unavailable = r[
                r.status.isin(ABSENT)
                & (r.status_known_utc <= known_at)
                & (r.start_utc < end)
                & (r.end_utc > start)
            ]
            ids -= set(unavailable.resource_id.dropna().astype(str))
        return [rid for rid in sorted(ids)
                if not any(a == rid and start < b and end > c
                           for a, c, b in self.reservations)]

    def reserve(self, role, start, end, known_at):
        ids = self.available(role, start, end, known_at)
        if not ids:
            return None
        self.reservations.append((ids[0], pd.Timestamp(start), pd.Timestamp(end)))
        return ids[0]
