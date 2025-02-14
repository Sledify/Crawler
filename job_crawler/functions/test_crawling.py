import requests
from bs4 import BeautifulSoup

# 크롤링할 페이지 URL 입력
url = "https://www.saramin.co.kr/zf_user/jobs/relay/view?isMypage=no&rec_idx=49832679&recommend_ids=eJxNj8kRQzEMQqvJXVgL5pxC0n8XUfJnLB%2BfwYBCW4hVnw28%2BA5JgcWPbP1xy4xs1R70cKzGepALtKNSEZnz19qwB%2BFuPEU7rdInSpGmCxlVJ7mzCjEz0nvImDu3ZhW72NYUeYC61H7J64QE7JibiEvt4%2FXbXF%2BnDUDL&view_type=list&gz=1&t_ref_content=grand_fix&t_ref=jobcategory_recruit&t_ref_area=103&relayNonce=3ff945e24b3158057a43&immediately_apply_layer_open=n#seq=0"

# HTTP 요청 보내기
response = requests.get(url)
response.raise_for_status()  # 요청이 실패하면 예외 발생

# BeautifulSoup 객체 생성
soup = BeautifulSoup(response.text, "html.parser")

# 특정 클래스의 div 요소 가져오기
divs = soup.find_all("div", class_="wrap_jv_cont")

# 모든 텍스트 추출
for div in divs:
    print(div.get_text(strip=True))
