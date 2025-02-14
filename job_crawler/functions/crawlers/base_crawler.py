import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

class BaseCrawler(ABC):
    """ 모든 크롤러가 상속받을 기본 크롤러 클래스 """

    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_page(self, url):
        """ 페이지 요청 및 BeautifulSoup 변환 """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"❌ 요청 실패 ({url}): {e}")
            return None

    @abstractmethod
    def crawl_jobs(self):
        """ 크롤링 메서드 (각 크롤러에서 구현) """
        pass
