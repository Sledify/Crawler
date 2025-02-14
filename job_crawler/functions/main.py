import requests
from bs4 import BeautifulSoup
from datetime import datetime
from save_to_firestore import save_job_posting

# ✅ 크롤링할 URL 및 헤더 설정
URL = "https://www.saramin.co.kr/zf_user/jobs/list/job-category?page=1&cat_kewd=403"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ✅ 하드코딩된 자기소개서 문항 리스트
SELF_INTRO_QUESTIONS = [
    "1. 이 부문에 지원한 동기를 기술해 주십시오.",
    "2. 이 직무와 관련된 경험을 본인의 역할과 성과 중심으로 기술해 주십시오.",
    "3. 나와 대다수의 의견이 다른 경우, 본인이 대처했던 경험과 그로부터 얻은 교훈을 기술해 주십시오."
]

def crawl_jobs():
    print("🔍 크롤링 시작...")
    response = requests.get(URL, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ 요청 실패: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    job_elements = soup.select(".list_item")

    job_list = []
    
    for job in job_elements[:10]:  
        title_element = job.select_one(".job_tit a")
        company_element = job.select_one(".company_nm a")
        link_element = title_element["href"] if title_element else None

        if title_element and company_element and link_element:
            job_info = {
                "URL": f"https://www.saramin.co.kr{link_element}",  # ✅ 기존 'link' → 'URL'로 변경
                "company": company_element.get_text(strip=True),
                "createdAt": datetime.utcnow(),  # ✅ 현재 시간 저장 (UTC 기준)
                "deadline": None,  # ✅ 마감일 정보 없음 (필요 시 추가 크롤링)
                "id": None,  # ✅ Firestore에서 자동 생성
                "isApplied": False,  # ✅ 기본값 False
                "job": title_element.get_text(strip=True),  # ✅ 기존 'title' → 'job'로 변경
                "jobDescription": "포지션 상세 없음",  # ✅ 기본 값 설정 (추후 크롤링 가능)
                "jobType": "정규직",  # ✅ 기본 값 설정 (필요 시 크롤링)
                "preferredQualifications": "우대사항 없음",  # ✅ 기본 값 설정 (필요 시 크롤링)
                "qualifications": "자격 요건 없음",  # ✅ 기본 값 설정 (필요 시 크롤링)
                "questions": SELF_INTRO_QUESTIONS  # ✅ 자기소개서 문항 추가
            }
            job_list.append(job_info)

    return job_list

if __name__ == "__main__":
    jobs = crawl_jobs()
    
    if jobs:
        print(f"📂 Firestore 저장 시작 (총 {len(jobs)}개 공고)")
        for job in jobs:
            print("🔎 크롤링된 데이터:", job)  # 크롤링 데이터 확인
            save_job_posting(job)
