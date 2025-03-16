from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import QuestionRequest
from agent import process_question
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
    """
    Endpoint để xử lý câu hỏi sử dụng Gemini API
    """
    try:
        if not question or not question.question:
            print("Error: Empty question received")
            return {"answer": "Vui lòng nhập câu hỏi của bạn."}
            
        # Gọi hàm process_question từ agent.py
        response = process_question(question.question)
        
        if not response:
            print("Error: Empty response from Gemini")
            return {"answer": "Xin lỗi, không thể xử lý câu hỏi này. Vui lòng thử lại với câu hỏi khác."}
            
        return {"answer": response}
        
    except Exception as e:
        import traceback
        print(f"Unexpected error processing question: {str(e)}\n{traceback.format_exc()}")
        return {"answer": "Xin lỗi, đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau."}

@app.get("/")
async def root():
    return {"message": "Welcome to Question Answering API with Gemini. Use /ask endpoint to ask questions about the data."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
