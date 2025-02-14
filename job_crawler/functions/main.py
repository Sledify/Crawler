import concurrent.futures
from crawlers.saramin_crawler import SaraminCrawler
from crawlers.campuspick_crawler import CampickCrawler
from crawlers.jobkorea_crawler import JobKoreaCrawler
from save_to_firestore import save_job_posting

def run_crawler(crawler):
    """각 크롤러를 실행하고 크롤링된 데이터 저장"""
    print(f"🚀 {crawler.__class__.__name__} 크롤링 시작...")
    jobs = crawler.crawl_jobs()

    if jobs:
        print(f"📂 Firestore 저장 시작 (총 {len(jobs)}개 공고)")
        for job in jobs:
            print(f"🔎 크롤링된 데이터: {job['job']} at {job['company']}")
            save_job_posting(job)
    else:
        print(f"❌ {crawler.__class__.__name__}에서 크롤링된 공고 없음")

if __name__ == "__main__":
    print("✨ 여러 채용 사이트에서 크롤링을 동시에 실행합니다...")

    # ✅ 크롤러 리스트 (필요 시 추가 가능)
    crawlers = [
        SaraminCrawler(),
        CampickCrawler(),
        JobKoreaCrawler(),
    ]

    # ✅ 병렬 처리하여 여러 크롤러 실행
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(run_crawler, crawlers)

    print("✅ 모든 크롤링 작업이 완료되었습니다!")
