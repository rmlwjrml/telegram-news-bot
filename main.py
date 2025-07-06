import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from telegram import Bot
import pytz
import time
import os

# 1. 환경 설정
kst = pytz.timezone('Asia/Seoul')
TELEGRAM_TOKEN = "7513053048:AAGhoPamVwZhGYqztK0huXWxg0FQ1W204fI"  # 예: "1234:AA..."
CHAT_ID = "5639589613"        # 예: "5639589613"
bot = Bot(token=TELEGRAM_TOKEN)

# 2. 중복 필터용 파일
sent_titles_file = "sent_titles.txt"
sent_titles = set()

def load_sent_titles():
    now = datetime.now(kst)
    three_days_ago = now - timedelta(days=1)
    if os.path.exists(sent_titles_file):
        with open(sent_titles_file, "r", encoding="utf-8") as f:
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
                    sent_titles.add((site, title))
                    new_lines.append(line.strip())
            except:
                continue
        with open(sent_titles_file, "w", encoding="utf-8") as f:
            for line in new_lines:
                f.write(line + "\n")

def save_sent_title(site, title):
    now_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
    with open(sent_titles_file, "a", encoding="utf-8") as f:
        f.write(f"{site}|{title}|{now_str}\n")

load_sent_titles()

# 3. 키워드 목록 (대폭 추가)
keywords = [
    "2차전지", "AI", "AI반도체", "AI고속도로", "GPT", "GPT칩", "챗GPT", "로봇",
    "전기차", "자율주행", "우주항공", "원전", "수소", "석유", "천연가스", "탄소중립",
    "반도체", "미국", "중국", "삼성", "SK", "LG", "비만치료제", "mRNA", "임상", "신약",
    "재건", "우크라이나", "북한", "대북", "방산", "국방", "국가전략산업", "속보", "실시간",
    "SMR", "ESS", "BMS", "클라우드", "K콘텐츠", "한미", "전력", "재생에너지", "친환경", "NFT"
]

# 4. HTML 기반 뉴스 채널 (20개 이상 테스트용)
news_sites = {
    "전자신문": "https://www.etnews.com/news/economy",
    "연합뉴스": "https://www.yna.co.kr/economy/all",
    "이데일리": "https://www.edaily.co.kr/news",
    "아시아경제": "https://www.asiae.co.kr/list.htm?sec=economy5",
    "인포스탁": "https://www.infostockdaily.co.kr/news/articleList.html?sc_section_code=S1N2",
    "머니투데이": "https://news.mt.co.kr/news_list.html?section=industry",
    "뉴스1": "https://www.news1.kr/industry",
    "파이낸셜뉴스": "https://www.fnnews.com/economy",
    "서울경제": "https://www.sedaily.com/NewsList/GB01",
    "조선비즈": "https://biz.chosun.com/industry/",
    "매일경제": "https://www.mk.co.kr/news/economy/",
    "한경닷컴": "https://www.hankyung.com/economy/",
    "디지털데일리": "https://www.ddaily.co.kr/news/section_list.php?sec_code=02",
    "팍스넷": "https://www.paxnet.co.kr/news/all",
    "브릿지경제": "https://www.viva100.com/main/view.php?key=202",
    "데이터넷": "https://www.datanet.co.kr/news/articleList.html?sc_section_code=S1N1",
    "ZDNet Korea": "https://zdnet.co.kr/news/",
    "약업신문": "https://www.yakup.com/news/index.html?mode=view&cat=1",
    "코메디닷컴": "https://www.kormedi.com/news/",
    "메디칼업저버": "https://www.monews.co.kr/news/articleList.html?sc_section_code=S1N1"
}

# 5. 크롤링 및 키워드 필터링 함수
def fetch_html_news():
    now = datetime.now(kst)
    five_min_ago = now - timedelta(minutes=5)

    for site, url in news_sites.items():
        try:
            resp = requests.get(url, timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")

            # a 태그 중 뉴스 링크 후보 수집
            candidates = soup.find_all("a", href=True)
            for tag in candidates:
                title = tag.get_text(strip=True)
                link = tag["href"]

                # 필터: 비어있거나 너무 짧은 제목 제외
                if not title or len(title) < 8:
                    continue

                # 필터: 유튜브 제외
                if "youtube.com" in link or "youtu.be" in link:
                    continue

                # 링크 상대경로 처리
                if link.startswith("/"):
                    link = url.split("/")[0] + "//" + url.split("/")[2] + link

                # 필터: 중복 뉴스 제거 (같은 채널 + 제목 기준)
                if (site, title) in sent_titles:
                    continue

                # 필터: 키워드 포함 여부
                if not any(k in title for k in keywords):
                    continue

                # 발송 및 저장
                bot.send_message(chat_id=CHAT_ID, text=f"[{site}] {title}\n{link}")
                sent_titles.add((site, title))
                save_sent_title(site, title)

        except Exception as e:
            print(f"[{site}] 크롤링 실패: {e}")
            continue

# 6. 메인 루프
if __name__ == "__main__":
    while True:
        fetch_html_news()
        time.sleep(5)
