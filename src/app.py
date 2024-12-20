import os
import logging
# Logger để ghi lỗi
logger = logging.getLogger(__name__) 
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from routes.candidate_management import candidate_management_router
from routes.job_management import job_management_router
#from routes.chatbot import chatbot_router

from db.db_connection import MongoDB

from dotenv import dotenv_values
config = dotenv_values("../.env")

os.environ["LANGCHAIN_API_KEY"] = config["LANGCHAIN_API_KEY"]
os.environ["HUGGINGFACEHUB_API_TOKEN"] = config["HUGGINGFACEHUB_API_TOKEN"]
os.environ["GROQ_API_KEY"] = config["GROQ_API_KEY"]

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
@app.get("/")
async def check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_db_client():
    app.mongodb = MongoDB(uri=config['MONGODB_URI'], db_name=config['MONGODB_DB'])
    await app.mongodb.init()  # Initialize the MongoDB connection
    print("Connected to MongoDB database!")

@app.on_event("shutdown")
async def shutdown_db_client():
    await app.mongodb.close()  # Close the MongoDB connection
    print("Disconnected from MongoDB database!")

app.include_router(candidate_management_router, prefix="/candidates", tags=["candidates"])
app.include_router(job_management_router, prefix="/jobs", tags=["jobs"])

#app.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])