import os
import json
import pytz
from datetime import datetime
import requests
import re

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

def strip_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)

def generate_report(entries, raw=False):
    vn_today = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d/%m/%Y")
    title = f"🧾 <b>Top 5 Tin Nổi Bật Ngày {vn_today}</b>\n\n" if not raw else f"Top 5 Tin Nổi Bật Ngày {vn_today}\n\n"

    sorted_entries = sorted(entries, key=lambda x: x["is_breaking"], reverse=True)
    top5 = sorted_entries[:5]

    body = ""
    for i, item in enumerate(top5, 1):
        prefix = "🔥" if item["is_breaking"] else f"{i}️⃣" if not raw else f"{i}."
        body += (
            f"{prefix} <b>{item['title_en']}</b>\n{item['summary_en']}\n"
            f"📌 <b>{item['title_vi']}</b>\n{item['summary_vi']}\n"
            f"🔗 <a href='{item['link']}'>Read more</a>\n\n" if not raw else
            f"{prefix} {item['title_vi']}\n{item['summary_vi']}\nLink: {item['link']}\n\n"
        )

    footer = "📺 <i>Bản tin tổng hợp dành cho kênh YouTube CK Crypto</i>" if not raw else "Nguồn: CK Crypto Bot – Tự động tổng hợp"
    return title + body + footer

def save_txt_report(text):
    vn_today = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y%m%d")
    file_path = f"daily_summary_{vn_today}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"✅ Saved .txt summary to: {file_path}")

def main():
    entries = load_daily_log()
    if not entries:
        print("⚠️ No log entries found today.")
        return

    # HTML version for Telegram
    html_message = generate_report(entries, raw=False)
    send_telegram(html_message)

    # Clean text version for file
    txt_message = generate_report(entries, raw=True)
    save_txt_report(txt_message)

    print("✅ Daily summary sent & saved.")

if __name__ == "__main__":
    main()
