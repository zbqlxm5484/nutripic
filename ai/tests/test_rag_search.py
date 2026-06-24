from app.schemas.rag import RagSearchFilters, RagSearchRequest
from app.services.rag import search_rag


def test_rag_search_returns_ranked_local_documents():
    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["fatigue sleep magnesium"],
            filters=RagSearchFilters(source_types=["idisk", "functional_ingredient"], top_k=3),
        )
    )

    assert len(response.results) >= 2
    assert response.results[0].score >= response.results[1].score
    assert {result.source_type for result in response.results}.issubset(
        {"idisk", "functional_ingredient"}
    )


def test_rag_search_applies_source_type_filter():
    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["omega anticoagulant"],
            filters=RagSearchFilters(source_types=["functional_ingredient"], top_k=5),
        )
    )

    assert response.results
    assert all(result.source_type == "functional_ingredient" for result in response.results)
    assert response.results[0].document_id == "functional_ingredient_omega3"


def test_rag_search_respects_top_k():
    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["fatigue sleep magnesium omega"],
            filters=RagSearchFilters(top_k=1),
        )
    )

    assert len(response.results) == 1


def test_rag_search_returns_empty_results_when_no_document_matches():
    response = search_rag(
        RagSearchRequest(
            request_id="req_test_rag",
            search_queries=["unrelated_query_without_match"],
            filters=RagSearchFilters(top_k=8),
        )
    )

    assert response.results == []
