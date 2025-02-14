import firebase_admin
from firebase_admin import credentials, firestore

# ✅ Firebase 인증 정보 설정
cred = credentials.Certificate("serviceAccountKey.json")  # 다운로드한 JSON 키 파일 경로
firebase_admin.initialize_app(cred)

# ✅ Firestore 클라이언트 생성
db = firestore.client()
