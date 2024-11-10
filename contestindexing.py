from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import json

# Capella 클러스터 연결 설정
def connect_to_capella():
    try:
        cluster = Cluster(
            "couchbases://cb.ox0y9-2jlicdby7v.cloud.couchbase.com",  # Capella 클러스터의 엔드포인트 URL
            ClusterOptions(
                PasswordAuthenticator("Access", "Hsh1357900!")  # Cluster Access Name과 Password
            )
        )
        # 타임아웃 설정 (필요 시, 버킷에서 설정)
        bucket = cluster.bucket("restaurant_data")
        collection = bucket.default_collection()
        print("Capella 클러스터에 연결 성공")
        return collection
    except Exception as e:
        print(f"Error connecting to Couchbase Capella: {e}")
        return None  # 연결 실패 시 None 반환

# 연결 테스트
if __name__ == "__main__":
    connect_to_capella()

def create_restaurant_index():
    # JSON 파일 로드 확인
    print("Loading data from JSON file...")
    try:
        with open("/home/ec2-user/environment/chat_al/pages/restaurant_data.json", "r", encoding="utf-8") as json_file:
            reviews_data = json.load(json_file)
        print(f"Loaded {len(reviews_data)} records from JSON file.")
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return  # 파일 읽기 실패 시 함수 종료

    # Capella 연결 확인
    collection = connect_to_capella()
    if collection is None:
        print("Failed to connect to Couchbase Capella.")
        return

    # Couchbase에 데이터를 문서로 추가
    for review in reviews_data:
        try:
            document_key = review['name']  # 식당 이름을 키로 사용
            document_value = {
                "name": review['name'],
                "address": review.get('address', 'N/A'),
                "menu": review.get('menu', []),
                "review_text": review.get('review_text', '')
            }
            collection.upsert(document_key, document_value)
            print(f"Added document for restaurant: {document_key}")
        except Exception as e:
            print(f"Error adding document for {document_key}: {e}")
            continue

    print("모든 데이터를 Couchbase Capella에 성공적으로 업로드했습니다.")

if __name__ == "__main__":
    create_restaurant_index()
