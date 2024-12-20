import os
import logging
# Logger để ghi lỗi
logger = logging.getLogger(__name__)

from fastapi import APIRouter, File, UploadFile, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from db.models import Candidate, Job
from db.schemas import list_serial

from base.llm_model import get_gsk_parse_llm
from rag.main import build_rag_parser_chain
from .utils import load_pdf, load_txt

import uuid
from bson import ObjectId


job_management_router = APIRouter()

@job_management_router.get("/getAll_jobs")
async def getAll_jobs(request: Request):
    try:
        database = request.app.mongodb.get_database()
        jobs_collection = database["Jobs"]
        jobs = jobs_collection.find()

        return JSONResponse(
            status_code=200,
            content={
                "status": 200,
                "success": True,
                "message": "Jobs retrieved successfully",
                "data": list_serial(jobs)
            }
        )
    except Exception as e:
        logger.error(f"Failed to retrieve jobs: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to retrieve jobs"
            }
        )

@job_management_router.post("/parser_job", response_model=dict)
async def parser_jobs(request: Request, file: UploadFile = File(...)):
    # Make sense input file
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "success": False,
                "message": "No file uploaded"
            }
        )
    if file.content_type != "text/plain":
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "success": False,
                "message": "Invalid file type"
            }
        )

    # Save file (safe file name)
    safe_filename = os.path.basename(file.filename)
    file_location = f"../file_upload/JDs/{safe_filename}"
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

    # Read file
    try:
        JDs_content = load_txt(file_location)
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

    # Extract information
    try:
        llm_parser = get_gsk_parse_llm(model_name='llama-3.1-70b-versatile')
        parser_job_chain = build_rag_parser_chain(llm_parser, Job)

        output = parser_job_chain.invoke(input={"cv_content": JDs_content})
        print('Success')
    except Exception as e:
        logger.error(f"Failed to extract JD information: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to extract JD information"
            }
        )
    
    # Store into mongo database
    try:
        if "_id" not in output or not output["_id"]:
            output["_id"] = str(uuid.uuid4())  # initial id

        database = request.app.mongodb.get_database()
        collection = database["Jobs"]

        insert_result = collection.insert_one(dict(output))

        # Retrieve the document using the returned _id
        inserted_id = insert_result.inserted_id
        retrieved_doc = collection.find_one({"_id": inserted_id})
    except Exception as e:
        logger.error(f"Failed to save job: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to save job"
            }
        )
    # Return success flat
    return JSONResponse(
        status_code=200,
        content={
            "status": 200,
            "success": True,
            "message": "JD information extracted successfully",
            "data": retrieved_doc
        }
    )
   
@job_management_router.put("/{job_id}")
async def update_job(request: Request, job_id: str, update_data: Job):
    try:
        # Access database
        database = request.app.mongodb.get_database()  # Replace with the actual database name
        jobs_collection = database["Jobs"]

        # Check if the jobs exists and update
        job = jobs_collection.find_one({"_id": job_id})
        if not job:
            return JSONResponse(
                status_code=404,
                content={
                    "status": 404,
                    "success": False,
                    "message": "Job not found"
                }
            )
        
        # Prepare update data by filtering out None values (to avoid updating fields with None)
        update_data_dict = {k: v for k, v in update_data.dict().items()}

        # Perform the update
        updated_job = jobs_collection.find_one_and_update(
            {"_id": job_id},
            {"$set": update_data_dict},
            return_document=True  # This returns the updated document
        )

        return JSONResponse(
            status_code=200,
            content={
                "status": 200,
                "success": True,
                "message": "Job updated successfully",
                "data": updated_job
            }
        )


    except Exception as e:
        logger.error(f"Failed to update job: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to update job"
            }
        )

@job_management_router.delete("/{job_id}")
async def delete_job(request: Request, job_id: str):
    try:
        # Access database
        database = request.app.mongodb.get_database() 
        jobs_collection = database["Jobs"]

        # Check job exist
        job = jobs_collection.find_one({"_id": job_id})
        if not job:
            return JSONResponse(
                status_code=404,
                content={
                    "status": 404,
                    "success": False,
                    "message": "Job not found"
                }
            )

        # Delete job
        result = jobs_collection.delete_one({"_id": job_id})
        if result.deleted_count == 1:
            return JSONResponse(
                status_code=200,
                content={
                    "status": 200,
                    "success": True,
                    "message": "Job deleted successfully"
                }
            )
        else:
            raise Exception("Failed to delete job")

    except Exception as e:
        logger.error(f"Failed to delete job: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to delete job"
            }
        )
