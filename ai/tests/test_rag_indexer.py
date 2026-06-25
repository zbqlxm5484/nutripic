import os

os.environ.setdefault("AI_INTERNAL_API_KEY", "test_internal_key")

from app.services.rag_indexer import (
    build_functional_ingredient_documents,
    build_idisk_interaction_documents,
    build_idisk_disease_documents,
    build_idisk_side_effect_documents,
    build_rag_documents,
    build_supplement_evidence_documents,
)
from app.services.rag_vector_store import build_vector_index


def test_build_idisk_interaction_documents():
    documents = build_idisk_interaction_documents()

    assert documents
    document = documents[0]

    assert document["document_id"].startswith("idisk_interaction_")
    assert document["source_type"] == "idisk"
    assert document["source_name"] == "iDISK"
    assert document["title"].startswith("iDISK interaction:")
    assert "5-htp" in document["title"]
    assert "Antidepressants" in document["title"]
    assert document["content"]
    assert "Supplement ingredient ID:" in document["content"]
    assert "Supplement ingredient name: 5-htp." in document["content"]
    assert "Target type: drug_or_target." in document["content"]
    assert "Target label: Antidepressants." in document["content"]
    assert "Evidence source:" in document["content"]
    assert document["metadata"]["dataset"] == "dsi_d"
    assert document["metadata"]["dsi_id"]
    assert document["metadata"]["dsi_name"] == "5-htp"
    assert document["metadata"]["target_id"]
    assert document["metadata"]["target_type"] == "drug_or_target"
    assert document["metadata"]["target_label"] == "Antidepressants"
    assert "5-HTP" in document["metadata"]["dsi_common_names"]
    assert "Antidepressants/anxiolytics (tricyclics, MAOIs, and SSRIs)" in document["metadata"]["target_aliases"]
    assert document["metadata"]["relation_label"] == "interacts with"


def test_build_idisk_disease_documents():
    documents = build_idisk_disease_documents()

    assert documents
    document = documents[0]

    assert document["document_id"].startswith("idisk_disease_")
    assert document["source_type"] == "idisk"
    assert document["title"].startswith("iDISK effectiveness:")
    assert "5-htp" in document["title"]
    assert "Anxiety" in document["title"]
    assert "Target type: disease_or_condition." in document["content"]
    assert "Target label: Anxiety." in document["content"]
    assert document["metadata"]["dataset"] == "dsi_dis"
    assert document["metadata"]["dsi_id"]
    assert document["metadata"]["dsi_name"] == "5-htp"
    assert document["metadata"]["disease_id"]
    assert document["metadata"]["target_type"] == "disease_or_condition"
    assert document["metadata"]["target_label"] == "Anxiety"
    assert document["metadata"]["relation_label"] == "is effective for"


def test_build_idisk_side_effect_documents():
    documents = build_idisk_side_effect_documents()

    assert documents
    document = documents[0]

    assert document["document_id"].startswith("idisk_side_effect_")
    assert document["source_type"] == "idisk"
    assert document["title"].startswith("iDISK adverse reaction:")
    assert "5-htp" in document["title"]
    assert "Mania" in document["title"]
    assert "Target type: side_effect." in document["content"]
    assert "Target label: Mania." in document["content"]
    assert document["metadata"]["dataset"] == "dsi_ss"
    assert document["metadata"]["dsi_id"]
    assert document["metadata"]["dsi_name"] == "5-htp"
    assert document["metadata"]["side_effect_id"]
    assert document["metadata"]["target_type"] == "side_effect"
    assert document["metadata"]["target_label"] == "Mania"
    assert "manic episode" in document["metadata"]["target_aliases"]
    assert document["metadata"]["relation_label"] == "has adverse reaction"


def test_build_functional_ingredient_documents_uses_korean_ingredient_title():
    documents = build_functional_ingredient_documents()

    assert documents
    assert not any(document["title"] == "기 능 성" for document in documents)

    magnesium = next(
        document for document in documents if document["title"] == "마그네슘"
    )

    assert magnesium["source_type"] == "functional_ingredient"
    assert magnesium["metadata"]["ingredient_name_ko"] == "마그네슘"
    assert magnesium["metadata"]["normalized_name"] == "마그네슘"
    assert magnesium["metadata"]["daily_dosage_structured"] == {
        "raw": "94.5~250 mg",
        "min_value": 94.5,
        "max_value": 250.0,
        "unit": "mg",
    }
    assert magnesium["metadata"]["precaution_tags"] == []
    assert "원료명: 마그네슘" in magnesium["content"]
    assert "기능성 내용:" in magnesium["content"]
    assert "일일섭취량:" in magnesium["content"]
    assert "구조화된 일일섭취량: 94.5~250 mg" in magnesium["content"]
    assert "에너지 이용에 필요" in magnesium["content"]

    red_ginseng = next(
        document for document in documents if document["title"] == "홍삼"
    )

    assert red_ginseng["metadata"]["daily_dosage_structured"]["min_value"] == 3.0
    assert red_ginseng["metadata"]["daily_dosage_structured"]["max_value"] == 80.0
    assert red_ginseng["metadata"]["daily_dosage_structured"]["unit"] == "mg"
    assert red_ginseng["metadata"]["precaution_tags"] == ["medication_caution"]


def test_build_supplement_evidence_documents_marks_reference_only_risk_data():
    documents = build_supplement_evidence_documents()

    assert len(documents) == 192

    aloe = next(
        document
        for document in documents
        if document["metadata"]["supplement_name"] == "aloe vera"
        and document["metadata"]["condition"] == "digestive aid"
    )

    assert aloe["source_type"] == "supplement_evidence"
    assert aloe["source_name"] == "SnakeOil supplement evidence score"
    assert aloe["metadata"]["evidence_score"] == 0
    assert aloe["metadata"]["evidence_label"] == "harmful"
    assert aloe["metadata"]["is_harmful"] is True
    assert aloe["metadata"]["usage_policy"] == "risk_and_evidence_reference_only"
    assert "not a recommendation candidate source" in aloe["content"]
    assert aloe["metadata"]["source_links"]


def test_build_rag_documents_returns_unique_document_ids():
    documents = build_rag_documents()
    document_ids = [document["document_id"] for document in documents]

    assert documents
    assert len(document_ids) == len(set(document_ids))


def test_build_vector_index_adds_embeddings_and_terms():
    documents = build_rag_documents()
    index = build_vector_index(documents[:3])
    document = index["documents"][0]

    assert index["schema_version"] == 1
    assert index["embedding_model"] == "local-hashed-token-v1"
    assert index["embedding_dimension"] == 512
    assert document["document_id"]
    assert document["embedding"]
    assert document["terms"]
