import time
from crawlers.base_crawler import BaseCrawler
from datetime import datetime
from save_to_firestore import save_job_posting

class JobKoreaCrawler(BaseCrawler):
    """ 잡코리아 채용 정보를 크롤링하는 크롤러 """

    def __init__(self):
        super().__init__("https://www.jobkorea.co.kr")
        self.base_search_url = f"{self.base_url}/Search/?stext=개발자&tabType=recruit&Page_No=1"
        self.max_pages = 20  # 페이지 탐색 제한 (추후 변경 가능)

        # ✅ 자기소개서 문항 리스트
        self.self_intro_questions = [
            "1. 이 직무에 지원한 동기를 설명해 주세요.",
            "2. 관련 경험과 성과를 구체적으로 기술해 주세요.",
            "3. 협업 경험 및 갈등 해결 방법을 설명해 주세요."
        ]

    def crawl_jobs(self):
        """ 잡코리아 채용 리스트 페이지에서 공고 수집 """
        print("🔍 잡코리아 채용 리스트 크롤링 시작...")
        job_list = []

        for page_no in range(1, self.max_pages + 1):
            url = f"{self.base_search_url}{page_no}"
            soup = self.fetch_page(url)

            if not soup:
                print(f"❌ {page_no} 페이지를 가져오지 못함")
                continue

            job_elements = soup.select("div.list-default > ul > li")

            if not job_elements:
                print(f"❌ 잡코리아 {page_no} 페이지에서 공고 없음")
                break  # 더 이상 공고가 없으면 중단

            for job in job_elements:
                title_element = job.select_one("a.title")
                company_element = job.select_one("a.name.dev_view")
                exp_element = job.select_one("span.exp")
                edu_element = job.select_one("span.edu")
                loc_element = job.select_one("span.loc.long")
                date_element = job.select_one("span.date")
                keywords_element = job.select_one("p.etc")

                if title_element and company_element:
                    job_url = f"{self.base_url}{title_element['href']}" if title_element.has_attr("href") else "링크 없음"

                    job_info = {
                        "site": "JobKorea",
                        "URL": job_url,
                        "company": company_element.get_text(strip=True),
                        "createdAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "deadline": date_element.get_text(strip=True) if date_element else "마감일 정보 없음",
                        "id": None,
                        "isApplied": False,
                        "job": title_element.get_text(strip=True),
                        "jobDescription": "상세 정보 없음",
                        "jobType": exp_element.get_text(strip=True) if exp_element else "경력 정보 없음",
                        "preferredQualifications": edu_element.get_text(strip=True) if edu_element else "학력 요건 없음",
                        "qualifications": "자격 요건 없음",
                        "location": loc_element.get_text(strip=True) if loc_element else "위치 정보 없음",
                        "keywords": keywords_element.get_text(strip=True) if keywords_element else "키워드 없음",
                        "questions": self.self_intro_questions
                    }

                    job_list.append(job_info)
                    time.sleep(0.1)  # 크롤링 속도 조절

            print(f"📄 {page_no} 페이지 크롤링 완료 (총 {len(job_list)}개 수집)")

        return job_list
