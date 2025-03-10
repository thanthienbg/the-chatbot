import json
import re
from utils import custom_llm_api_call
from fuzzywuzzy import fuzz
from underthesea import pos_tag

# Load the JSON data
try:
    with open('../data/buoihoc_full_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading JSON data: {str(e)}")
    data = []
    raise

def preprocess_text(text):
    """Normalize text and extract keywords using POS tagging"""
    if not isinstance(text, str):
        return ""
    # Normalize text
    text = text.lower().strip()
    
    # Use POS tagging to identify important words
    tagged_words = pos_tag(text)
    
    # Filter for nouns (N, Np), verbs (V), and adjectives (A)
    important_words = [word for word, tag in tagged_words 
                      if tag.startswith(('N', 'V', 'A'))]
    
    # Join the important words back together
    return ' '.join(important_words)

def extract_info_from_question(question):
    """Determine what information the question is targeting"""
    question = question.lower()

    # Map question keywords to JSON fields
    field_mapping = {
        "THỜI GIAN": ["khi nào", "thời gian", "ngày", "lúc nào", "hôm"],
        "NỘI DUNG BUỔI HỌC": ["chủ đề", "nội dung", "học về gì", "học gì", "có gì"],
        "LINK XEM LẠI VIDEO + TÀI LIỆU": ["xem lại", "link", "video", "live", "tài liệu"],
        "GHI CHÚ": ["ghi chú", "lưu ý", "nhắc nhở", "note"]
    }

    # Check for date in question
    date_match = re.search(r"\d{1,2}/\d{1,2}", question)

    # Find which fields the question relates to
    matched_fields = [field for field, keywords in field_mapping.items() 
                     if any(word in question for word in keywords)]

    return {
        "date": date_match.group() if date_match else None,
        "fields": matched_fields if matched_fields else list(field_mapping.keys())
    }

def search_relevant_entries(question: str):
    """Find entries relevant to the question using POS tagging and fuzzy matching"""
    # Extract important keywords from question using POS tagging
    processed_question = preprocess_text(question)
    
    # Check for specific date in question
    date_match = re.search(r"\d{1,2}/\d{1,2}(/\d{4})?|\d{4}/\d{1,2}/\d{1,2}", question)
    if date_match:
        date = date_match.group()
        matched_entries = [entry for entry in data if date in entry.get("THỜI GIAN", "")]
    else:
        # Search for content matches using fuzzy matching on processed text
        matched_entries = []
        for entry in data:
            # Process each field with POS tagging
            content = preprocess_text(entry.get("NỘI DUNG BUỔI HỌC", ""))
            link = preprocess_text(entry.get("LINK XEM LẠI VIDEO + TÀI LIỆU", ""))
            note = preprocess_text(entry.get("GHI CHÚ", ""))
            
            # Use fuzzy matching with processed text
            if (fuzz.partial_ratio(processed_question, content) > 70 or
                fuzz.partial_ratio(processed_question, link) > 70 or
                fuzz.partial_ratio(processed_question, note) > 70):
                matched_entries.append(entry)
    
    # If no matches found, return empty list
    if not matched_entries:
        return []
        
    # Extract relevant fields based on question context
    info = extract_info_from_question(question)
    return [{field: entry.get(field, "") for field in info["fields"]} 
            for entry in matched_entries]

def format_entries_info(relevant_entries=None):
    """Format entries information for context"""
    if relevant_entries:
        formatted_entries = ""
        for entry in relevant_entries:
            formatted_entries += "\n".join(f"{field}: {value}" 
                                        for field, value in entry.items())
            formatted_entries += "\n---\n"
        return f"Thông tin liên quan:\n{formatted_entries}"
    
    sample_entries = data[:3]
    fields = list(data[0].keys()) if data else []
    formatted_sample = ""
    for entry in sample_entries:
        formatted_sample += "\n".join(f"{field}: {entry.get(field, '')}" 
                                    for field in fields)
        formatted_sample += "\n---\n"
    return f"Các trường trong dữ liệu: {', '.join(fields)}\nDữ liệu mẫu:\n{formatted_sample}"


def process_question(question: str) -> str:
    """Process a question about the JSON data and return an answer"""
    # Search for relevant data first
    relevant_entries = search_relevant_entries(question)

    # Create a context-aware prompt
    context = format_entries_info(relevant_entries)
    prompt = f"""Dựa trên dữ liệu JSON sau:

        {context}
        
        Vui lòng trả lời câu hỏi này: {question}
        
        Hãy đưa ra câu trả lời rõ ràng và ngắn gọn dựa trên dữ liệu được hiển thị ở trên.
    """

    # Get response from LLM
    response = custom_llm_api_call(prompt)
    if response == "404":
        return context
    return response


# Initialize the JSON processor
csv_processor = {
    'process_question': process_question
}

if __name__ == "__main__":
    # Test the function with a sample input
    test_question = "Buổi học vào ngày 16/07 có link không?"
    try:
        # Use data from the loaded JSON file instead of simulating sample data
        # Use search_relevant_entries and display output
        result = search_relevant_entries(test_question)
        print("Search results:")
        print(result)

        # Test process_question
        response = process_question(test_question)
        print("Process Question Response:")
        print(response)

    except Exception as e:
        print(f"An error occurred during testing: {str(e)}")
