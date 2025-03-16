import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path('../.env')
load_dotenv(dotenv_path=env_path)

# Configure Gemini API
try:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        # Try to read directly from .env file if environment variable is not set
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_API_KEY='):
                        GOOGLE_API_KEY = line.split('=')[1].strip().strip("'").strip('"')
                        break
    
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in .env file. Please add GOOGLE_API_KEY=your_api_key to .env file")
        
    genai.configure(api_key=GOOGLE_API_KEY)
    print("✅ Đã cấu hình Gemini API thành công")
except Exception as e:
    print(f"❌ Lỗi khi cấu hình Gemini API: {str(e)}")
    raise

def load_json_data():
    """Load JSON data and return as formatted string"""
    try:
        # Read JSON file
        with open('../data/data_normalized.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert JSON to formatted string
        data_str = "Dữ liệu các buổi học:\n\n"
        for idx, lesson in enumerate(data, 1):
            data_str += f"Buổi {idx}:\n"
            for key, value in lesson.items():
                data_str += f"{key}: {value or ''}\n"
            data_str += "---\n"
        
        return data_str
    except Exception as e:
        print(f"❌ Lỗi khi đọc file JSON: {str(e)}")
        return None

def ask_gemini(question: str, data: str) -> str:
    """Ask Gemini AI about the data"""
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash-8b')
        
        # Prepare the prompt with context and question
        prompt = f"""Dựa trên dữ liệu sau đây về các buổi học:
    
            {data}
    
            Hãy trả lời câu hỏi sau một cách chính xác và ngắn gọn: {question}
    
            ### Quy tắc trả lời:
            - **Nếu ngày không hợp lệ** (ví dụ: 30/2, 31/4, hoặc ngày không tồn tại trong lịch), hãy trả lời: **"Buổi học không tồn tại."** 
            - **Nếu ngày hợp lệ nhưng không có dữ liệu**, hãy trả lời: **"Tôi không tìm thấy thông tin về buổi học này trong dữ liệu."**
            - **Nếu không tìm thấy thông tin chính xác**, có thể gợi ý buổi học gần nhất nhưng phải nói rõ: **"Không có dữ liệu cho ngày *ngày được hỏi*, bạn có thể quan tâm buổi học gần nhất vào ngày gần nhất."**
            - **BẮT BUỘC phải kiểm tra thông tin ngày trong câu hỏi.**
            - **Không tự tạo nội dung nếu dữ liệu không có thông tin.**
            - **Câu trả lời phải ngắn gọn, súc tích, dễ hiểu.**
            - **Trả lời bằng tiếng Việt.**
    
            ### Định dạng câu trả lời (nếu có dữ liệu):
            ✅ **Nội dung buổi học**:   
            📌 **Link xem lại**:
            📄 **Tài liệu**: 
            📝 **Ghi chú**: 
    
            Lưu ý: Không suy diễn hoặc bịa đặt thông tin ngoài dữ liệu đã cung cấp.
        """

        response = model.generate_content(prompt)
        
        if response.text:
            return response.text.strip()
        return "Xin lỗi, tôi không thể xử lý câu hỏi này."

    except Exception as e:
        print(f"❌ Lỗi khi gọi Gemini API: {str(e)}")
        return f"Đã xảy ra lỗi khi xử lý câu hỏi: {str(e)}"

def process_question(question: str) -> str:
    """Process a question using Gemini API"""
    # Load JSON data
    data = load_json_data()
    if not data:
        return "Không thể tải dữ liệu JSON."
    
    # Ask Gemini about the data
    response = ask_gemini(question, data)
    return response

def print_json_content():
    """Print all content from JSON file"""
    try:
        # Read JSON file
        with open('../data/data_normalized.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("\n📊 NỘI DUNG FILE JSON:")
        print("="*100)
        
        # Print headers (assuming all objects have the same keys)
        if data and len(data) > 0:
            headers = data[0].keys()
            header_str = " | ".join(f"{h:^20}" for h in headers)
            print(header_str)
            print("-"*len(header_str))
            
            # Print rows
            for lesson in data:
                row_str = " | ".join(f"{str(val or ''):^20}" for val in lesson.values())
                print(row_str)
                print("-"*len(header_str))
        
        print("="*100)
        return True
    except Exception as e:
        print(f"❌ Lỗi khi đọc file JSON: {str(e)}")
        return False

if __name__ == "__main__":
    def run_test(question: str) -> None:
        """Run a single test question and display results"""
        print("\n" + "="*80)
        print(f"📝 Câu hỏi: {question}")
        print("-"*80)
        print("💡 Câu trả lời:")
        response = process_question(question)
        print(response)
        print("="*80)

    # Test cases covering different scenarios
    test_cases = [
        "Buổi học ngày 18/02 học về chủ đề gì?"
    ]
    
    print("\n🔰 BẮT ĐẦU KIỂM TRA HỆ THỐNG HỎI ĐÁP")
    print("Tổng số câu hỏi test:", len(test_cases))
    
    try:
        for i, question in enumerate(test_cases, 1):
            print(f"\n📊 Test #{i}/{len(test_cases)}")
            run_test(question)
                
    except KeyboardInterrupt:
        print("\n\n⚠️ Đã dừng kiểm tra theo yêu cầu người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình kiểm tra: {str(e)}")
    finally:
        print("\n✅ HOÀN THÀNH KIỂM TRA")