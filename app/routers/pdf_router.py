from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.pdf_service import process_pdf, get_pdf_content, generate_response

router = APIRouter()

@router.post("/v1/pdf", status_code=status.HTTP_201_CREATED)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are allowed."
        )
    try:
        pdf_id = await process_pdf(file)
        return {"pdf_id": pdf_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/v1/chat/{pdf_id}", status_code=status.HTTP_200_OK)
async def chat_with_pdf(pdf_id: str, query: dict):
    message = query.get("message")
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message field is required."
        )
    try:
        pdf_content = get_pdf_content(pdf_id)
        if not pdf_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF not found."
            )

        response = await generate_response(pdf_content, message)
        return {"response": response}
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
