from crawlers.base_crawler import BaseCrawler
from datetime import datetime
from save_to_firestore import save_job_posting

class SaraminCrawler(BaseCrawler):
    """ 사람인 채용 정보를 크롤링하는 크롤러 """

    def __init__(self):
        super().__init__("https://www.saramin.co.kr")
        self.job_list_url = f"{self.base_url}/zf_user/jobs/list/job-category?page=1&cat_kewd=84"

        # ✅ 자기소개서 문항 리스트
        self.self_intro_questions = [
            "1. 이 부문에 지원한 동기를 기술해 주십시오.",
            "2. 이 직무와 관련된 경험을 본인의 역할과 성과 중심으로 기술해 주십시오.",
            "3. 나와 대다수의 의견이 다른 경우, 본인이 대처했던 경험과 그로부터 얻은 교훈을 기술해 주십시오."
        ]

    def extract_job_details(self, job_url):
        """ 상세 채용 공고에서 정보 크롤링 """
        soup = self.fetch_page(job_url)
        if not soup:
            return {
                "jobDescription": "포지션 상세 없음",
                "jobType": "정규직",
                "preferredQualifications": "우대사항 없음",
                "qualifications": "자격 요건 없음",
                "deadline": "마감일 정보 없음"
            }

        card_element = soup.select_one(".card_cont.wrap_recruit_view")
        deadline = card_element["data-closing-date"] if card_element and "data-closing-date" in card_element.attrs else "마감일 정보 없음"
        job_title = card_element["data-recruit-title"] if card_element and "data-recruit-title" in card_element.attrs else "공고 제목 없음"

        # ✅ 근무 형태 (정규직 등)
        job_type_element = soup.select_one(".section_basic_view .wrap_summary_job .list_summary .type")
        job_type = job_type_element.get_text(strip=True) if job_type_element else "정규직"

        # ✅ 경력 요건
        qualifications_element = soup.select_one(".section_basic_view .wrap_summary_job .list_summary .experience")
        qualifications = qualifications_element.get_text(strip=True).replace("\xa0", " ") if qualifications_element else "자격 요건 없음"

        # ✅ 학력 요건
        preferred_qualifications_element = soup.select_one(".section_basic_view .wrap_summary_job .list_summary .education")
        preferred_qualifications = preferred_qualifications_element.get_text(strip=True).replace("\xa0", " ") if preferred_qualifications_element else "우대사항 없음"

        # ✅ 상세 설명 크롤링 (iframe이 있는 경우)
        job_description = "포지션 상세 없음"
        iframe_element = soup.select_one("iframe.recruit_detail_iframe")

        if iframe_element:
            iframe_src = iframe_element.get("data-src") or iframe_element.get("src")
            if iframe_src:
                iframe_url = f"{self.base_url}{iframe_src}"
                iframe_soup = self.fetch_page(iframe_url)
                if iframe_soup:
                    detail_view = iframe_soup.select_one(".cont_detail_view")
                    if detail_view:
                        job_description = detail_view.get_text(strip=True) or "포지션 상세 없음"

        return {
            "job": job_title,
            "jobDescription": job_description,
            "jobType": job_type,
            "preferredQualifications": preferred_qualifications,
            "qualifications": qualifications,
            "deadline": deadline
        }

    def crawl_jobs(self):
        """ 사람인 채용 리스트 페이지에서 공고 수집 """
        print("🔍 사람인 채용 리스트 크롤링 시작...")
        soup = self.fetch_page(self.job_list_url)
        if not soup:
            return []

        job_elements = soup.select(".list_item")
        job_list = []

        for job in job_elements[:10]:  # 최대 10개 크롤링
            title_element = job.select_one(".job_tit a")
            company_element = job.select_one(".company_nm a")

            if title_element and company_element:
                relative_link = title_element["href"]

                if "rec_idx=" in relative_link:
                    job_url = f"{self.base_url}/zf_user/jobs/relay/view?rec_idx=" + relative_link.split("rec_idx=")[-1].split("&")[0]

                    print(f"📌 상세 페이지 크롤링 시작: {job_url}")

                    # ✅ 2차 크롤링 중단하고, 기본 정보만 수집
                    job_info = {
                        "site": "Saramin",
                        "URL": job_url,
                        "company": company_element.get_text(strip=True),
                        "createdAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "deadline": "마감일 정보 없음",
                        "id": None,
                        "isApplied": False,
                        "job": title_element.get_text(strip=True),
                        "jobDescription": "상세 정보 없음",
                        "jobType": "정규직",
                        "preferredQualifications": "우대사항 없음",
                        "qualifications": "자격 요건 없음",
                        "questions": self.self_intro_questions
                    }

                    job_list.append(job_info)

        return job_list
