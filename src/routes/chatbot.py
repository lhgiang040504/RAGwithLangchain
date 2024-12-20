import os
import logging
# Logger để ghi lỗi
logger = logging.getLogger(__name__)

from fastapi import APIRouter

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from base.llm_model import get_hf_chatbot_llm
from rag.main import build_rag_chatbot_chain, InputQA, OutputQA

llm_chatbot = get_hf_chatbot_llm(model_name='mistralai/Mistral-7B-Instruct-v0.2', temperature=0.9)
genai_docs = "../data_source/generative_ai"
genai_chain = build_rag_chatbot_chain(llm_chatbot, data_dir=genai_docs, data_type='pdf', workers_for_load=12)

chatbot_router = APIRouter()

@chatbot_router.post("/generative_ai", response_model=OutputQA)
async def generative_ai(inputs: InputQA):
    answer = llm_chatbot.invoke(inputs.question)
    return {"answer": answer}