from firebase_config import db

def save_job_posting(job_data):
    job_posts_ref = db.collection("job_posts")

    # ✅ 중복 체크: 동일한 URL이 존재하면 저장하지 않음
    job_query = job_posts_ref.where("URL", "==", job_data["URL"]).stream()
    
    if any(job_query):
        print(f"⚠️ 중복된 공고: {job_data['job']} - 저장 생략")
        return

    job_posts_ref.add(job_data)
    print(f"✅ Firestore에 저장 완료: {job_data['job']} - {job_data['company']}")
