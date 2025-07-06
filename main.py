
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
    "2차전지", "韓", "中", "배터리", "4인뱅", "저출산", "인구정책", "K콘텐츠", "출산", "특징주", 
"4인터넷", "5G", "AI", "AI고속도로", "AI반도체", "AR", "AWS", "BMS", "ESS", "FDA승인", "GPT", "GPT칩", "IRA", 
"K문화", "K뷰티", "K콘텐츠", "LNG", "NFT", "SG", "SMR", "SOC", "STO", "VR", "ai", "ai고속도로", "ai반도체", 
"ar", "aws", "bms", "블록체인", "챗GPT", "구글", "국내최초", "국가전략산업", "국산화", "데이터센터", "대북지원", 
"대왕고래", "대통령", "대체에너지", "딥러닝", "라이다", "로보택시", "로봇", "로봇눈", "로봇손", "마귀상어", 
"메타", "메타버스", "면역항암제", "모빌리티", "바이오", "방사능", "방산", "백신", "북극항로", "블랙웰", 
"비만치료제", "사이버보안", "산불", "상용화", "생명공학", "석유", "세계최대", "세계최초", "스마트공장", 
"스마트시티", "스마트안경", "스마트팩토리", "스마트팜", "속보", "수소", "수출계약", "수출공시", "수출허가", 
"수해", "스테이블코인", "스타트업", "시황", "실시간 속보", "신약", "안전", "알래스카", "알츠하이머", 
"애플", "양자컴퓨터", "에너지고속도로", "에너지정책", "에너지안보", "에너지저장장치", "엔비디아", "여론", 
"예비타당성", "옵티머스", "원유", "원전", "원전건설", "원전해체", "유전자치료", "이차전지", "이재명", 
"인터넷은행", "임상", "임상1상", "임상2상", "임상3상", "임상완료", "자율주행", "자동차", "재건", "재난", 
"재생에너지", "전기차", "전력", "전력망", "전선", "전자결제", "전쟁", "전쟁위험", "정비사업", "정부주도", 
"정부지원", "제재완화", "제재해제", "지역화폐", "지능형로봇", "지진", "진단기기", "진단시약", "진단키트", 
"차세대배터리", "챗gpt", "철강", "초고속인터넷", "초소형모듈원자로", "초전도체", "치매", "친환경에너지", 
"카카오페이", "카지노", "클라우드", "키오스크", "탄소배출권", "탄소중립", "탄소세", "탄소포집", "테슬라", 
"트럼프", "특허", "특허등록", "특허취득", "특허획득", "특징주", "투자유치", "핀테크", "핑크퐁", "풍력", 
"퓨리오사", "해상풍력", "해저터널", "해외수주", "핵심기술", "핵심소재", "핵폐기물", "화장품", "환경규제", 
"황사", "황사경보", "황사주의보", "황사특보", "황사피해", "휴머노이드", "휴전", "희토류", "잭슨황", 
"우주항공", "항공사", "항공우주", "한류", "한한령", "생명과학", "줄기세포", "mRNA", "ms", "네이버페이", 
"리튬", "니켈", "도시재생", "규제완화", "감세", "세제혜택", "李", "兆", "美", "한미", "폭염", "러시아", 
"우크라이나", "세종이전", "구리", "K반도체", "피부암", "피부암 재생", "피부재생", "연골재생", "플랫폼", "동물대체", "식약처", "재생의료", "장기재생", "동물시험", "친환경소재", "플라스틱", "선박", "조선", "드론", "헬스케어", "인공장기", "장기이식", "이스라엘", "이란", "하마스", "중국", "신약개발", "세포치료제", "항체치료제", "토큰", "디지털자산", "가상화폐", "철강", "가스"]

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
                bot.send_message(chat_id=CHAT_ID, text=f"[{title}]\n{link}")
        except Exception:
            continue

if __name__ == "__main__":
    load_sent_links()
    while True:
        fetch_and_filter_html_news()
        time.sleep(5)
