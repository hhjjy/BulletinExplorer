from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup



#靜態類別 輸入網址轉類別
class ScraperFactory:
    @staticmethod
    def get_scraper(url):
        # 根據不同的網址返回不同的爬蟲實例
        if "bulletin.ntust.edu.tw" in url:
            return NTUSTBulletinScraper(url)
        elif "lc.ntust.edu.tw" in url:
            return NTUSTLanguageCenterScraper(url)
        elif "www.ntust.edu.tw" in url:
            return NTUSTMajorAnnouncementScraper(url)
        else:
            raise ValueError(f"No scraper found for the given URL: {url}")



# 基礎爬蟲類
class Scraper(ABC):
    def __init__(self, url):
        self.url = url

    @abstractmethod
    def scrape(self):
        pass
# 台科大公佈欄爬蟲
# https://bulletin.ntust.edu.tw/p/403-1045-1391-1.php?Lang=zh-tw
class NTUSTBulletinScraper(Scraper):
    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find("table")# 找table 標籤 
        thead = table.find("thead")# 從table 找第一個匹配的
        tbody = table.find("tbody")# 從table找第一個匹配的

        # # Process the table one row at a time
        i = 1
        data = [] 
        for row in tbody.find_all("tr"):
            data_row = [] 
            date = row.find("td",{"data-th":"日期"}).get_text(strip=True)            
            publisher = row.find("td",{"data-th":"發佈單位"}).get_text(strip=True)
            title = row.find("td",{"data-th":"標題"}).get_text(strip=True)
            a_tag = row.find("a")
            url = a_tag['href'] if a_tag and 'href' in a_tag.attrs else None
            content = "" # 從url去爬連結內文
            if url != None:
                webpage = requests.get(url)
                soup = BeautifulSoup(webpage.content, 'html.parser')
                paragraphs = soup.find_all("p")
                for p in paragraphs:
                    content += p.get_text(strip=True)
            data.append({'date':date,'publisher':publisher,'title':title,'url':url,'content':content})
        return data

        

# 台科大語言中心爬蟲
class NTUSTLanguageCenterScraper(Scraper):
    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 添加針對台科大語言中心的爬蟲邏輯
        print("Scraping NTUST Language Center...")
    
# 台科大校網公布欄爬蟲
class NTUSTMajorAnnouncementScraper(Scraper):
    def scrape(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 添加針對台科大校網公布欄的爬蟲邏輯
        print("Scraping NTUST Major Announcements...")



