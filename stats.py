"""
Sports Meet 2026 - Visitor Statistics & Persistence.
Tracks total guests welcomed today, session arrivals, recent influx, and hourly trends.
"""
import datetime
import json
import os
import time


class VisitorStats:
    def __init__(self, path, reset_daily=True):
        self.path = path
        self.total = 0
        self.arrivals = []       # unix timestamps of arrivals (trimmed to last 24h)
        self.session_new = 0     # arrivals in current app session
        self.today = datetime.date.today().isoformat()
        self._load(reset_daily)

    def _load(self, reset_daily):
        try:
            if not os.path.exists(self.path):
                return
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            saved_date = data.get("date")
            if reset_daily and saved_date != self.today:
                print(f"[stats] New date ({self.today} vs saved {saved_date}). Starting fresh count for today.")
                return
            self.total = max(0, int(data.get("total", 0)))
            raw_arrivals = data.get("arrivals", [])
            valid_arrivals = []
            for t in raw_arrivals:
                try:
                    valid_arrivals.append(float(t))
                except (ValueError, TypeError):
                    pass
            self.arrivals = valid_arrivals
            print(f"[stats] Successfully resumed visitor count: {self.total}")
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
            print(f"[stats] Starting with initial count 0 (Note: {exc})")

    def save(self):
        """Atomically persist count and arrival timestamps to disk."""
        try:
            dirname = os.path.dirname(self.path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            tmp = self.path + ".tmp"
            payload = {
                "date": self.today,
                "total": self.total,
                "arrivals": self.arrivals,
                "last_updated": datetime.datetime.now().isoformat(),
            }
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
            os.replace(tmp, self.path)
        except Exception as e:
            print(f"[stats] Error saving visitor statistics: {e}")

    def add(self, n=1):
        """Record n new visitors."""
        now = time.time()
        self.total += n
        self.session_new += n
        self.arrivals.extend([now] * n)
        self._trim(now)
        self.save()

    def adjust(self, delta):
        """Manually adjust total count (+1 or -1)."""
        self.total = max(0, self.total + delta)
        self.save()

    def reset(self):
        """Reset today's count."""
        self.total = 0
        self.session_new = 0
        self.arrivals = []
        self.save()

    def _trim(self, now):
        """Trim arrivals older than 24 hours to keep data lean."""
        cutoff = now - 86400
        self.arrivals = [t for t in self.arrivals if t >= cutoff]

    def recent_arrivals(self, seconds=600):
        """Number of arrivals in the last N seconds (default: 10 minutes)."""
        cutoff = time.time() - seconds
        return sum(1 for t in self.arrivals if t >= cutoff)

    def arrivals_last_hour(self):
        """Total arrivals in the last 60 minutes."""
        return self.recent_arrivals(3600)

    def buckets(self, count=12, seconds=300):
        """
        Arrivals per bucket, oldest first.
        Default: 12 buckets x 5 minutes = 60 minutes window.
        """
        now = time.time()
        out = [0] * count
        cutoff = now - (count * seconds)
        for t in self.arrivals:
            if t < cutoff:
                continue
            age = now - t
            idx = int(age // seconds)
            if 0 <= idx < count:
                out[count - 1 - idx] += 1
        return out
