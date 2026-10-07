"""Save a USD rate sent by the iPhone shortcut to rate.json (run by the Set USD rate workflow)."""
import json
import os
import re
import sys
from datetime import datetime, timezone

raw = os.environ.get("RATE", "").replace(",", "").strip()
as_at = re.sub(r"\s+", " ", os.environ.get("AS_AT", "")).strip()[:40] or None

try:
    rate = float(raw)
except ValueError:
    sys.exit(f"Not a number: {raw!r}")
if not 100 < rate < 1000:
    sys.exit(f"Rate looks wrong: {rate}")
if as_at and not re.fullmatch(r"\d{1,2} [A-Za-z]+ \d{4} \d{1,2}:\d{2} ?[AP]M", as_at):
    sys.exit(f"Unexpected 'as at' time: {as_at!r}")

data = {
    "rate": rate,
    "type": "Telegraphic Transfer selling rate",
    "bankAsAt": as_at,
    "source": "https://www.nationstrust.com/exchange-rates",
}

try:
    old = json.load(open("rate.json"))
except Exception:
    old = {}

if {k: old.get(k) for k in data} == data:
    print("Rate unchanged:", rate)
    sys.exit(0)

data["fetchedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
with open("rate.json", "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
print("Rate updated:", rate, as_at)
