import json
import streamlit as st
import boto3
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.llms import BedrockLLM
import lambda_function_to_final_streamlit as lambda_fn

# AWS Rekognition 및 Bedrock 설정
rekognition_client = boto3.client('rekognition', region_name='us-east-1')
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

# LangChain 및 Claude 모델 설정
class BedrockLLM:
    def __init__(self, client, model_id, model_kwargs):
        self.client = client
        self.model_id = model_id
        self.model_kwargs = model_kwargs

    def __call__(self, prompt):
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.model_kwargs['max_tokens'],
            "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
        })

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body
        )
        response_body = json.loads(response.get("body").read())
        return response_body["content"][0]["text"]

llm = BedrockLLM(client=bedrock_runtime, model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0", model_kwargs={'max_tokens': 1000})
memory = ConversationBufferMemory()
chat_chain = ConversationChain(llm=llm, memory=memory, prompt=ChatPromptTemplate.from_template("{history}\nUser: {input}\nAssistant:"))

# Streamlit 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("Restaurant Recommendation Chatbot")

# Display previous messages
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input and condition extraction
user_input = st.chat_input("Ask me about nearby restaurants...")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state["messages"].append({'role': 'user', 'content': user_input})

    # Claude 모델로 사용자 조건 추출
    extraction_prompt = f"""
    Analyze the user's requirements from the following sentence:
    \"{user_input}\"
    Provide the requirements in a JSON format, capturing any relevant details the user might mention. These details might include:
    - Specific preferences or constraints related to food, budget, dining style, ambiance, distance, or any other aspect.
    - Avoid using predefined field names. Instead, extract the details naturally as described by the user.
    - If certain details are not mentioned, exclude them from the JSON response.
    """
    extracted_conditions = chat_chain.run(input=extraction_prompt)

    # JSON으로 파싱된 조건을 사용하여 Lambda 함수 호출
    try:
        conditions = json.loads(extracted_conditions)
        response = lambda_fn.lambda_handler(conditions, None)
        
        if response['statusCode'] == 200:
            recommendations = json.loads(response['body'])
            
            # Show restaurant recommendations
            recommendation_text = "Here are some nearby options:\n\n"
            for place in recommendations:
                recommendation_text += f"- {place['name']} (Rating: {place.get('rating', 'N/A')})\n  Address: {place.get('address', 'Address not available')}\n"
            
            st.chat_message("assistant").write(recommendation_text)
            st.session_state["messages"].append({'role': 'assistant', 'content': recommendation_text})
        
        else:
            st.error("Unable to find any matching restaurants. Please try with different criteria.")

    except json.JSONDecodeError:
        st.error("Failed to interpret the response. Please try again.")
