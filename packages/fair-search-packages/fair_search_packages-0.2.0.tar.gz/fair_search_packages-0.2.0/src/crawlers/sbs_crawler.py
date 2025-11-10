from selenium.webdriver.common.by import By
from crawlers.crawler import Crawler 
import time
import re
from article import Article as DataArticle
from datetime import datetime

#https://news.sbs.co.kr/news/search/result.do?query={}&tabIdx=2&pageIdx={}
class SBSCrawler(Crawler):
    # 기사링크 수집
    def collect_article_links(self):
        i = 0
        current_page = 1
        while(i < self.count):
            base_url = f"https://news.sbs.co.kr/news/search/result.do?query={self.keyword}&tabIdx=2&pageIdx={current_page}"
            self.driver.get(base_url)
            time.sleep(1.5)
            articles = self.driver.find_elements(By.CSS_SELECTOR, "a.news")
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
            title = self.driver.find_element(By.CSS_SELECTOR, "h1.article_main_tit").text
        except:
            title = ""
        try:
            content = self.driver.find_element(By.CSS_SELECTOR, "div.text_area").text
            # 추출된 본문 안에 내용이 공백 또는 개행 문자로만 이루어져 있는지 확인하는 정규식 표현 
            if content == "" or bool(re.fullmatch(r'[ \n]*', content)): return None
            # 개행 문자가 두 개 이상 노출 시 하나로 축약
            content = re.sub(r'\n{2,}', '\n', content)
        except:
            return None
        
        dt = self.driver.find_element(By.CSS_SELECTOR, "div.date_area span").text
        # "입력 " 길이 제외하기 
        try:
            dt = datetime.strptime(dt, "%y.%m.%d %H:%M")
            dt = dt.strftime("%y-%m-%d:%H")
        except:
            from datetime import timedelta, timezone
            KST = timezone(timedelta(hours=9))
            kst_now = datetime.now(KST)
            dt = kst_now.strftime("%y-%m-%d:%H")
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
    crawler = SBSCrawler(keyword="이재명", site="sbs", count=5)
    crawler.run()
