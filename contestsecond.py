import json
import boto3

# AWS Bedrock 및 Rekognition 클라이언트 설정
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
rekognition = boto3.client('rekognition', region_name='us-east-1')

# Claude 모델과 AWS Bedrock의 Messages API를 사용하여 상호작용하는 함수
def analyze_with_bedrock(prompt, max_tokens=1000):
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',  # Claude 모델 ID
            body=json.dumps({
                "messages": messages,
                "max_tokens": max_tokens,
                "anthropic_version": "bedrock-2023-05-31"
            }),
            contentType="application/json"
        )
        result = json.loads(response['body'].read().decode('utf-8'))
        
        # 응답 내용 디버깅을 위한 전체 출력
        # print("Full response:", result)
        
        # content에서 텍스트 추출 후 JSON 형식으로 파싱
        if 'content' in result and isinstance(result['content'], list) and len(result['content']) > 0:
            response_text = result['content'][0]['text']
            try:
                # 텍스트를 JSON으로 파싱
                parsed_response = json.loads(response_text)
                return parsed_response
            except json.JSONDecodeError:
                print("Error: Failed to parse response text as JSON.")
                return response_text  # JSON 형식이 아닐 경우 원문 반환
        else:
            print("Error: 'content' key not found or empty in the response.")
            return "Error: No content in response."
    
    except Exception as e:
        print("An error occurred while calling the Bedrock model:", e)
        return "Error: Exception occurred."

# 리뷰 텍스트를 Claude 모델에 전달하여 메뉴 정보 추출
def extract_menu_items_from_reviews(reviews):
    menu_items = []
    for review in reviews:
        review_text = review.get('text', '')
        prompt = f"""
        다음 리뷰에서 언급된 메뉴 항목을 추출해 주세요. 결과는 'menu_items' 리스트로 반환해 주세요:
        \"{review_text}\"
        """
        response = analyze_with_bedrock(prompt)
        
        # JSON 형식일 경우 menu_items를 추출
        if isinstance(response, dict) and 'menu_items' in response:
            menu_items.extend(response['menu_items'])
        else:
            print("Non-JSON response:", response)
    
    # 중복 제거 후 반환
    return list(set(menu_items))

# 전체 식당 정보를 분석하여 'menu_items' 필드 추가
def analyze_restaurants_with_menu(restaurants):
    analyzed_data = []
    for restaurant in restaurants:
        name = restaurant.get('name', '이름 정보 없음')
        address = restaurant.get('address', '주소 정보 없음')
        rating = restaurant.get('rating', '평점 정보 없음')
        reviews = restaurant.get('reviews', [])
        
        # 리뷰에서 메뉴 항목 추출
        menu_items = extract_menu_items_from_reviews(reviews)
        
        # 분석된 식당 정보 저장
        restaurant_info = {
            'name': name,
            'address': address,
            'rating': rating,
            'menu_items': menu_items,
            'reviews': reviews
        }
        analyzed_data.append(restaurant_info)

    # JSON 파일로 저장
    with open('analyzed_restaurant_data_with_menu.json', 'w', encoding='utf-8') as f:
        json.dump(analyzed_data, f, ensure_ascii=False, indent=2)

    print("분석된 식당 정보가 'analyzed_restaurant_data_with_menu.json' 파일에 저장되었습니다.")

# JSON 파일에서 식당 데이터를 불러와 분석
with open('restaurant_data.json', 'r', encoding='utf-8') as f:
    restaurants_data = json.load(f)

analyze_restaurants_with_menu(restaurants_data)