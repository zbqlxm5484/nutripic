from fastapi import APIRouter, Depends

from app.core.security import verify_internal_api_key
from app.schemas.guardrails import (
    InputGuardrailRequest,
    InputGuardrailResponse,
    OutputGuardrailRequest,
    OutputGuardrailResponse,
)
from app.services.guardrails import check_input_guardrail, check_output_guardrail

router = APIRouter(prefix="/guardrails", dependencies=[Depends(verify_internal_api_key)])


@router.post("/input/", response_model=InputGuardrailResponse)
def input_guardrail(payload: InputGuardrailRequest):
    return check_input_guardrail(payload)


@router.post("/output/", response_model=OutputGuardrailResponse)
def output_guardrail(payload: OutputGuardrailRequest):
    return check_output_guardrail(payload)