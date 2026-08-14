import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from pydantic import BaseModel
import shutil
import tempfile
import uuid
from pathlib import Path
from documents_processor.file_handler import DocumentProcessor
from retriever.builder import RetrieverBuilder
from agents.workflow import AgentWorkflow
from sessions import sessions
from config import constants
from utils.logging import logger
from fastapi.middleware.cors import CORSMiddleware

#lets initiate the classes
processor = DocumentProcessor()
retriever_builder = RetrieverBuilder()
workflow = AgentWorkflow()

#api endpoint check
app = FastAPI(
    title="DocChat API",
    version="1.0.0",
    openapi_version="3.0.3"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://docchat560.netlify.app/",
        "https://docchat560.netlify.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    session_id: str
    question: str


@app.get("/")
async def root():
    return {
        "message": "DocChat API is running!"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }

#upload file endpoint
@app.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(
            status_code=400,
            detail="No documents were uploaded."
        )

    temporary_files = []

    try:
        # Create temporary files for DocumentProcessor
        for uploaded_file in files:

            # Check extension
            extension = Path(uploaded_file.filename).suffix.lower()

            if extension not in constants.ALLOWED_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {extension}"
                )

            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=extension
            )

            # Copy uploaded contents into temporary file
            shutil.copyfileobj(
                uploaded_file.file,
                temp_file
            )

            temp_file.close()

            temporary_files.append(temp_file)

        logger.info(
            f"Received {len(temporary_files)} document(s)"
        )

        # Process documents using your existing processor
        chunks = processor.process(temporary_files)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No usable content could be extracted from the documents."
            )

        logger.info(
            f"Created {len(chunks)} document chunks"
        )

        # Build your existing hybrid retriever
        retriever = retriever_builder.build_hybrid_retriever(
            chunks
        )

        # Create a unique session
        session_id = str(uuid.uuid4())

        # Store retriever for future questions
        sessions[session_id] = {
            "retriever": retriever,
            "file_count": len(files)
        }

        logger.info(
            f"Created session: {session_id}"
        )

        return {
            "session_id": session_id,
            "file_count": len(files),
            "chunk_count": len(chunks),
            "message": "Documents uploaded and processed successfully."
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Upload processing error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process documents: {str(e)}"
        )

    finally:
        # Remove temporary files
        for temp_file in temporary_files:
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass

#query endpoint
@app.post("/ask")
async def ask_question(request: QuestionRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    session = sessions.get(request.session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please upload your documents again."
        )

    retriever = session["retriever"]

    try:
        logger.info(f"Question: {request.question}")
        logger.info(f"Retriever: {type(retriever)}")

        result = workflow.full_pipeline(
            question=request.question,
            retriever=retriever
        )

        logger.info(f"Workflow result: {result}")

        return {
            "answer": result["draft_answer"],
            "verification": result["verification_report"]
        }

    except Exception as e:
        logger.error(
            f"Question processing error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )