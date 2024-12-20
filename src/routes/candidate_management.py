import os
import logging
# Logger để ghi lỗi
logger = logging.getLogger(__name__)

from fastapi import APIRouter, File, UploadFile, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from db.models import Candidate
from db.schemas import list_serial

from base.llm_model import get_gsk_parse_llm
from rag.main import build_rag_parser_chain
from .utils import load_pdf

import uuid
from bson import ObjectId


candidate_management_router = APIRouter()

@candidate_management_router.get("/getAll_candidates")
async def getAll_candidates(request: Request):
    try:
        database = request.app.mongodb.get_database()
        candidates_collection = database["Candidates"]
        candidates = candidates_collection.find()

        return JSONResponse(
            status_code=200,
            content={
                "status": 200,
                "success": True,
                "message": "Candidates retrieved successfully",
                "data": list_serial(candidates)
            }
        )
    except Exception as e:
        logger.error(f"Failed to retrieve candidates: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to retrieve candidates"
            }
        )

@candidate_management_router.post("/parser_candidate", response_model=dict)
async def parser_candidate(request: Request, file: UploadFile = File(...)):
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
    if file.content_type != "application/pdf":
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
    file_location = f"../file_upload/CVs/{safe_filename}"
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

    # Extract information
    try:
        llm_parser = get_gsk_parse_llm(model_name='llama-3.1-70b-versatile')
        parser_candidate_chain = build_rag_parser_chain(llm_parser, Candidate)

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
    
    # Store into mongo database
    try:
        if "_id" not in output or not output["_id"]:
            output["_id"] = str(uuid.uuid4())  # initial id

        database = request.app.mongodb.get_database()
        collection = database["Candidates"]

        insert_result = collection.insert_one(dict(output))

        # Retrieve the document using the returned _id
        inserted_id = insert_result.inserted_id
        retrieved_doc = collection.find_one({"_id": inserted_id})
    except Exception as e:
        logger.error(f"Failed to save candidate: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to save candidate"
            }
        )
    # Return success flat
    return JSONResponse(
        status_code=200,
        content={
            "status": 200,
            "success": True,
            "message": "CV information extracted successfully",
            "data": retrieved_doc
        }
    )
   
@candidate_management_router.put("/{candidate_id}")
async def update_candidate(request: Request, candidate_id: str, update_data: Candidate):
    try:
        # Access database
        database = request.app.mongodb.get_database()  # Replace with the actual database name
        candidates_collection = database["Candidates"]

        # Check if the candidate exists and update
        candidate = candidates_collection.find_one({"_id": candidate_id})
        if not candidate:
            return JSONResponse(
                status_code=404,
                content={
                    "status": 404,
                    "success": False,
                    "message": "Candidate not found"
                }
            )
        
        # Prepare update data by filtering out None values (to avoid updating fields with None)
        update_data_dict = {k: v for k, v in update_data.dict().items()}

        # Perform the update
        updated_candidate = candidates_collection.find_one_and_update(
            {"_id": candidate_id},
            {"$set": update_data_dict},
            return_document=True  # This returns the updated document
        )

        return JSONResponse(
            status_code=200,
            content={
                "status": 200,
                "success": True,
                "message": "Candidate updated successfully",
                "data": updated_candidate
            }
        )


    except Exception as e:
        logger.error(f"Failed to update candidate: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to update candidate"
            }
        )

@candidate_management_router.delete("/{candidate_id}")
async def delete_candidate(request: Request, candidate_id: str):
    try:
        # Access database
        database = request.app.mongodb.get_database()  
        candidates_collection = database["Candidates"]

        # Check cadidate exist
        candidate = candidates_collection.find_one({"_id": candidate_id})
        if not candidate:
            return JSONResponse(
                status_code=404,
                content={
                    "status": 404,
                    "success": False,
                    "message": "Candidate not found"
                }
            )

        # Delete candidate
        result = candidates_collection.delete_one({"_id": candidate_id})
        if result.deleted_count == 1:
            return JSONResponse(
                status_code=200,
                content={
                    "status": 200,
                    "success": True,
                    "message": "Candidate deleted successfully"
                }
            )
        else:
            raise Exception("Failed to delete candidate")

    except Exception as e:
        logger.error(f"Failed to delete candidate: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "success": False,
                "message": "Failed to delete candidate"
            }
        )
