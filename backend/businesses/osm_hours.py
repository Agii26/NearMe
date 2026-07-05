"""
Best-effort parser for a useful subset of OSM's `opening_hours` tag syntax.

Full spec: https://wiki.openstreetmap.org/wiki/Key:opening_hours
That spec supports holidays, month ranges, sunset/sunrise, comments, and more.
This parser deliberately supports only the common day-range + time-range case,
which covers the large majority of real-world tags. Anything it can't parse
returns None so the caller can fall back to storing the raw string and
treating hours as unknown, rather than guessing.
"""

import re

OSM_DAY_MAP = {
    "Mo": "mon",
    "Tu": "tue",
    "We": "wed",
    "Th": "thu",
    "Fr": "fri",
    "Sa": "sat",
    "Su": "sun",
}
DAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

_TIME_RE = re.compile(r"^([0-2]\d:[0-5]\d)-([0-2]\d:[0-5]\d)$")
_DAY_TOKEN_RE = re.compile(r"^(Mo|Tu|We|Th|Fr|Sa|Su)(-(Mo|Tu|We|Th|Fr|Sa|Su))?$")


def _expand_days(day_field):
    """'Mo-Fr' -> [mon,tue,wed,thu,fri]; 'Mo,We,Fr' -> [mon,wed,fri]; 'Su' -> [sun]."""
    days = []
    for token in day_field.split(","):
        token = token.strip()
        match = _DAY_TOKEN_RE.match(token)
        if not match:
            return None
        start_abbr = match.group(1)
        end_abbr = match.group(3)
        start_idx = DAY_ORDER.index(OSM_DAY_MAP[start_abbr])
        if end_abbr:
            end_idx = DAY_ORDER.index(OSM_DAY_MAP[end_abbr])
            if end_idx < start_idx:
                return None  # wrap-around ranges (Fr-Mo) not supported
            days.extend(DAY_ORDER[start_idx : end_idx + 1])
        else:
            days.append(DAY_ORDER[start_idx])
    return days


def _parse_time_spans(time_field):
    """'09:00-18:00,19:00-22:00' -> [['09:00','18:00'], ['19:00','22:00']]. 'off'/'closed' -> []."""
    time_field = time_field.strip()
    if time_field.lower() in ("off", "closed"):
        return []
    if time_field == "24/7":
        return [["00:00", "24:00"]]
    spans = []
    for part in time_field.split(","):
        match = _TIME_RE.match(part.strip())
        if not match:
            return None
        spans.append([match.group(1), match.group(2)])
    return spans


def parse_opening_hours(raw):
    """
    Returns a dict like {"mon": [["09:00","18:00"]], "tue": [], ...} covering
    all seven days (missing days from the input default to unknown/unset —
    only days explicitly mentioned end up with a value), or None if any rule
    in the string couldn't be parsed.
    """
    if not raw or not raw.strip():
        return None

    if raw.strip() == "24/7":
        return {day: [["00:00", "24:00"]] for day in DAY_ORDER}

    result = {}
    for rule in raw.split(";"):
        rule = rule.strip()
        if not rule:
            continue
        parts = rule.split(None, 1)
        if len(parts) != 2:
            return None
        day_field, time_field = parts
        days = _expand_days(day_field)
        if days is None:
            return None
        spans = _parse_time_spans(time_field)
        if spans is None:
            return None
        for day in days:
            result[day] = spans

    return result or None
