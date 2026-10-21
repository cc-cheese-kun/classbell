# classbell

把高校课表转成带课前提醒的日历：一份 `.ics` 文件，导入任何日历 App，上课前自动响。

Turn a university class schedule into a calendar with per-class alarms. No server, no account, your data never leaves your machine.

## 它解决什么

- 教务系统给的课表是一张网页表格，手机日历里什么都没有，全靠脑子记
- 每学期手动往日历里敲课，一门课重复十几周，敲到怀疑人生
- 通用的「课表 App」要注册、要授权、还塞广告

classbell 只做一件事：**课表 JSON → 带提醒的 .ics**。导入 iOS / Android / Outlook / Google 日历都行，每个课程事件自带提前提醒。

## 15 分钟跑通（用示例数据）

```bash
git clone https://github.com/cc-cheese-kun/classbell.git
cd classbell
python3 classbell.py \
  --schedule examples/schedule.json \
  --periods  examples/periods.json \
  --term-start 2026-08-31 \
  --out classbell.ics
```

把生成的 `classbell.ics` 发到手机上点开导入，就能看到示例课程已经排进日历、每节带 30 分钟提前提醒。不需要安装任何依赖，Python 3 标准库就能跑。

## 换成你自己的课表

只需要准备两个文件，格式照着 `examples/` 改：

**schedule.json** — 一门课一条（同一门课不同周/地点就拆成多条）：

| 字段 | 说明 |
|---|---|
| `course` | 课程名 |
| `teacher` | 教师（可空） |
| `weekday` | 1=周一 … 7=周日 |
| `weeks` | 上课的周次列表，如 `[1,2,3,4]`，双周课就是 `[2,4,6,8]` |
| `start_period` / `end_period` | 起止节次 |
| `location` | 地点（可空） |

**periods.json** — 你学校的作息表：节次 → `[开始, 结束]`，如 `"1": ["08:00", "08:45"]`。

**--term-start** — 本学期第 1 周的周一日期。这一个日期对了，整学期的周次就都对了。

提醒提前量用 `--alarm 分钟数` 改，默认 30。

## 可选：Bark 推送提醒（iPhone）

不想用日历闹钟，也可以用 [Bark](https://github.com/Finb/Bark) 把提醒推到手机：见 `bark_remind.py` 顶部说明。复制 `.env.example` 为 `.env` 填自己的 key，每分钟跑一次脚本即可。**key 只放在本地 `.env`，已在 .gitignore 里，别提交。**

## 路线图

- [x] v0.1 核心转换（JSON → ICS + VALARM）、Bark 推送脚本、示例数据
- [ ] v0.2 常见教务系统导出格式导入（正方 / 强智的 Excel 课表）
- [ ] v0.2 连堂自动合并、调休/停课排除日期
- [ ] v0.3 一键生成本学期全部提醒的托管脚本模板

欢迎提 issue 说你学校的课表长什么样——导入格式就是按真实样本加的。

## 隐私

课表只在你本地转换，不上传任何服务器。仓库里的示例数据全是编的，不含任何真实课程与个人信息。

## License

MIT
