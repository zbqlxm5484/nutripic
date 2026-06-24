from fastapi import APIRouter, Depends

from app.core.security import verify_internal_api_key
from app.schemas.reports import ReportGenerateRequest, ReportGenerateResponse
from app.services.report_generator import generate_report

router = APIRouter(prefix="/reports", dependencies=[Depends(verify_internal_api_key)])


@router.post("/generate/", response_model=ReportGenerateResponse)
def report_generate(payload: ReportGenerateRequest):
    return generate_report(payload)