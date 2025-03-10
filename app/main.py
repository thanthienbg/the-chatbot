from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import QuestionRequest
from agent import csv_processor
from agent import search_relevant_entries, format_entries_info
import uvicorn

app = FastAPI(title="Question Answering API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ask")
async def ask_question(question: QuestionRequest):
    try:
        if not question or not question.question:
            print("Error: Empty question received")
            return {"answer": "Vui lòng nhập câu hỏi của bạn."}
            
        response = csv_processor['process_question'](question.question)
        if not response:
            print("Error: Empty response from processor")
            return {"answer": "Xin lỗi, không thể xử lý câu hỏi này. Vui lòng thử lại với câu hỏi khác."}
            
        return {"answer": response}
    except KeyError as e:
        print(f"KeyError in processor: {str(e)}")
        return {"answer": "Xin lỗi, đã xảy ra lỗi trong quá trình xử lý. Vui lòng thử lại sau."}
    except Exception as e:
        import traceback
        print(f"Unexpected error processing question: {str(e)}\n{traceback.format_exc()}")
        return {"answer": "Xin lỗi, đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau."}

@app.post("/ask_without_ai")
async def ask_without_ai(question: QuestionRequest):
    try:
        if not question or not question.question:
            print("Error: Empty question received")
            return {"answer": "Vui lòng nhập câu hỏi của bạn."}

        # Fetch relevant entries using search_relevant_entries
        relevant_entries = search_relevant_entries(question.question)
        if not relevant_entries:
            print("Error: No relevant entries found")
            return {
                "answer": f"Với câu hỏi '{question.question}', chúng tôi không tìm thấy thông tin phù hợp. Vui lòng thử lại với câu hỏi khác."}

        # Format the retrieved entries for response
        response = format_entries_info(relevant_entries)
        return {"answer": f"Với câu hỏi '{question.question}', chúng tôi có câu trả lời: {response}"}
    except Exception as e:
        import traceback
        print(f"Unexpected error processing question without AI: {str(e)}\n{traceback.format_exc()}")
        return {"answer": "Xin lỗi, đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau."}



@app.get("/")
async def root():
    return {"message": "Welcome to CSV Question Answering API. Use /ask endpoint to ask questions about the CSV data."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
