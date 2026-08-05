#!/usr/bin/env python3
"""Parse a WhatsApp Android chat export (.txt) into messages.csv + stats.json.

Decision: issue 2 (wraplove) — Python 3 stdlib, no deps. messages.csv is the
canonical dataset; stats.json is the only thing the landing consumes.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

LINE_RE = re.compile(
    r"^(\d{1,2})/(\d{1,2})/(\d{2,4}), (\d{1,2}):(\d{2})(?::(\d{2}))? - (.*)$"
)
# Media placeholders that mark a message as media, not text (localized).
MEDIA_OMITTED = re.compile(
    r"<[^>]*\b(?:omitted|omitido|adjunto|attached)\b[^>]*>", re.I
)
SYS_KEYWORDS = ("end-to-end", "encrypted", "creó", "creaste", "unió", "salió", "deleted")

EMOJI_RANGES = [
    (0x1F000, 0x1FAFF),  # symbols, pictographs, supplemental
    (0x2600, 0x27BF),    # misc symbols, dingbats
    (0x2B00, 0x2BFF),    # misc symbols and arrows
    (0x1F1E6, 0x1F1FF),  # regional indicators
]
SKIP = {0xFE0F, 0x200D} | set(range(0x1F3FB, 0x1F400))  # VS16, ZWJ, skin tones

def is_emoji(ch: str) -> bool:
    c = ord(ch)
    if c in SKIP:
        return False
    return any(lo <= c <= hi for lo, hi in EMOJI_RANGES)

def parse_chat(path: Path):
    raw = path.read_text(encoding="utf-8-sig")
    raw = "".join(ch for ch in raw if ch.isprintable() or ch == "\n")
    msgs, cur = [], None
    for line in raw.splitlines():
        m = LINE_RE.match(line)
        if m:
            d, mo, y, h, mi, s = m.group(1, 2, 3, 4, 5, 6)
            y = int(y)
            y = y + 2000 if y < 100 else y
            try:
                ts = datetime(int(y), int(mo), int(d), int(h), int(mi), int(s or 0))
            except ValueError:
                continue
            rest = m.group(7)
            sender, text = (rest.split(": ", 1) + [None])[:2] if ": " in rest else (None, rest)
            cur = {"ts": ts, "sender": sender, "text": text or ""}
            msgs.append(cur)
        elif cur is not None:
            cur["text"] += "\n" + line
    return msgs

def classify(m):
    if m["sender"] is None:
        return "system"
    if MEDIA_OMITTED.search(m["text"]) or re.search(r"\.(jpg|jpeg|png|gif|mp4|opus|pdf)\s*\(|\(file attached\)", m["text"], re.I):
        return "media"
    return "text"

def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else next(Path(".").glob("WhatsApp Chat*.txt"))
    msgs = parse_chat(src)
    for m in msgs:
        m["type"] = classify(m)

    with open("messages.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["epoch", "date", "sender", "type", "text"])
        for m in msgs:
            w.writerow([int(m["ts"].timestamp()), m["ts"].isoformat(sep=" ", timespec="minutes"), m["sender"] or "", m["type"], m["text"].replace("\n", "\\n")])

    texts = [m for m in msgs if m["type"] == "text" and m["sender"]]
    senders = sorted({m["sender"] for m in texts})
    by = {s: [m for m in texts if m["sender"] == s] for s in senders}
    words = {s: sum(len(m["text"].split()) for m in by[s]) for s in senders}
    first, last = msgs[0], msgs[-1]

    emoji_counts = Counter()
    for m in texts:
        for ch in m["text"]:
            if is_emoji(ch):
                emoji_counts[ch] += 1

    days = sorted({m["ts"].date() for m in msgs})
    streaks, cur = [], 1
    for a, b in zip(days, days[1:]):
        cur = cur + 1 if b - a == timedelta(days=1) else 1
        streaks.append(cur)
    longest_streak = max(streaks, default=1)

    per_day = Counter(m["ts"].date() for m in msgs)
    top_day = max(per_day.items(), key=lambda kv: kv[1])

    def count_sayings(patterns):
        return {s: sum(1 for m in by[s] if any(p in m["text"].lower() for p in patterns)) for s in senders}

    te_quiero = count_sayings(["te quiero"])
    te_amo = count_sayings(["te amo"])

    hour_counts = Counter(m["ts"].hour for m in texts)
    weekday_counts = Counter(m["ts"].weekday() for m in texts)

    first_msgs = {}
    for s in senders:
        first_msgs[s] = next((m["text"] for m in msgs if m["sender"] == s and m["type"] == "text"), "")

    stats = {
        "span": {"first": first["ts"].isoformat(), "last": last["ts"].isoformat()},
        "total_messages": len(msgs),
        "per_sender": {s: {"messages": len(by[s]), "words": words[s], "first_message": first_msgs[s]} for s in senders},
        "media_per_sender": {s: sum(1 for m in msgs if m["sender"] == s and m["type"] == "media") for s in senders},
        "top_emojis": [{"emoji": e, "count": c} for e, c in emoji_counts.most_common(15)],
        "hours": [{"hour": h, "count": c} for h, c in sorted(hour_counts.items())],
        "weekdays": [{"weekday": w, "count": c} for w, c in sorted(weekday_counts.items())],
        "longest_streak_days": longest_streak,
        "top_day": {"date": str(top_day[0]), "messages": top_day[1]},
        "te_quiero": te_quiero,
        "te_amo": te_amo,
        "days_with_messages": len(days),
        "msgs_per_day": round(len(msgs) / max(len(days), 1), 1),
    }
    Path("stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"parsed {len(msgs)} messages ({len(days)} days) -> messages.csv + stats.json")

if __name__ == "__main__":
    main()
