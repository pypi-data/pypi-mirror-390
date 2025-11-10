from selenium.webdriver.common.by import By
from crawlers.crawler import Crawler 
import time
import re
from article import Article as DataArticle
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 중앙일보
# https://www.koreadaily.com/search?searchWord=%EB%AF%BC%EC%83%9D+%EC%A0%95%EC%B1%85&searchType=all&highLight=true&page=1
class KoreaCrawler(Crawler):
    # 기사링크 수집
    def collect_article_links(self):
        i = 0
        current_page = 1
        while(i < self.count):
            base_url = f"https://www.koreadaily.com/search?searchWord={self.keyword}&searchType=all&highLight=true&page={current_page}"
            self.driver.get(base_url)
            time.sleep(1.5)
            articles = self.driver.find_elements(By.CSS_SELECTOR, "div.newsList a")
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

    # 기사제목과 원본 추출
    def extract_article_data(self, url, index, page):
        self.driver.get(url)
        try:
            title = self.driver.find_element(By.CSS_SELECTOR, "div.headline h1").text
        except:
            title = ""
        try:
            # 기사 본문 p 태그 리스트 추출
            content = self.driver.find_element(By.CSS_SELECTOR, "section#newsBody").text
            # 추출된 본문 안에 내용이 공백 또는 개행 문자로만 이루어져 있는지 확인하는 정규식 표현 
            if content == "" or bool(re.fullmatch(r'[ \n]*', content)): return None
            # 개행 문자가 두 개 이상 노출 시 하나로 축약
            content = re.sub(r'\n{2,}', '\n', content)
        except:
            return None
        dt = extract_koreadaily_dt(self.driver)
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


def _get_text_or_before(driver, el):
    """일반 텍스트 우선, 없으면 ::before content를 읽어 반환"""
    text = (el.text or "").strip().replace("\xa0", " ")
    if text:
        return text
    # ::before content 읽기 (양쪽에 따옴표가 포함되어 옴)
    content = driver.execute_script(
        "return window.getComputedStyle(arguments[0],'::before').getPropertyValue('content');",
        el
    )
    if not content:
        return ""
    content = content.strip()
    # content는 보통 '"2025.08.10 06:52"' 식으로 따옴표 포함 → 제거
    if len(content) >= 2 and content[0] in ("'", '"') and content[-1] == content[0]:
        content = content[1:-1]
    return content.strip().replace("\xa0", " ")

def extract_koreadaily_dt(driver):
    """코리아데일리 기사 상세에서 입력/업데이트 시각 중 하나를 파싱해 'YYYY-MM-DD:HH' 반환"""

    # 2025.08.10 06:52 또는 2025.08.10. 06:52 모두 허용
    DT_RE = re.compile(r'(\d{4}\.\d{2}\.\d{2})\.?\s+(\d{2}:\d{2})')
    # 날짜 박스가 보일 때까지 대기
    date_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.dateBox"))
    )
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", date_box)
    except Exception:
        pass

    # 후보 요소 수집: 입력/업데이트
    input_els = date_box.find_elements(By.CSS_SELECTOR, "p.dateTime span.input, span.input")
    update_els = date_box.find_elements(By.CSS_SELECTOR, "span.update")

    texts = []
    for el in input_els + update_els:
        t = _get_text_or_before(driver, el)
        if t:
            texts.append(t)

    # 컨테이너 전체 텍스트도 폴백으로 시도
    box_text = (date_box.text or "").strip().replace("\xa0", " ")
    if box_text:
        texts.append(box_text)

    # 정규식으로 첫 유효한 날짜 추출
    for t in texts:
        m = DT_RE.search(t)
        if m:
            ymd, hm = m.group(1), m.group(2)
            dt_obj = datetime.strptime(f"{ymd} {hm}", "%Y.%m.%d %H:%M")
            return dt_obj.strftime("%Y-%m-%d:%H")

    # 최후 폴백: 페이지 소스에서 검색
    m = DT_RE.search(driver.page_source)
    if m:
        dt_obj = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y.%m.%d %H:%M")
        return dt_obj.strftime("%Y-%m-%d:%H")

    raise ValueError("코리아데일리 날짜를 찾지 못했습니다.")


if __name__ == "__main__":
    crawler = KoreaCrawler(keyword="이재명", site="korea", count=10)
    crawler.run()
