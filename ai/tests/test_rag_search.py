import os

os.environ.setdefault("AI_INTERNAL_API_KEY", "test_internal_key")

from app.schemas.rag import RagSearchFilters, RagSearchRequest
from app.schemas.rag import RagSearchResult
from app.services import rag
from app.services.rag import search_rag
from app.services import rag_vector_store
from app.services.rag_vector_store import RagVectorStoreUnavailable


def build_test_vector_document(document_id, metadata):
    text = "shared supplement evidence"
    return {
        "document_id": document_id,
        "source_type": "idisk",
        "source_name": "iDISK",
        "title": document_id,
        "content": text,
        "metadata": metadata,
        "terms": rag_vector_store.tokenize(text),
        "embedding": rag_vector_store.embed_text(text),
    }


def test_rag_search_returns_ranked_local_documents():
    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["5-HTP serotonin"],
            filters=RagSearchFilters(source_types=["idisk", "functional_ingredient"], top_k=3),
        )
    )

    assert len(response.results) >= 2
    assert response.results[0].score >= response.results[1].score
    assert {result.source_type for result in response.results}.issubset(
        {"idisk", "functional_ingredient"}
    )


def test_rag_search_accepts_missing_query_bundle():
    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["5-HTP serotonin"],
            filters=RagSearchFilters(source_types=["idisk"], top_k=1),
        )
    )

    assert len(response.results) == 1


def test_rag_search_boosts_idisk_condition_ids(monkeypatch):
    documents = (
        build_test_vector_document("doc_unmatched_condition", {"disease_id": "DIS_OTHER"}),
        build_test_vector_document("doc_matched_condition", {"disease_id": "DIS_MATCH"}),
    )
    monkeypatch.setattr(rag_vector_store, "load_vector_documents", lambda: documents)

    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["shared supplement"],
            rag_query_bundle={"idisk": {"condition_ids": ["DIS_MATCH"]}},
            filters=RagSearchFilters(source_types=["idisk"], top_k=2),
        )
    )

    assert response.results[0].document_id == "doc_matched_condition"


def test_rag_search_boosts_idisk_drug_ids(monkeypatch):
    documents = (
        build_test_vector_document("doc_unmatched_drug", {"target_id": "D_OTHER"}),
        build_test_vector_document("doc_matched_drug", {"target_id": "D_MATCH"}),
    )
    monkeypatch.setattr(rag_vector_store, "load_vector_documents", lambda: documents)

    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["shared supplement"],
            rag_query_bundle={"idisk": {"drug_ids": ["D_MATCH"]}},
            filters=RagSearchFilters(source_types=["idisk"], top_k=2),
        )
    )

    assert response.results[0].document_id == "doc_matched_drug"


def test_rag_search_boosts_idisk_ingredient_ids(monkeypatch):
    documents = (
        build_test_vector_document("doc_unmatched_ingredient", {"dsi_id": "DSI_OTHER"}),
        build_test_vector_document("doc_matched_ingredient", {"dsi_id": "DSI_MATCH"}),
    )
    monkeypatch.setattr(rag_vector_store, "load_vector_documents", lambda: documents)

    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["shared supplement"],
            rag_query_bundle={"idisk": {"ingredient_ids": ["DSI_MATCH"]}},
            filters=RagSearchFilters(source_types=["idisk"], top_k=2),
        )
    )

    assert response.results[0].document_id == "doc_matched_ingredient"


def test_rag_search_applies_source_type_filter():
    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["functional ingredient"],
            filters=RagSearchFilters(source_types=["functional_ingredient"], top_k=5),
        )
    )

    assert response.results
    assert all(result.source_type == "functional_ingredient" for result in response.results)


def test_rag_search_finds_functional_ingredient_by_korean_claims():
    cases = [
        ("마그네슘 에너지 신경 근육", "마그네슘"),
        ("홍삼 면역 피로 혈액흐름", "홍삼"),
        ("루테인 눈 건강", "루테인"),
    ]

    for query, expected_title in cases:
        response = search_rag(
            RagSearchRequest(
                request_id="req_test_rag",
                search_queries=[query],
                filters=RagSearchFilters(source_types=["functional_ingredient"], top_k=3),
            )
        )

        assert response.results
        assert any(expected_title in result.title for result in response.results)


