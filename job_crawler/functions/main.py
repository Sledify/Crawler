import requests
from bs4 import BeautifulSoup

# ✅ 크롤링할 URL (사람인 - 개발자 채용 공고 페이지)
URL = "https://www.saramin.co.kr/zf_user/jobs/list/job-category?page=1&cat_kewd=403"

# ✅ 요청 헤더 설정 (필요한 경우 User-Agent 추가)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def crawl_jobs():
    print("🔍 채용 정보 크롤링 시작...")
    
    response = requests.get(URL, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ 요청 실패: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, "html.parser")

    # ✅ 채용 공고 리스트 찾기
    job_elements = soup.select(".list_item")  # 해당 사이트에 맞는 클래스 선택

    job_list = []
    
    for job in job_elements[:10]:  # 상위 10개만 크롤링
        title_element = job.select_one(".job_tit a")  # 채용 제목
        company_element = job.select_one(".company_nm a")  # 회사 이름
        link_element = title_element["href"] if title_element else None

        if title_element and company_element and link_element:
            job_info = {
                "title": title_element.get_text(strip=True),
                "company": company_element.get_text(strip=True),
                "link": f"https://www.saramin.co.kr{link_element}"
            }
            job_list.append(job_info)

    # ✅ 크롤링 결과 출력
    print("\n📌 채용 공고 목록:")
    for idx, job in enumerate(job_list, 1):
        print(f"{idx}. {job['title']} - {job['company']}")
        print(f"   🔗 링크: {job['link']}\n")

if __name__ == "__main__":
    crawl_jobs()
