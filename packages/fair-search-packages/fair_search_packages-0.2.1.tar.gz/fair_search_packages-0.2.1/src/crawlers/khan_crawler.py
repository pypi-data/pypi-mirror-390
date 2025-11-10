from selenium.webdriver.common.by import By
import time
from datetime import datetime
import re
from crawlers.crawler import Crawler 
from article import Article as DataArticle
from fair_setup import random_datetime

# 경향신문
# https://search.khan.co.kr/?q=검색 키워드&media=khan&page=1&section=1&term=0&startDate=&endDate=&sort=1
# 필요한 데이터 = 기사제목, 기사본문
class KhanCrawler(Crawler):
    # 기사링크 수집
    def collect_article_links(self):
        i = 0
        current_page = 1
        while(i < self.count):
            base_url = f"https://search.khan.co.kr/?q={self.keyword}&media=khan&page={current_page}&section=1&term=0&startDate=&endDate=&sort=1"
            self.driver.get(base_url)
            time.sleep(1.5)
            articles = self.driver.find_elements(By.CSS_SELECTOR, "article a")
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
            title = self.driver.find_element(By.CSS_SELECTOR, "section.article-wrap h1").text
        except:
            title = "제목없음"
        
        try:
            # 기사 본문 p 태그 리스트 추출
            paragraphs = self.driver.find_elements(By.CSS_SELECTOR, "p.content_text.text-l")
            # 텍스트만 추출 후 \n으로 연결
            content = "\n".join([p.text.strip() for p in paragraphs])
            if content == "" or bool(re.fullmatch(r'\n*', content)): return None
        except:
            return None


        # 입력 시간 추출 (기존 코드 보정)
        print(f"{url} parsing start")
        dt_el = self.driver.find_element(By.CSS_SELECTOR, "div.date p")
        if dt_el == "": dt_el = self.driver.find_element(By.CSS_SELECTOR, "div.date a p")
        raw = dt_el.text.strip()           # ← .text로 문자열 꺼내기
        if not raw:  # 비어있으면 펼치기 후 다시 시도
            from selenium.webdriver.support.ui import WebDriverWait 
            self.driver.find_element(By.CSS_SELECTOR, "div.date a").click()
            WebDriverWait(self.driver, 2).until(
                lambda d: any(p.text.strip() for p in d.find_elements(By.CSS_SELECTOR, "div.date p"))
            )
            raw = self.driver.find_element(By.CSS_SELECTOR, "div.date a p").text.strip()

        raw = raw.replace("입력", "").strip()  # '입력 ' 제거+

        # 문자열을 datetime으로 파싱
        try:
            dt = datetime.strptime(raw, "%Y.%m.%d %H:%M")
            dt = dt.strftime("%y-%m-%d:%H")
        except:
            dt = random_datetime()
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
    
if __name__ == "__main__":
    crawler = KhanCrawler(keyword="이재명", site="khan")
    crawler.run()