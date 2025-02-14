import requests
from bs4 import BeautifulSoup
from datetime import datetime
from save_to_firestore import save_job_posting

# ✅ 크롤링할 URL 및 헤더 설정
BASE_URL = "https://www.saramin.co.kr"
JOB_LIST_URL = f"{BASE_URL}/zf_user/jobs/list/job-category?page=1&cat_kewd=403"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ✅ 하드코딩된 자기소개서 문항 리스트
SELF_INTRO_QUESTIONS = [
    "1. 이 부문에 지원한 동기를 기술해 주십시오.",
    "2. 이 직무와 관련된 경험을 본인의 역할과 성과 중심으로 기술해 주십시오.",
    "3. 나와 대다수의 의견이 다른 경우, 본인이 대처했던 경험과 그로부터 얻은 교훈을 기술해 주십시오."
]

def extract_job_details(job_url):
    """각 채용 공고 상세 페이지에서 추가 정보 크롤링"""
    response = requests.get(job_url, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ 상세 페이지 요청 실패: {response.status_code}")
        return {
            "jobDescription": "포지션 상세 없음",
            "jobType": "정규직",
            "preferredQualifications": "우대사항 없음",
            "qualifications": "자격 요건 없음",
            "deadline": "마감일 정보 없음"
        }

    soup = BeautifulSoup(response.text, "html.parser")

    # ✅ 공고 카드에서 직접 정보 추출
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

    # ✅ 상세 설명 (iframe 크롤링)
    job_description = "포지션 상세 없음"
    iframe_element = soup.select_one("iframe.recruit_detail_iframe")
    
    if iframe_element:
        iframe_src = iframe_element.get("data-src") or iframe_element.get("src")
        if iframe_src:
            iframe_url = f"{BASE_URL}{iframe_src}"
            iframe_response = requests.get(iframe_url, headers=HEADERS)
            if iframe_response.status_code == 200:
                iframe_soup = BeautifulSoup(iframe_response.text, "html.parser")
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

def crawl_job_list():
    """1차 크롤링: 채용 리스트 페이지에서 URL 수집"""
    print("🔍 채용 리스트 크롤링 시작...")
    response = requests.get(JOB_LIST_URL, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ 리스트 페이지 요청 실패: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    job_elements = soup.select(".list_item")

    job_list = []
    
    for job in job_elements[:10]:  # 최대 10개 크롤링 (확장 가능)
        title_element = job.select_one(".job_tit a")
        company_element = job.select_one(".company_nm a")
        link_element = title_element["href"] if title_element else None

        if company_element and link_element:
            job_url = f"{BASE_URL}{link_element}"
            print(f"📌 상세 페이지 크롤링 시작: {job_url}")

            # 2차 크롤링: 상세 페이지 크롤링
            job_details = extract_job_details(job_url)

            job_info = {
                "URL": job_url,
                "company": company_element.get_text(strip=True),
                "createdAt": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "deadline": job_details["deadline"],
                "id": None,
                "isApplied": False,
                "job": job_details["job"],
                "jobDescription": job_details["jobDescription"],
                "jobType": job_details["jobType"],
                "preferredQualifications": job_details["preferredQualifications"],
                "qualifications": job_details["qualifications"],
                "questions": SELF_INTRO_QUESTIONS
            }
            job_list.append(job_info)

    return job_list

if __name__ == "__main__":
    jobs = crawl_job_list()
    
    if jobs:
        print(f"📂 Firestore 저장 시작 (총 {len(jobs)}개 공고)")
        for job in jobs:
            print("🔎 크롤링된 데이터:", job)  # 크롤링 데이터 확인
            save_job_posting(job)
