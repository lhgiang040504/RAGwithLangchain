import os
import logging
# Logger để ghi lỗi
logger = logging.getLogger(__name__)

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["LANGCHAIN_API_KEY"] = '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'
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"
os.environ["GROQ_API_KEY"] = "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"

from fastapi import FastAPI, File, UploadFile, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from base.llm_model import get_hf_chatbot_llm, get_gsk_parse_llm
from rag.main import build_rag_chatbot_chain, build_rag_parser_chain, InputQA, OutputQA

from db.models import Candidate
from rag.utils import load_pdf, remove_non_utf8_characters


llm_chatbot = get_hf_chatbot_llm(model_name='mistralai/Mistral-7B-Instruct-v0.2', temperature=0.9)
llm_parser = get_gsk_parse_llm(model_name='llama-3.1-70b-versatile')
genai_docs = "../data_source/generative_ai"

#genai_chain = build_rag_chatbot_chain(llm_chatbot, data_dir=genai_docs, data_type='pdf', workers_for_load=12)
parser_candidate_chain = build_rag_parser_chain(llm_parser, Candidate)


# App - FastAPI
app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using LangChain's Runnable interfaces"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Routes - FastAPI
@app.get("/check")
async def check():
    return {"status": "ok"}

@app.post("/generative_ai", response_model=OutputQA)
async def generative_ai(inputs: InputQA):
    answer = llm_chatbot.invoke(inputs.question)
    return {"answer": answer}


@app.post("/parser_candidate", response_model=dict)
async def parser_candidate(request: Request, file: UploadFile = File(...)):
    # Kiểm tra loại file
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "success": False,
                "message": "No file uploaded"
            }
        )
    if file.content_type != "application/pdf":
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "success": False,
                "message": "Invalid file type"
            }
        )

    # Lưu file (xử lý tên file an toàn)
    safe_filename = os.path.basename(file.filename)
    file_location = f"./data/CVs/{safe_filename}"
    try:
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to save file"
            }
        )

    # Đọc nội dung file CVs
    try:
        CVs_content = load_pdf(file_location)
    except Exception as e:
        logger.error(f"Failed to read PDF: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to read PDF"
            }
        )

    # Trích xuất thông tin CVs
    try:
        output = parser_candidate_chain.invoke(input={"cv_content": CVs_content})
        print('Success')
    except Exception as e:
        logger.error(f"Failed to extract CV information: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to extract CV information"
            }
        )
    
    # Trả về kết quả thành công
    return JSONResponse(
        status_code=200,
        content={
            "status": 200,
            "success": True,
            "message": "CV information extracted successfully",
            "data": output
        }
    )
