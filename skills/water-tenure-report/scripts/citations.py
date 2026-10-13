"""Reference strings (OSCOLA or APA 7) built from sources.csv fields, and evidence grades.

The catalogue's `author_org` convention: "Author; Outlet" for news, "Account; Platform" for
social media, "Author; Journal" for articles, an organisation name otherwise. Sources a reader
cannot open (verifiability restricted, team, drive-only, lost) are cited as "on file with the
research team", so internal paths never reach a report.
"""
from __future__ import annotations

import datetime as dt
import re

ON_FILE = {"restricted", "team", "drive-only", "lost"}
FIELD = {"interview", "group-interview", "fgd", "workshop", "observation", "community-mapping"}


def grade(stype: str, author: str = "", press_markers: list[str] | None = None) -> str:
    """Evidence grade of a source by its type: what kind of source it is, not whether it is true."""
    a = (author or "").lower()
    if stype in ("admin-record", "permit-register", "archive"):
        return "E1"
    if stype == "statistics":
        return "E2" if "poll" in a else "E1"
    if stype in FIELD:
        return "E2"
    if stype in ("academic", "grey-report", "ngo-report", "map-drone", "project-deliverable"):
        return "E3"
    if stype == "news":
        return "E4"
    if stype == "photo-video":
        markers = press_markers or ["tv", "news", "press", "foto", "antara", "reuters", "afp", "ap "]
        return "E4" if any(m in a for m in markers) else "E5"
    if stype == "social-media":
        return "E5"
    if stype in ("derived-summary", "ai-generated"):
        return "D"
    return "E3"


def long_date(d: str) -> str:
    try:
        x = dt.date.fromisoformat((d or "")[:10])
        return f"{x.day} {x.strftime('%B')} {x.year}"
    except ValueError:
        return d or "n.d."


def year(d: str) -> str:
    m = re.match(r"(\d{4})", d or "")
    return m.group(1) if m else "n.d."


def _parts(author: str) -> list[str]:
    return [p.strip() for p in (author or "").split(";") if p.strip()]


def _where(s: dict, accessed: str) -> str:
    url = (s.get("path_or_url") or "").strip()
    if (s.get("verifiability") or "").strip() in ON_FILE or not url.lower().startswith("http"):
        return "(on file with the research team)"
    return f"<{url}> accessed {accessed}"


def oscola(s: dict, accessed: str) -> tuple[str, str]:
    """(full reference, short form) in OSCOLA style."""
    st, title, date = s.get("source_type", ""), (s.get("title") or "").strip(), s.get("date", "")
    p = _parts(s.get("author_org", ""))
    where = _where(s, accessed)
    if st in ("interview", "group-interview", "fgd", "workshop"):
        who = (s.get("respondent_code") or s.get("source_id") or "").strip()
        kind = {"interview": "Interview", "group-interview": "Group interview", "fgd": "Focus group discussion",
                "workshop": "Workshop"}[st]
        full = f"{kind} {who} ({long_date(date)}) {where}"
        return full, f"{kind} {who.split(',')[0]}"
    if st in ("news", "social-media", "photo-video") and len(p) >= 2:
        full = f"{'; '.join(p[:-1])}, ‘{title}’ ({p[-1]}, {long_date(date)}) {where}"
        return full, f"{p[0]}, ‘{_short(title)}’"
    if st == "academic" and len(p) >= 2:
        full = f"{p[0]}, ‘{title}’ ({year(date)}) {p[1]} {where}"
        return full, f"{p[0]}, ‘{_short(title)}’"
    org = p[0] if p else ""
    full = f"{org + ', ' if org else ''}*{title}* ({long_date(date)}) {where}"
    return full, f"{org + ', ' if org else ''}*{_short(title)}*"


def apa(s: dict, accessed: str) -> tuple[str, str]:
    """(reference-list entry, author-date short form) in APA 7 style."""
    st, title, date = s.get("source_type", ""), (s.get("title") or "").strip(), s.get("date", "")
    p = _parts(s.get("author_org", ""))
    url = (s.get("path_or_url") or "").strip()
    on_file = (s.get("verifiability") or "").strip() in ON_FILE or not url.lower().startswith("http")
    tail = "Unpublished; on file with the research team." if on_file else url
    if st in ("interview", "group-interview", "fgd", "workshop"):
        who = (s.get("respondent_code") or s.get("source_id") or "").strip()
        return f"{who} ({year(date)}). *{title}* [{st}]. {tail}", f"{who.split(',')[0]}, {year(date)}"
    author = p[0] if p else title
    outlet = f" {p[-1]}." if len(p) >= 2 else ""
    return (f"{author}. ({year(date)}). *{title}*.{outlet} {tail}".replace("..", "."),
            f"{author}, {year(date)}")


def _short(title: str, n: int = 6) -> str:
    w = title.split()
    return " ".join(w[:n]) + ("..." if len(w) > n else "")


def anonymise(ref: str) -> str:
    """Drop the account name before the title quote of a social-media reference."""
    i = ref.find("‘")
    return "Post by a private account, " + ref[i:] if i > 0 else ref
