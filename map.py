import requests
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from urllib.parse import quote
from geopy.geocoders import Nominatim
from io import BytesIO

# 네이버 API 키 정보
client_id = "l6yznajxjx"
client_secret = "xOheTWLjJViz0sXqo5clhHde8zzZaF3Arw0KmwVU"
API_KEY_ID = "wcxilqd5m6"
API_KEY = "2GyqwdtjghXi0X5IoORFJGr1K7ibP7gvUdQ0OHtB"

def get_coordinates(query, client_id, client_secret):
    encoded_query = quote(query)
    url = f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={encoded_query}"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if "addresses" in data and len(data["addresses"]) > 0:
            address = data["addresses"][0]
            latitude = address.get("y")
            longitude = address.get("x")
            return latitude, longitude
        else:
            print(f"{query}에 대한 좌표를 찾을 수 없습니다.")
            return None
    else:
        print(f"오류 발생({query}):", response.status_code)
        return None

def get_nearest_road(lat, lng):
    geolocator = Nominatim(user_agent="road_locator")
    location = geolocator.reverse((lat, lng), exactly_one=True)
    if location:
        return location.latitude, location.longitude
    else:
        print("도로 근처 위치를 찾을 수 없습니다.")
        return None

# 선택된 음식점의 상세 정보와 지도에 경로 표시
def show_restaurant_details_with_map(celebrity_name, restaurant_name, start_coords):
    # 음식점 상세 정보 가져오기
    details = next((r for r in restaurant_details[celebrity_name] if r['name'] == restaurant_name), None)
    if details:
        st.subheader(f"{details['name']}의 상세 정보")
        st.write(f"음식점 이름: {details['name']}")
        st.write(f"거리: {details['distance']}")
        st.write(f"영업시간: {details['hours']}")
        st.write(f"메뉴: {details['menu']}")
        
        # 도착지 좌표 계산
        goal_coords = get_nearest_road(float(details["distance"].split()[0]), float(details["distance"].split()[1]))
        
        if goal_coords:
            url = f"https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving?start={start_coords[1]},{start_coords[0]}&goal={goal_coords[1]},{goal_coords[0]}"
            headers = {
                "x-ncp-apigw-api-key-id": API_KEY_ID,
                "x-ncp-apigw-api-key": API_KEY
            }
            
            # 길찾기 경로 요청
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                # 지도 생성
                m = folium.Map(location=[start_coords[0], start_coords[1]], zoom_start=12)
                
                # 출발지 마커 추가
                folium.Marker(
                    location=start_coords,
                    popup="출발지",
                    tooltip="출발지",
                    icon=folium.Icon(color="green")
                ).add_to(m)

                # 도착지 마커 추가
                folium.Marker(
                    location=goal_coords,
                    popup=details['name'],
                    tooltip="도착지",
                    icon=folium.Icon(color="red")
                ).add_to(m)

                # 경로 시각화
                try:
                    route = data['route']['traoptimal'][0]['path']
                    path_coords = [(lat, lng) for lng, lat in route]
                    folium.PolyLine(
                        locations=path_coords,
                        color="blue",
                        weight=5,
                        opacity=0.7,
                        tooltip="경로"
                    ).add_to(m)

                    # 전체 경로가 보이도록 줌 설정
                    m.fit_bounds(path_coords)

                except KeyError:
                    st.write("경로 데이터가 없습니다.")

                # 지도 HTML 렌더링
                folium_static(m)
            else:
                st.write("경로 요청 중 오류 발생:", response.status_code)

# Streamlit UI
st.title("연예인 방문 맛집 경로 탐색")

# 예시 데이터: Streamlit 예제에서는 '지디', '배용준' 등과 같은 특정 유명인의 데이터만 사용할 수 있습니다.
# celebrity_name으로 지정된 유명인 목록과 각 맛집 데이터를 아래와 같이 사용할 수 있습니다.
