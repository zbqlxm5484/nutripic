from app.schemas.rag import RagSearchRequest, RagSearchResponse, RagSearchResult

FIXTURE_DOCUMENTS = [
    RagSearchResult(
        document_id="functional_ingredient_magnesium",
        source_type="functional_ingredient",
        source_name="건강기능식품 기능성원료 인정현황",
        title="마그네슘",
        content="마그네슘은 정상적인 근육 기능 유지에 필요한 기능성 원료입니다. 일일섭취량과 섭취 시 주의사항을 확인해야 합니다.",
        score=0.91,
        metadata={
            "ingredient_name_ko": "마그네슘",
            "ingredient_name_en": "Magnesium",
            "normalized_name": "magnesium",
            "daily_dosage": "기능성원료 인정현황의 일일섭취량 범위를 따르세요.",
            "expected_effects": ["정상적인 근육 기능 유지"],
            "side_effects": ["설사", "복부 불편감"],
            "precautions": ["신장 질환이 있는 경우 전문가와 상담하세요."],
        },
    ),
    RagSearchResult(
        document_id="idisk_sleep_fatigue_magnesium",
        source_type="idisk",
        source_name="iDISK 증상/성분 데이터",
        title="피로와 수면 관련 성분 후보",
        content="피로와 수면 관리 맥락에서 마그네슘이 관련 성분 후보로 검색될 수 있습니다.",
        score=0.84,
        metadata={
            "symptoms": ["fatigue", "sleep"],
            "related_ingredients": ["magnesium"],
        },
    ),
]


def search_rag(payload: RagSearchRequest) -> RagSearchResponse:
    source_types = set(payload.filters.source_types or [])
    top_k = payload.filters.top_k

    query_text = " ".join(payload.search_queries).lower()
    results = []

    for document in FIXTURE_DOCUMENTS:
        if source_types and document.source_type not in source_types:
            continue

        if is_related(query_text, document):
            results.append(document)

    if not results:
        results = FIXTURE_DOCUMENTS[:1]

    return RagSearchResponse(results=results[:top_k])


def is_related(query_text: str, document: RagSearchResult) -> bool:
    searchable_text = " ".join(
        [
            document.title,
            document.content,
            document.metadata.get("ingredient_name_en", ""),
            document.metadata.get("normalized_name", ""),
            " ".join(document.metadata.get("symptoms", [])),
            " ".join(document.metadata.get("related_ingredients", [])),
        ]
    ).lower()

    query_terms = query_text.replace("_", " ").split()

    return any(term in searchable_text for term in query_terms)