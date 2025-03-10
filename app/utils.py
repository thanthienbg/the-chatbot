import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API endpoint and payload for custom LLM
VLLM_API_URL = "https://13b4-103-140-39-129.ngrok-free.app/v1/chat/completions"
payload = {
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "messages": [],
    "temperature": 0.5
}


def custom_llm_api_call(prompt):
    try:
        payload["messages"] = [{"role": "user", "content": prompt}]
        response = requests.post(VLLM_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("choices", [{}])[0].get("message", {}).get("content", "Xin lỗi, tôi không thể trả lời câu hỏi này.")
    except requests.exceptions.RequestException as e:
        print(f"API request error: {str(e)}")
        return "Xin lỗi, hiện tại tôi không thể kết nối với máy chủ. Vui lòng thử lại sau."
    except (KeyError, ValueError, TypeError) as e:
        print(f"Response parsing error: {str(e)}")
        return "Xin lỗi, đã xảy ra lỗi khi xử lý câu trả lời. Vui lòng thử lại."


# Adapter function for direct Q&A
class LLMService:
    def __init__(self, temperature=0.7):
        self.temperature = temperature

    def ask_question(self, question):
        return custom_llm_api_call(question)


# Initialize the LLM service
llm_service = LLMService(temperature=0.5)