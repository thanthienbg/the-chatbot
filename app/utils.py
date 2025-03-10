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
        if not VLLM_API_URL:
            print("Error: VLLM_API_URL is not configured")
            return "Xin lỗi, hệ thống chưa được cấu hình đúng. Vui lòng liên hệ quản trị viên."

        payload["messages"] = [{"role": "user", "content": prompt}]
        
        try:
            response = requests.post(VLLM_API_URL, json=payload, timeout=30)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            print(f"Timeout error connecting to {VLLM_API_URL}")
            return "Xin lỗi, máy chủ đang phản hồi chậm. Vui lòng thử lại sau ít phút."
        except requests.exceptions.ConnectionError:
            print(f"Connection error to {VLLM_API_URL}")
            return "Xin lỗi, không thể kết nối với máy chủ. Vui lòng kiểm tra kết nối mạng và thử lại."
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {str(e)}")
            return "Xin lỗi, đã xảy ra lỗi khi giao tiếp với máy chủ. Vui lòng thử lại sau."
        
        try:
            response_data = response.json()
        except ValueError as e:
            print(f"Invalid JSON response: {str(e)}\nResponse content: {response.text}")
            return "Xin lỗi, máy chủ trả về dữ liệu không hợp lệ. Vui lòng thử lại."

        if not response_data.get("choices"):
            print(f"No choices in response. Full response: {response_data}")
            return "Xin lỗi, máy chủ không trả về câu trả lời hợp lệ. Vui lòng thử lại."

        return response_data.get("choices", [{}])[0].get("message", {}).get("content", "Xin lỗi, tôi không thể trả lời câu hỏi này.")

    except Exception as e:
        print(f"Unexpected error in custom_llm_api_call: {str(e)}")
        return "Xin lỗi, đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau."


# Adapter function for direct Q&A
class LLMService:
    def __init__(self, temperature=0.7):
        self.temperature = temperature

    def ask_question(self, question):
        return custom_llm_api_call(question)


# Initialize the LLM service
llm_service = LLMService(temperature=0.5)