def test_rag_search_accepts_official_mfds_functional_category():
    response = search_rag(
        RagSearchRequest(
            request_id="req_test_immunity_mfds_category",
            search_queries=["immune support 면역 기능 개선 supplements"],
            rag_query_bundle={"mfds": {"functional_categories": ["면역 기능 개선"]}},
            filters=RagSearchFilters(source_types=["idisk", "functional_ingredient"], top_k=8),
        )
    )

    assert response.results
    assert response.needs_clarification is False
    assert response.low_rag_score is False
    assert response.results[0].source_type == "functional_ingredient"
    assert response.results[0].score >= rag.RAG_MIN_SCORE


def test_rag_search_accepts_added_health_goal_categories():
    cases = [
        ("body fat 체지방 감소 supplements", "체지방 감소"),
        ("bone health 관절 뼈 건강 supplements", "관절 / 뼈 건강"),
        ("blood sugar 혈당 조절 supplements", "혈당 조절"),
    ]

    for query, category in cases:
        response = search_rag(
            RagSearchRequest(
                request_id="req_test_added_mfds_category",
                search_queries=[query],
                rag_query_bundle={"mfds": {"functional_categories": [category]}},
                filters=RagSearchFilters(source_types=["idisk", "functional_ingredient"], top_k=8),
            )
        )

        assert response.results
        assert response.needs_clarification is False
        assert response.low_rag_score is False
        assert response.results[0].source_type == "functional_ingredient"
        assert response.results[0].score >= rag.RAG_MIN_SCORE


def test_rag_search_can_filter_supplement_evidence_reference_documents():
    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["aloe vera harmful digestive aid"],
            filters=RagSearchFilters(source_types=["supplement_evidence"], top_k=3),
        )
    )

    assert response.results
    assert all(result.source_type == "supplement_evidence" for result in response.results)

    result = response.results[0]
    assert result.metadata["supplement_name"] == "aloe vera"
    assert result.metadata["evidence_score"] == 0
    assert result.metadata["is_harmful"] is True
    assert result.metadata["usage_policy"] == "risk_and_evidence_reference_only"


def test_rag_search_respects_top_k():
    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["magnesium calcium serotonin"],
            filters=RagSearchFilters(top_k=1),
        )
    )

    assert len(response.results) == 1


def test_rag_search_returns_empty_results_when_no_document_matches():
    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["zzzznomatchtoken"],
            filters=RagSearchFilters(top_k=8),
        )
    )

    assert response.results == []


def test_rag_search_raises_service_unavailable_when_vector_store_fails(monkeypatch):
    def raise_store_unavailable(**kwargs):
        raise RagVectorStoreUnavailable()

    monkeypatch.setattr(rag, "search_vector_index", raise_store_unavailable)

    try:
        search_rag(
            RagSearchRequest(
                request_id="req_test_rag",
                search_queries=["magnesium"],
                filters=RagSearchFilters(top_k=1),
            )
        )
    except Exception as exc:
        assert exc.status_code == 503
        assert exc.error_code == "rag_service_unavailable"
        assert exc.message == "RAG 검색 인덱스를 사용할 수 없습니다."
        assert exc.request_id == "req_test_rag"
    else:
        raise AssertionError("Expected rag_service_unavailable error")


def test_rag_search_uses_chroma_backend_when_configured(monkeypatch):
    def fake_chroma_search(**kwargs):
        return [
            RagSearchResult(
                document_id="doc_chroma_test",
                source_type="functional_ingredient",
                source_name="test",
                title="chroma result",
                content="from chroma",
                score=0.9,
                metadata={},
            )
        ]

    monkeypatch.setattr(rag.settings, "rag_vector_backend", "chroma")
    monkeypatch.setattr(rag, "search_chroma_index", fake_chroma_search)

    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["magnesium"],
            filters=RagSearchFilters(top_k=1),
        )
    )

    assert response.results[0].document_id == "doc_chroma_test"
