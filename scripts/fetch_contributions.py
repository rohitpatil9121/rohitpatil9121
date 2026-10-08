"""Scrape the public contribution calendar (no token) into data/contributions.json.

    python scripts/fetch_contributions.py

Username comes from GH_USERNAME, else the repo owner in Actions, else DEFAULT_USER.
"""
import json
import os
import re
from collections import OrderedDict
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"
DEFAULT_USER = "rohitpatil9121"

COUNT_RE = re.compile(r"^\s*(\d[\d,]*|No)\s+contribution", re.I)


def fetch(user):
    resp = requests.get(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "profile-readme-heatmap", "X-Requested-With": "XMLHttpRequest"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.text


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}
    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        m = COUNT_RE.match(tips.get(cell.get("id"), ""))
        count = 0 if not m or m.group(1).lower() == "no" else int(m.group(1).replace(",", ""))
        days.append({
            "date": cell["data-date"],
            "count": count,
            "level": int(cell.get("data-level", 0)),
        })
    days.sort(key=lambda d: d["date"])
    return days


def stats(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)

    # A zero today doesn't break the streak until the day is over.
    tail = days[:-1] if days and not days[-1]["count"] else days
    current = 0
    for d in reversed(tail):
        if not d["count"]:
            break
        current += 1

    best = max(days, key=lambda d: d["count"])
    monthly = OrderedDict()
    for d in days:
        monthly[d["date"][:7]] = monthly.get(d["date"][:7], 0) + d["count"]
    return {
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "active_days": sum(1 for d in days if d["count"]),
        "monthly": monthly,
    }


def main():
    user = (os.environ.get("GH_USERNAME") or os.environ.get("GITHUB_REPOSITORY_OWNER")
            or DEFAULT_USER)
    days = parse(fetch(user))
    if len(days) < 300:
        raise SystemExit(f"only parsed {len(days)} days - GitHub's markup may have changed")
    data = {
        "user": user,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stats": stats(days),
        "days": days,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    s = data["stats"]
    print(f"{user}: {s['total']} contributions over {len(days)} days "
          f"(streak {s['current_streak']}, longest {s['longest_streak']}) as of {date.today()}")


if __name__ == "__main__":
    main()
