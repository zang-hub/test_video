import os
import json
import pytz
from datetime import datetime
import requests

# --- ENV ---
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

def load_daily_log():
    today = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y%m%d")
    log_file = f"log_{today}.json"
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def generate_report(entries):
    vn_today = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d/%m/%Y")
    title = f"🧾 <b>Top 5 Tin Nổi Bật Ngày {vn_today}</b>\n\n"

    # Ưu tiên tin breaking lên đầu
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

    footer = "📺 <i>Bản tin tổng hợp dành cho kênh YouTube CK Crypto</i>"
    return title + body + footer

def main():
    entries = load_daily_log()
    if not entries:
        print("⚠️ No log entries found today.")
        return

    message = generate_report(entries)
    send_telegram(message)
    print("✅ Daily summary sent.")

if __name__ == "__main__":
    main()
