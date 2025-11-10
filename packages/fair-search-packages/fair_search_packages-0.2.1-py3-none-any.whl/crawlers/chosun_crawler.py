import time
import re
from crawlers.crawler import Crawler 
from article import Article as DataArticle
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# https://www.chosun.com/nsearch/?query={}&page={}&siteid=&sort=1&date_period=&date_start=&date_end=&writer=&field=&emd_word=&expt_word=&opt_chk=false&app_check=0&website=www,chosun&category=
class ChosunCrawler(Crawler):
    # 기사링크 수집
    def collect_article_links(self):
        i = 0
        current_page = 1
        while(i < self.count):
            base_url = f"https://www.chosun.com/nsearch/?query={self.keyword}&page={current_page}&siteid=&sort=1&date_period=&date_start=&date_end=&writer=&field=&emd_word=&expt_word=&opt_chk=false&app_check=0&website=www,chosun&category="
            self.driver.get(base_url)
            time.sleep(1.5)
            articles = self.driver.find_elements(By.CSS_SELECTOR, "div.story-card-right a.text__link.story-card__headline")
            links_dict = {"page" : current_page, "links" : []}
            for article in articles:
                try:
                    href = article.get_attribute("href")
                    if href and (href not in links_dict["links"]):
                        links_dict['links'].append(href)
                        i += 1
                        if i == self.count: 
                            self.article_links.append(links_dict)
                            return
                except:
                    continue
            self.article_links.append(links_dict)
            current_page += 1
            if current_page > self.max_pages : return

    # 기사제목과 기사본문 추출
    def extract_article_data(self, url, index, page):
        self.driver.get(url)
        try:
            title = self.driver.find_element(By.CSS_SELECTOR, "h1.article-header__headline").text
        except:
            title = ""
        
        try:
            # 기사 본문 p 태그 리스트 추출
            contents = self.driver.find_elements(By.CSS_SELECTOR, "p.article-body__content.article-body__content-text")
            # 텍스트만 추출 후 \n으로 연결
            content = "\n".join([p.text.strip() for p in contents])
            if content == "" or bool(re.fullmatch(r'\n*', content)): return None
        except:
            return None
        
        dt = extract_chosun_datetime(self.driver, prefer="input")  # 또는 "update"
        print(f"✅ 수집 완료: {title}... / {content[:30]}... 총 : {len(content)}자 / 날짜 : {dt}")
        return DataArticle(**{
            "title": title, 
            "content": content, 
            "url" : url, 
            "index" : index+1, 
            "page" : page, 
            "keyword" : self.keyword,
            "site" : self.site,
            "media" : self.site,
            "datetime" : dt
        })



# 2025.07.16. 18:09 / 2025.07.16 18:09 모두 허용
CHOSUN_DT_RE = re.compile(r'(\d{4}\.\d{2}\.\d{2})\.?\s+(\d{2}:\d{2})')

def extract_chosun_datetime(driver, prefer="input"):  # "input" or "update"
    """
    조선닷컴 기사 상세에서 날짜 파싱.
    1) dateBox 컨테이너 탐색
    2) inputDate/upDate 둘 다 시도
    3) 비어 있으면 page_source에서 폴백
    반환: "YYYY-MM-DD:HH"
    """
    # 1) dateBox 대기
    date_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.dateBox, .dateBox"))
    )
    # 가시화/스크롤 보정
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", date_box)
    except Exception:
        pass

    # 2) 두 줄 각각 텍스트 추출
    def get_text(sel):
        els = date_box.find_elements(By.CSS_SELECTOR, sel)
        if not els:
            return ""
        t = (els[0].text or "").strip().replace("\xa0", " ")
        return t

    # 가끔 늦게 채워지므로 짧은 대기 (최대 5초)
    try:
        WebDriverWait(driver, 5).until(
            lambda d: any((get_text("span.inputDate"), get_text("span.upDate")))
        )
    except Exception:
        pass

    input_raw  = get_text("span.inputDate")  # 예: "입력\n2025.07.16. 17:40"
    update_raw = get_text("span.upDate")     # 예: "업데이트 2025.07.16. 18:09"

    # 라벨 제거 후 정규식으로 날짜만 추출
    def parse_one(raw: str):
        raw = raw.replace("입력", "").replace("업데이트", "").strip()
        m = CHOSUN_DT_RE.search(raw)
        if not m:
            return None
        ymd, hm = m.group(1), m.group(2)
        return datetime.strptime(f"{ymd} {hm}", "%Y.%m.%d %H:%M")

    dt_obj = None
    if prefer == "input":
        dt_obj = parse_one(input_raw) or parse_one(update_raw)
    else:
        dt_obj = parse_one(update_raw) or parse_one(input_raw)

    # 3) 여전히 없으면 page_source 폴백
    if dt_obj is None:
        m = CHOSUN_DT_RE.search(driver.page_source)
        if not m:
            raise ValueError(f"날짜 파싱 실패: input={input_raw!r}, update={update_raw!r}")
        dt_obj = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y.%m.%d %H:%M")

    return dt_obj.strftime("%Y-%m-%d:%H")

    

if __name__ == "__main__":
    crawler = ChosunCrawler(keyword="민생회복", site="chosun",count=3)
    # 흐음... 
    import asyncio
    asyncio.run(crawler.run())
    