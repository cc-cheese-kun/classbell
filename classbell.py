#!/usr/bin/env python3
"""classbell — 把高校课表转成带课前提醒的日历文件（.ics）。

输入两个 JSON：
  schedule.json  课程列表，字段见 examples/schedule.json
  periods.json   作息表：节次 -> [开始, 结束]，见 examples/periods.json

用法：
  python3 classbell.py --schedule examples/schedule.json \
      --periods examples/periods.json \
      --term-start 2026-08-31 \
      --out classbell.ics

生成的每个课程事件自带 VALARM，默认提前 30 分钟提醒（--alarm 可改）。
把 .ics 导入手机/电脑日历即可，不依赖任何服务器。
"""

import argparse
import json
import sys
import uuid
from datetime import date, datetime, time, timedelta

VTIMEZONE = """BEGIN:VTIMEZONE
TZID:Asia/Shanghai
BEGIN:STANDARD
DTSTART:19700101T000000
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
TZNAME:CST
END:STANDARD
END:VTIMEZONE"""


def parse_hhmm(s):
    h, m = s.split(":")
    return time(int(h), int(m))


def esc(text):
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def build_events(schedule, periods, term_start):
    """yield (start_dt, end_dt, summary, location, description)"""
    for entry in schedule:
        weekday = int(entry["weekday"])  # 1=周一 ... 7=周日
        start_t = parse_hhmm(periods[str(entry["start_period"])][0])
        end_t = parse_hhmm(periods[str(entry["end_period"])][1])
        for week in entry["weeks"]:
            day = term_start + timedelta(days=(week - 1) * 7 + (weekday - 1))
            yield (
                datetime.combine(day, start_t),
                datetime.combine(day, end_t),
                entry["course"],
                entry.get("location", ""),
                f"教师：{entry.get('teacher', '')}（第{week}周）",
            )


def to_ics(events, alarm_minutes):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//classbell//classbell//CN",
        "CALSCALE:GREGORIAN",
        VTIMEZONE,
    ]
    stamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    for start, end, summary, location, desc in events:
        uid = f"{uuid.uuid5(uuid.NAMESPACE_URL, f'{summary}|{start.isoformat()}|{location}')}@classbell"
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}",
            f"DTSTART;TZID=Asia/Shanghai:{start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND;TZID=Asia/Shanghai:{end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{esc(summary)}",
            f"LOCATION:{esc(location)}",
            f"DESCRIPTION:{esc(desc)}",
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{esc(summary)}",
            f"TRIGGER:-PT{alarm_minutes}M",
            "END:VALARM",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def main():
    ap = argparse.ArgumentParser(description="课表 -> 带提醒的 .ics 日历")
    ap.add_argument("--schedule", required=True, help="课程 JSON 路径")
    ap.add_argument("--periods", required=True, help="作息 JSON 路径")
    ap.add_argument("--term-start", required=True, help="学期第 1 周周一，YYYY-MM-DD")
    ap.add_argument("--out", default="classbell.ics", help="输出 .ics 路径")
    ap.add_argument("--alarm", type=int, default=30, help="提前提醒分钟数，默认 30")
    args = ap.parse_args()

    with open(args.schedule, encoding="utf-8") as f:
        schedule = json.load(f)
    with open(args.periods, encoding="utf-8") as f:
        periods = json.load(f)
    term_start = date.fromisoformat(args.term_start)
    if term_start.weekday() != 0:
        print(f"警告：{args.term_start} 不是周一，请确认这就是第 1 周周一", file=sys.stderr)

    events = sorted(build_events(schedule, periods, term_start))
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        f.write(to_ics(events, args.alarm))
    print(f"已生成 {args.out}：{len(events)} 个课程事件，提前 {args.alarm} 分钟提醒")


if __name__ == "__main__":
    main()
