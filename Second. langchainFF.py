import json
import boto3
from langchain import ChatBedrock

# AWS 클라이언트 설정
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
rekognition = boto3.client('rekognition', region_name='us-east-1')

# LangChain Claude 모델 설정
model_kwargs = {
    'temperature': 0.7,
    'max_tokens': 1000,
    'top_p': 0.9,
    'frequency_penalty': 0,
    'presence_penalty': 0,
}
llm = ChatBedrock(
    client=bedrock_runtime,
    model_id='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
    model_kwargs=model_kwargs,
    streaming=True
)

# AWS Rekognition과 Claude 모델을 함께 사용하여 이미지 분석
def analyze_image(image_url):
    # Rekognition을 통해 이미지 레이블 분석
    rekognition_response = rekognition.detect_labels(
        Image={'Bytes': image_url},
        MaxLabels=10,
        MinConfidence=80
    )
    labels = [label['Name'] for label in rekognition_response['Labels']]
    
    # Claude 모델에 레이블을 전달하여 자연스러운 JSON 형식 생성
    prompt = f"""
    Given the following labels from an image: {labels}
    Interpret these labels and provide a JSON output that reflects the scene, objects, ambiance, or any other notable features observed. Avoid using predefined fields; instead, reflect the content naturally.
    """
    
    response = llm.chat(
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    return response['choices'][0]['message']['content']

# Claude 모델을 사용하여 리뷰 텍스트 분석
def analyze_review(review_text):
    prompt = f"""
    Analyze the following review text and extract relevant insights as JSON. Avoid using specific predefined fields; instead, reflect the user's comments naturally:
    \"{review_text}\"
    """
    response = llm.chat(
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response['choices'][0]['message']['content']

# 분석 수행
def analyze_restaurants(restaurants):
    analyzed_data = []
    for restaurant in restaurants:
        place_id = restaurant['place_id']
        name = restaurant['name']
        address = restaurant.get('vicinity', '주소 정보 없음')
        rating = restaurant.get('rating', '평점 정보 없음')
        photo_reference = restaurant.get('photos', [{}])[0].get('photo_reference', None)
        image_url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key=YOUR_GOOGLE_API_KEY' if photo_reference else None

        # 이미지 분석
        if image_url:
            image_analysis = analyze_image(image_url)
        else:
            image_analysis = '이미지 없음'

        # 리뷰 텍스트 분석
        reviews = restaurant.get('reviews', [])
        review_analysis = []
        for review in reviews:
            review_text = review.get('text', '')
            analysis = analyze_review(review_text)
            review_analysis.append({
                'review_text': review_text,
                'analysis': analysis
            })

        # JSON 형식으로 정보 저장
        restaurant_info = {
            'name': name,
            'address': address,
            'rating': rating,
            'image_analysis': image_analysis,
            'review_analysis': review_analysis
        }
        analyzed_data.append(restaurant_info)

    # JSON 형식으로 출력
    print(json.dumps(analyzed_data, ensure_ascii=False, indent=2))

# Step 1에서 얻은 JSON 데이터를 불러와 분석
with open('restaurants.json', 'r', encoding='utf-8') as f:
    restaurants_data = json.load(f)

analyze_restaurants(restaurants_data)
