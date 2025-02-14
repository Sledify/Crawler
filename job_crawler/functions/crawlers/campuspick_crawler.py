from crawlers.base_crawler import BaseCrawler
from datetime import datetime
from save_to_firestore import save_job_posting

class CampickCrawler(BaseCrawler):
    """ 캠퍼스픽 채용 정보를 크롤링하는 크롤러 """

    def __init__(self):
        super().__init__("https://www.campuspick.com")
        self.job_list_url = f"{self.base_url}/study?category=5"

        # ✅ 자기소개서 문항 리스트 (캠퍼스픽에 맞게 수정)
        self.self_intro_questions = [
            "1. 이 스터디에 지원한 이유를 설명하세요.",
            "2. 본인의 역할과 기대하는 점을 서술하세요.",
            "3. 팀원들과 협업 시 중요하게 생각하는 가치는 무엇인가요?"
        ]

    def extract_job_details(self, job_url):
        """ 상세 채용 공고에서 정보 크롤링 """
        soup = self.fetch_page(job_url)
        if not soup:
            return {
                "jobDescription": "포지션 상세 없음",
                "jobType": "스터디/공모전",
                "preferredQualifications": "우대사항 없음",
                "qualifications": "자격 요건 없음",
                "deadline": "마감일 정보 없음"
            }

        # ✅ 제목 및 마감일 정보
        job_title_element = soup.select_one("article h2")
        job_title = job_title_element.get_text(strip=True) if job_title_element else "공고 제목 없음"

        deadline_element = soup.select_one("p.info > span:nth-child(1)")
        deadline = deadline_element.get_text(strip=True) if deadline_element else "마감일 정보 없음"

        # ✅ 근무 형태
        job_type = "스터디/공모전"

        # ✅ 경력 요건 (캠퍼스픽에는 별도 표기가 없으므로 기본값 설정)
        qualifications = "자격 요건 없음"
        preferred_qualifications = "우대사항 없음"

        # ✅ 상세 설명
        job_description_element = soup.select_one("article p.text")
        job_description = job_description_element.get_text(strip=True) if job_description_element else "포지션 상세 없음"

        return {
            "job": job_title,
            "jobDescription": job_description,
            "jobType": job_type,
            "preferredQualifications": preferred_qualifications,
            "qualifications": qualifications,
            "deadline": deadline
        }

    def crawl_jobs(self):
        """ 캠퍼스픽 채용 리스트 페이지에서 공고 수집 """
        print("🔍 캠퍼스픽 채용 리스트 크롤링 시작...")
        soup = self.fetch_page(self.job_list_url)
        if not soup:
            return []

        job_elements = soup.select("div.list > a")
        job_list = []

        for job in job_elements[:10]:  # 최대 10개 크롤링
            title_element = job.select_one("h2")
            company_element = job.select_one("p.profile")
            link_element = job["href"] if job.has_attr("href") else None

            if title_element and company_element and link_element:
                job_url = f"{self.base_url}{link_element}"

                print(f"📌 상세 페이지 크롤링 시작: {job_url}")

                # ✅ 2차 크롤링 중단하고, 기본 정보만 수집
                job_info = {
                    "site": "Campick",
                    "URL": job_url,
                    "company": company_element.get_text(strip=True),
                    "createdAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "deadline": "마감일 정보 없음",
                    "id": None,
                    "isApplied": False,
                    "job": title_element.get_text(strip=True),
                    "jobDescription": "상세 정보 없음",
                    "jobType": "스터디/공모전",
                    "preferredQualifications": "우대사항 없음",
                    "qualifications": "자격 요건 없음",
                    "questions": self.self_intro_questions
                }

                job_list.append(job_info)

        return job_list
