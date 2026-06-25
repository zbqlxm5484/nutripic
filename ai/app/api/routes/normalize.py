from fastapi import APIRouter, Depends

from app.core.security import verify_internal_api_key
from app.schemas.normalize import NormalizeRequest, NormalizeResponse
from app.services.normalize import normalize

router = APIRouter(dependencies=[Depends(verify_internal_api_key)])


@router.post("/normalize/", response_model=NormalizeResponse)
def normalize_input(payload: NormalizeRequest):
    return normalize(payload)