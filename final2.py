import streamlit as st

if "selected_celeb" not in st.session_state:
    st.session_state["selected_celeb"] = None


# Streamlit UI 구성
st.title("연예인이 방문한 음식점 추천")
celebrity_name = st.text_input("연예인의 이름을 입력하세요:")

if st.button("추천 음식점 리스트 생성"):
    if celebrity_name not in ["규현", "키"]:
        st.warning("올바른 이름을 입력하세요.")
    else:
        st.session_state["selected_celeb"] = celebrity_name
        st.switch_page("pages/choose_restaurant.py")
        # splay_restaurant_list(celebrity_name)
