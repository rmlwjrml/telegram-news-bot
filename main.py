
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from telegram import Bot
import pytz
import time
import os

kst = pytz.timezone('Asia/Seoul')
TELEGRAM_TOKEN = "7513053048:AAGhoPamVwZhGYqztK0huXWxg0FQ1W204fI"  # ✅ Bot C 전용 (HTML용)
CHAT_ID = "5639589613"
bot = Bot(token=TELEGRAM_TOKEN)

sent_links_file = "sent_links.txt"
sent_titles = set()

def load_sent_links():
    global sent_titles
    now = datetime.now(kst)
    three_days_ago = now - timedelta(days=3)
    if os.path.exists(sent_links_file):
        with open(sent_links_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            parts = line.strip().split("|")
            if len(parts) != 3:
                continue
            site, title, date_str = parts
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                if date_obj >= three_days_ago:
                    sent_titles.add(f"{site}|{title}")
                    new_lines.append(line.strip())
            except:
                continue
        with open(sent_links_file, "w", encoding="utf-8") as f:
            for line in new_lines:
                f.write(line + "\n")

def save_sent_title(site, title):
    now_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
    with open(sent_links_file, "a", encoding="utf-8") as f:
        f.write(f"{site}|{title}|{now_str}\n")

keywords = [
    "2차전지", "배터리", "로봇", "AI", "GPT", "속보", "특징주", "전기차", "수소", "바이오", "우주항공", "항공사",
    "전력", "재생에너지", "AI반도체", "AI고속도로", "데이터센터", "스마트공장", "메타버스", "딥러닝",
    "자율주행", "임상", "FDA승인", "비만치료제", "면역항암제", "초전도체", "양자컴퓨터", "ESS", "BMS",
    "에너지저장장치", "클라우드", "핀테크", "전자결제", "SMR", "LNG", "친환경에너지", "K콘텐츠", "mRNA",
    "알츠하이머", "줄기세포", "재건", "국산화", "K뷰티", "AI고속도로", "K문화", "K콘텐츠", "챗GPT", "AI",
    "핵심소재", "수출계약", "해저터널", "탄소배출권", "탄소포집", "탄소세", "탄소중립", "풍력", "해상풍력",
    "우크라이나", "대북", "북한", "미사일", "전쟁", "휴전", "핵", "방산", "방사능", "국방"
]

html_sites = [
    {
        "name": "전자신문",
        "url": "https://www.etnews.com/news/economy",
        "list_selector": "ul.list_news > li",
        "title_selector": "a",
        "link_attr": "href",
        "encoding": "utf-8"
    },
    {
        "name": "서울경제",
        "url": "https://www.sedaily.com/NewsList/GB01",
        "list_selector": "div.list_area > ul > li",
        "title_selector": "a",
        "link_attr": "href",
        "encoding": "utf-8"
    },
    {
        "name": "디지털타임스",
        "url": "https://www.dt.co.kr/contents.html?section=net",
        "list_selector": "ul.list > li",
        "title_selector": "a",
        "link_attr": "href",
        "encoding": "euc-kr"
    },
    {
        "name": "ZDNet코리아",
        "url": "https://zdnet.co.kr/news/news_list.asp?z=0101",
        "list_selector": "ul.news_list > li",
        "title_selector": "a",
        "link_attr": "href",
        "encoding": "utf-8"
    },
    {
        "name": "한경닷컴",
        "url": "https://www.hankyung.com/economy",
        "list_selector": "ul.main-news-list > li",
        "title_selector": "a",
        "link_attr": "href",
        "encoding": "utf-8"
    },
    {
        "name": "이투데이",
        "url": "https://www.etoday.co.kr/news/section?MID=1020",
        "list_selector": "div.newsList > ul > li",
        "title_selector": "a",
        "link_attr": "href",
        "encoding": "utf-8"
    },
    {
        "name": "헤럴드경제",
        "url": "https://biz.heraldcorp.com/list.php?ct=020000000000",
        "list_selector": "ul.list_news > li",
        "title_selector": "a",
        "link_attr": "href",
        "encoding": "utf-8"
    },
    {
        "name": "약업신문",
        "url": "https://www.yakup.com/news/index.html?num_start=1",
        "list_selector": "div.news_list > ul > li",
        "title_selector": "a",
        "link_attr": "href",
        "encoding": "euc-kr"
    },
    {
        "name": "지디넷코리아",
        "url": "https://zdnet.co.kr/news/news_list.asp?z=0201",
        "list_selector": "ul.news_list > li",
        "title_selector": "a",
        "link_attr": "href",
        "encoding": "utf-8"
    },
]

def fetch_and_filter_html_news():
    now = datetime.now(kst)
    five_minutes_ago = now - timedelta(minutes=5)

    for site in html_sites:
        try:
            res = requests.get(site["url"], timeout=5)
            res.encoding = site.get("encoding", "utf-8")
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select(site["list_selector"])
            for item in items:
                a_tag = item.select_one(site["title_selector"])
                if not a_tag:
                    continue
                title = a_tag.get_text(strip=True)
                link = a_tag.get(site["link_attr"], "")
                if not link or "youtube.com" in link or "youtu.be" in link:
                    continue
                if not link.startswith("http"):
                    link = "https:" + link if link.startswith("//") else site["url"].split("/news")[0] + link
                if not title or not any(k in title for k in keywords):
                    continue
                unique_key = f"{site['name']}|{title}"
                if unique_key in sent_titles:
                    continue
                sent_titles.add(unique_key)
                save_sent_title(site['name'], title)
                bot.send_message(chat_id=CHAT_ID, text=f"[{title}]
{link}")
        except Exception:
            continue

if __name__ == "__main__":
    load_sent_links()
    while True:
        fetch_and_filter_html_news()
        time.sleep(5)
