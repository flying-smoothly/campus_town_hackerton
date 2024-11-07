import requests
import json

# Google Places API 키
API_KEY = 'YOUR_GOOGLE_API_KEY'

# 1. 특정 지역의 식당 검색
def search_restaurants(location, radius=600, keyword='restaurant'):  # 숙명여자대학교에서 숙대입구역까지의 거리 약 600m
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': location,  # 위도,경도 형식으로 예: '37.5665,126.9780' (서울 중심)
        'radius': radius,      # 반경 (미터 단위)
        'type': 'restaurant',  # 검색 타입 (식당)
        'keyword': keyword,    # 키워드 (예: 'restaurant')
        'key': API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    restaurants = data.get('results', [])
    
    return [restaurant['place_id'] for restaurant in restaurants]

# 2. 식당의 상세 정보 및 리뷰 가져오기
def get_restaurant_details(place_id):
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'place_id': place_id,
        'fields': 'name,rating,reviews,formatted_address,opening_hours,types,photos',
        'key': API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    result = data.get('result', {})

    # JSON 형식으로 세부 정보를 반환
    restaurant_info = {
        'name': result.get('name'),
        'rating': result.get('rating'),
        'address': result.get('formatted_address'),
        'opening_hours': result.get('opening_hours', {}).get('weekday_text', []),
        'types': result.get('types', []),
        'reviews': [],
        'photo_url': None
    }

    # 리뷰 추가
    reviews = result.get('reviews', [])
    for review in reviews:
        restaurant_info['reviews'].append({
            'author_name': review.get('author_name'),
            'rating': review.get('rating'),
            'text': review.get('text'),
            'relative_time_description': review.get('relative_time_description')
        })

    # 첫 번째 이미지 URL 추가
    if 'photos' in result:
        photo_ref = result['photos'][0].get('photo_reference')
        if photo_ref:
            restaurant_info['photo_url'] = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={API_KEY}"

    return restaurant_info

# 3. 특정 위치에 있는 식당 리뷰 및 상세 정보 수집 및 JSON 저장
def collect_and_save_restaurant_data(location):
    # 위치 내의 모든 식당 ID 가져오기
    restaurant_ids = search_restaurants(location)

    # 각 식당의 상세 정보 및 리뷰 수집
    restaurant_details_list = []
    for place_id in restaurant_ids:
        details = get_restaurant_details(place_id)
        restaurant_details_list.append(details)

    # JSON 파일로 저장
    with open('restaurant_data.json', 'w', encoding='utf-8') as f:
        json.dump(restaurant_details_list, f, ensure_ascii=False, indent=2)

    print("모든 식당의 세부 정보가 'restaurant_data.json' 파일에 저장되었습니다.")

# 숙명여자대학교 위치 (위도, 경도) 및 반경 설정
location = '37.5454,126.9643'  # 숙명여자대학교
collect_and_save_restaurant_data(location)
