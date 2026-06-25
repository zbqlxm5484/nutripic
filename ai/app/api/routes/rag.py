from fastapi import APIRouter, Depends

from app.core.security import verify_internal_api_key
from app.schemas.rag import RagSearchRequest, RagSearchResponse
from app.services.rag import search_rag

router = APIRouter(prefix="/rag", dependencies=[Depends(verify_internal_api_key)])


@router.post("/search/", response_model=RagSearchResponse)
def rag_search(payload: RagSearchRequest):
    return search_rag(payload)