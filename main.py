import requests
import feedparser
import os
import html
import re
import json
from datetime import datetime
import pytz
from translate import Translator

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

KEYWORDS = ['bitcoin', 'ethereum', 'etf', 'sec', 'binance', 'XRP', 'SOL', 'ADA', 'Crypto news', 'Altcoin']
BREAKING_KEYWORDS = ['breaking', 'urgent', 'hacked', 'exploit', 'lawsuit', 'ban', 'approval', 'rejected', 'SEC', 'ETF']
RSS_FEEDS = [
    'https://www.coindesk.com/arc/outboundfeeds/rss/',
    'https://cointelegraph.com/rss',
    'https://cryptoslate.com/feed/'
]

def get_today_id_file():
    today = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%Y%m%d")
    return f"sent_ids_{today}.json"

def load_sent_ids():
    path = get_today_id_file()
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()

def save_sent_ids(sent_ids):
    path = get_today_id_file()
    with open(path, "w") as f:
        json.dump(list(sent_ids), f)

def translate_to_vietnamese(text):
    try:
        return Translator(to_lang="vi").translate(text)
    except:
        return text

def clean_html(text):
    text = html.unescape(text)
    return re.sub(r'<[^>]+>', '', text).strip()

def truncate(text, max_length=300):
    return text if len(text) <= max_length else text[:max_length].rsplit(' ', 1)[0] + '...'

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

def is_today(entry_time):
    vn_now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    entry_dt = datetime(*entry_time[:6], tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))
    return entry_dt.date() == vn_now.date()

def send_today_news():
    print("📢 Checking news...")
    sent_ids = load_sent_ids()
    new_ids = set()

    entries = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            eid = entry.link.strip()
            if eid in sent_ids:
                continue
            if not hasattr(entry, 'published_parsed') or not is_today(entry.published_parsed):
                continue
            content = (entry.title + entry.get('summary', '')).lower()
            if any(k in content for k in [k.lower() for k in KEYWORDS]):
                entries.append((entry, eid))

    entries = sorted(entries, key=lambda x: getattr(x[0], 'published_parsed', datetime.now().timetuple()), reverse=True)[:2]

    for entry, eid in entries:
        title_en = clean_html(entry.title)
        summary_en = truncate(clean_html(entry.get("summary", "")))
        title_vi = translate_to_vietnamese(title_en)
        summary_vi = translate_to_vietnamese(summary_en)
        link = entry.link

        is_breaking = any(k in (entry.title + entry.get('summary', '')).lower() for k in [k.lower() for k in BREAKING_KEYWORDS])
        prefix = "🔥 <b>BREAKING:</b>\n" if is_breaking else "📰 <b>TIN MỚI:</b>\n"

        message = (
            f"{prefix}<b>{title_en}</b>\n{summary_en}\n\n"
            f"📌 <b>{title_vi}</b>\n{summary_vi}\n\n"
            f"🔗 <a href='{link}'>Read more</a>"
        )

        send_telegram(message)
        new_ids.add(eid)

    if new_ids:
        sent_ids.update(new_ids)
        save_sent_ids(sent_ids)
        print(f"✅ Sent {len(new_ids)} news")
    else:
        print("✅ No new news to send.")

if __name__ == "__main__":
    send_today_news()
