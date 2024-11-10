import streamlit as st
import pandas as pd

# 엑셀 파일에서 데이터 읽기
file_path_celebrity_list = '/home/ec2-user/environment/chat_al/pages/xx.xlsx'
file_path_key = '/home/ec2-user/environment/chat_al/pages/키.xlsx'

# 두 파일의 데이터프레임으로 읽기
celebrity_data = pd.read_excel(file_path_celebrity_list)
key_data = pd.read_excel(file_path_key)

# 데이터 준비
restaurant_data = {
    "규현": celebrity_data[['name', 'restaurant']].rename(columns={'restaurant': 'show'}).to_dict(orient='records'),
    "키": key_data[['연예인', '매장이름']].rename(columns={'연예인': 'name', '매장이름': 'show'}).to_dict(orient='records')
}

restaurant_details = {
    "규현": [
        {
            "name": row['restaurant'],
            "distance": "정보 없음",  # 실제 거리 데이터는 필요에 따라 추가
            "map_image": "",  # 지도 이미지 URL 추가
            "hours": "정보 없음",  # 영업시간 추가
            "menu": "정보 없음"  # 메뉴 정보 추가
        } for _, row in celebrity_data.iterrows()
    ],
    "키": [
        {
            "name": row['매장이름'],
            "distance": "정보 없음",  # 실제 거리 데이터는 필요에 따라 추가
            "map_image": "",  # 지도 이미지 URL 추가
            "hours": "정보 없음",  # 영업시간 추가
            "menu": "정보 없음"  # 메뉴 정보 추가
        } for _, row in key_data.iterrows()
    ]
}

# 뒤로 가기 버튼
if st.button("간다. 뒤로", type="primary"):
    st.session_state.current_page = "final2"
    st.experimental_rerun()  # 페이지를 새로 고침하여 변경된 상태 반영

# 각 음식점의 상세 정보
def show_restaurant_details(celebrity_name, index):
    details = restaurant_details[celebrity_name][index]

    st.subheader(f"{details['name']}의 상세 정보")
    st.write(f"음식점 이름: {details['name']}")
    st.write(f"거리: {details['distance']}")
    st.write(f"영업시간: {details['hours']}")
    st.write(f"메뉴: {details['menu']}")
    if details['map_image']:
        st.image(details['map_image'], caption="지도 사진", use_column_width=True)

# 선택된 연예인 이름을 가져옴
celebrity_name = st.session_state["selected_celeb"] 
st.header(f"{celebrity_name}의 추천 음식점 리스트")

# 음식점 리스트 출력
for restaurant in restaurant_data[celebrity_name]:
    st.write(f"매장명: {restaurant['name']} - 방송 이름: {restaurant['show']}")

# 매장명 입력
selected_restaurant_name = st.text_input("음식점 이름을 입력하세요:")

if st.button("상세 정보 보기"):
    if selected_restaurant_name in [restaurant['name'] for restaurant in restaurant_data[celebrity_name]]:
        index = next(i for i, restaurant in enumerate(restaurant_data[celebrity_name]) if restaurant['name'] == selected_restaurant_name)
        show_restaurant_details(celebrity_name, index)        
    else:
        st.warning("올바른 음식점 이름을 입력하세요.")
