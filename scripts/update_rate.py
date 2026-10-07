"""Fetch the Nations Trust Bank USD selling rate and save it to rate.json."""
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

URL = "https://www.nationstrust.com/exchange-rates"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
req = urllib.request.Request(URL, headers=HEADERS)
page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

# "Rate: Rupees per unit of foreign currency as at <span ...>07 October 2026 02:10 PM</span>"
as_at = re.search(r"as at\s*<span[^>]*>([^<]+)</span>", page)
as_at = html.unescape(as_at.group(1)).strip() if as_at else None

# USD row columns: notes buy, notes sell, DD buy, DD sell, TT buy, TT sell, import bill
row = re.search(r'alt="USD Flag".*?</tr>', page, re.S)
if not row:
    sys.exit("USD row not found")
cells = re.findall(r"<td>\s*([\d,.]+)\s*</td>", row.group(0))
if len(cells) < 6:
    sys.exit(f"Unexpected USD row: {cells}")
nums = [float(c.replace(",", "")) for c in cells]
tt_selling = nums[5]
if not 100 < tt_selling < 1000:
    sys.exit(f"Rate looks wrong: {tt_selling}")

data = {
    "rate": tt_selling,
    "type": "Telegraphic Transfer selling rate",
    "bankAsAt": as_at,
    "source": URL,
}

try:
    old = json.load(open("rate.json"))
except Exception:
    old = {}

if {k: old.get(k) for k in data} == data:
    print("Rate unchanged:", tt_selling)
    sys.exit(0)

data["fetchedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
with open("rate.json", "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
print("Rate updated:", tt_selling, as_at)
