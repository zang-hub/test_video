import os
import json
import pytz
import glob
from datetime import datetime, timedelta
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

def get_last_7_logs():
    logs = []
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    today = datetime.now(vn_tz)

    for i in range(7):
        day = today - timedelta(days=i)
        filename = f"log_{day.strftime('%Y%m%d')}.json"
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                    logs.extend(entries)
            except:
                continue
    return logs

def generate_weekly_report(entries):
    vn_now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
    week_range = f"{(vn_now - timedelta(days=6)).strftime('%d/%m')} - {vn_now.strftime('%d/%m/%Y')}"

    header = f"📅 <b>Top 5 Tin Nổi Bật Trong Tuần ({week_range})</b>\n\n"

    # Ưu tiên tin breaking
    sorted_entries = sorted(entries, key=lambda x: x["is_breaking"], reverse=True)
    top5 = sorted_entries[:5]

    body = ""
    for i, item in enumerate(top5, 1):
        prefix = "🔥" if item["is_breaking"] else f"{i}️⃣"
        body += (
            f"{prefix} <b>{item['title_en']}</b>\n"
            f"{item['summary_en']}\n"
            f"📌 <b>{item['title_vi']}</b>\n"
            f"{item['summary_vi']}\n"
            f"🔗 <a href='{item['link']}'>Read more</a>\n\n"
        )

    footer = "📺 <i>Bản tin cuối tuần dành cho kênh YouTube CK Crypto</i>"
    return header + body + footer

def main():
    entries = get_last_7_logs()
    if not entries:
        print("⚠️ No entries for weekly report.")
        return

    message = generate_weekly_report(entries)
    send_telegram(message)
    print("✅ Weekly summary sent.")

if __name__ == "__main__":
    main()
