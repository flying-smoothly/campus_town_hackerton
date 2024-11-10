from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions, QueryOptions  # couchbase.options에서 QueryOptions 가져오기
import json

# Capella 클러스터에 연결하는 함수
def connect_to_couchbase():
    try:
        cluster = Cluster(
            "couchbases://cb.ox0y9-2jlicdby7v.cloud.couchbase.com",  # 정확한 클러스터 엔드포인트 URL 입력
            ClusterOptions(
                PasswordAuthenticator("Access", "Hsh1357900!")  # 클러스터 Access 이름과 패스워드
            )
        )
        bucket = cluster.bucket("restaurant_data")  # 사용 중인 버킷 이름
        print("Capella 클러스터에 연결 성공")
        return cluster
    except Exception as e:
        print(f"Error connecting to Couchbase Capella: {e}")
        return None

# Lambda 함수
def lambda_handler(event, context):
    cluster = connect_to_couchbase()
    if cluster is None:
        return {
            'statusCode': 500,
            'body': json.dumps("Couchbase Capella에 연결 실패")
        }

    menu = event.get('menu')
    if menu:
        query = """
        SELECT name, address, rating, reviews 
        FROM `restaurant_data` 
        WHERE ANY item IN menu_items SATISFIES item = $menu END;
        """
        options = QueryOptions(named_parameters={"menu": menu})
        try:
            row = cluster.query(query, options)
            matching_restaurants = [result for result in row]
            return {
                'statusCode': 200,
                'body': json.dumps(matching_restaurants, ensure_ascii=False)
            }
        except Exception as e:
            print(f"Error executing query: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps("쿼리 실행 중 오류 발생")
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps("잘못된 요청: 'menu'를 지정하세요")
        }

# 테스트용 코드 (Lambda와 동일한 방식으로 호출)
if __name__ == "__main__":
    event = {"menu": "족발"}  # 테스트할 메뉴
    context = None
    response = lambda_handler(event, context)
    print("Lambda response:", response)

