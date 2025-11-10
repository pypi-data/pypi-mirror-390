from selenium.webdriver.common.by import By
from crawlers.crawler import Crawler 
import time
import re
from article import Article as DataArticle
from datetime import datetime

# https://news.kbs.co.kr/news/pc/search/search.do?query={검색어j}&sortType=date&filter=1&page=1&rpage=1
class KBSCrawler(Crawler):
    # 기사링크 수집
    def collect_article_links(self):
        i = 0
        current_page = 1
        while(i < self.count):
            base_url = f"https://news.kbs.co.kr/news/pc/search/search.do?query={self.keyword}&sortType=date&filter=1&page={current_page}&rpage=1"
            self.driver.get(base_url)
            time.sleep(1.5)
            articles = self.driver.find_elements(By.CSS_SELECTOR, "a.box-content.flex-style")
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
            title = self.driver.find_element(By.CSS_SELECTOR, "h4.headline-title").text
        except:
            title = ""
        try:
            content = self.driver.find_element(By.ID, "cont_newstext").text
            # 추출된 본문 안에 내용이 공백 또는 개행 문자로만 이루어져 있는지 확인하는 정규식 표현 
            if content == "" or bool(re.fullmatch(r'[ \n]*', content)): return None
            # 개행 문자가 두 개 이상 노출 시 하나로 축약
            content = re.sub(r'\n{2,}', '\n', content)
        except:
            return None
        dt = self.driver.find_element(By.CSS_SELECTOR, "div.dates em.input-date").text
        dt = dt[3:]
        dt = datetime.strptime(dt, "%Y.%m.%d (%H:%M)")
        dt = dt.strftime("%y-%m-%d:%H")
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
    crawler = KBSCrawler(keyword="민생지원", site="kbs", count=20)
    crawler.run()
