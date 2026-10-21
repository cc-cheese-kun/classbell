#!/usr/bin/env python3
"""可选：用 Bark 在课前把提醒推到 iPhone。

原理：本脚本每分钟跑一次（cron / 计划任务），查 schedule 里
「恰好在 N 分钟后开始」的课，命中就推一条。不需要常驻服务。

准备：
  1. iPhone 装 Bark App，拿到自己的 device key
  2. 复制 .env.example 为 .env，填 BARK_KEY
  3. crontab 每分钟跑：* * * * * python3 /path/to/bark_remind.py

注意：.env 里是你的推送密钥，不要提交到任何仓库。
"""

import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
AHEAD_MIN = 30  # 提前多少分钟提醒


def load_env():
    path = os.path.join(BASE, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def main():
    load_env()
    key = os.environ.get("BARK_KEY")
    if not key:
        print("缺少 BARK_KEY（见 .env.example）", file=sys.stderr)
        sys.exit(1)

    schedule = json.load(open(os.path.join(BASE, "examples", "schedule.json"), encoding="utf-8"))
    periods = json.load(open(os.path.join(BASE, "examples", "periods.json"), encoding="utf-8"))
    term_start = date.fromisoformat(os.environ["TERM_START"])  # 例：2026-08-31

    now = datetime.now()
    target = now + timedelta(minutes=AHEAD_MIN)
    week = (target.date() - term_start).days // 7 + 1
    if week < 1:
        return
    for e in schedule:
        if e["weekday"] != target.isoweekday() or week not in e["weeks"]:
            continue
        start = datetime.combine(target.date(), datetime.strptime(periods[str(e["start_period"])][0], "%H:%M").time())
        if abs((start - target).total_seconds()) < 60:
            body = f"{e['course']}\n{e.get('location', '')} · {periods[str(e['start_period'])][0]} 开始"
            data = json.dumps({"title": "classbell", "body": body, "group": "classbell", "level": "timeSensitive"}).encode()
            req = urllib.request.Request(
                "https://api.day.app/push",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=10)
            print(f"已推送：{body}")


if __name__ == "__main__":
    main()
