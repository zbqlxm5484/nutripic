import uuid
from urllib.parse import urlparse

from rest_framework import status
from rest_framework.exceptions import APIException

from .ai_client import AIClientError, AIServiceUnavailableError, get_ai_client
from .models import IHERB_ALLOWED_DOMAINS, IngredientLinkMapping


class AIServerException(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'AI 서버 호출에 실패했습니다.'
    default_code = 'ai_server_error'

    def __init__(self, ai_status_code=None, ai_payload=None, ai_path=None):
        detail = {
            'message': self.default_detail,
            'ai_status_code': ai_status_code,
            'ai_path': ai_path,
            'ai_error': ai_payload or {},
        }
        super().__init__(detail=detail)


class AIServiceUnavailableException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'AI 서비스를 일시적으로 사용할 수 없습니다.'
    default_code = 'service_unavailable'


def generate_report(request_data, user=None):
    request_id = create_request_id()
    client = get_ai_client()

    input_guardrail = call_ai(
        client.input_guardrail,
        {
            'request_id': request_id,
            'user_id': get_user_id(user),
            'task_type': 'report_generation',
            'input_text': build_input_text(request_data),
            'structured_input': {
                'health_goals': [item['code'] for item in request_data['health_goals']],
                'medications': [item['code'] for item in request_data.get('medications', [])],
                'special_conditions': [
                    item['code'] for item in request_data.get('special_conditions', [])
                ],
            },
        },
    )
    clarification = build_clarification_response(input_guardrail)
    if clarification:
        return clarification

    normalize_response = call_ai(
        client.normalize,
        {
            'request_id': request_id,
            'age': request_data['age'],
            'gender': request_data['gender'],
            'health_goals': request_data['health_goals'],
            'medications': request_data.get('medications', []),
            'special_conditions': request_data.get('special_conditions', []),
            'additional_notes': request_data.get('additional_notes') or '',
        },
    )
    clarification = build_clarification_response(normalize_response)
    if clarification:
        return clarification

    rag_response = call_ai(
        client.rag_search,
        {
            'request_id': request_id,
            'search_queries': normalize_response['search_queries'],
            'rag_query_bundle': normalize_response.get('rag_query_bundle', {}),
            'filters': {
                'source_types': ['idisk', 'functional_ingredient'],
                'top_k': 8,
            },
        },
    )

    # RAG 결과가 없거나 score가 기준 미만이면 추가 확인 질문을 반환한다.
    if rag_response.get('needs_clarification') or rag_response.get('low_rag_score'):
        return {
            'status': 'needs_clarification',
            'questions': [
                {
                    'code': 'low_rag_quality',
                    'message': (
                        '입력하신 건강 목표와 관련된 충분한 근거 자료를 찾지 못했습니다. '
                        '건강 목표나 증상을 더 구체적으로 설명해 주시겠어요?'
                    ),
                }
            ],
        }

    report_response = call_ai(
        client.generate_report,
        {
            'request_id': request_id,
            'user_id': get_user_id(user),
            'normalized_input': build_report_normalized_input(
                request_data=request_data,
                normalized_input=normalize_response['normalized_input'],
            ),
            'rag_contexts': build_rag_contexts(rag_response['results']),
        },
    )

    output_guardrail = call_ai(
        client.output_guardrail,
        {
            'request_id': request_id,
            'task_type': 'report_generation',
            'content': build_report_output_text(report_response),
            'citations': report_response.get('citations', []),
        },
    )
    clarification = build_clarification_response(output_guardrail)
    if clarification:
        return clarification

    inject_iherb_links(report_response.get('recommended_ingredients', []))
    return report_response


def generate_report_chat_response(report, content, user=None):
    request_id = create_request_id()
    client = get_ai_client()
    current_user = user or report.user

    input_guardrail = call_ai(
        client.input_guardrail,
        {
            'request_id': request_id,
            'user_id': get_user_id(current_user),
            'task_type': 'chat_response',
            'input_text': content,
            'structured_input': {
                'report_id': report.id,
                'recommended_ingredients': [
                    ingredient.get('normalized_name', '')
                    for ingredient in report.recommended_ingredients
                    if ingredient.get('normalized_name')
                ],
            },
        },
    )

    if input_guardrail.get('is_allowed') is False:
        return {
            'role': 'assistant',
            'content': (
                input_guardrail.get('safe_message')
                or '요청을 처리할 수 없습니다. 질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.'
            ),
            'guardrail_result': {
                'is_allowed': False,
                'risk_level': input_guardrail.get('risk_level', 'high'),
            },
            'citations': [],
        }

    report_context = build_report_context(report)
    chat_response = call_ai(
        client.chat_respond,
        {
            'request_id': request_id,
            'user_id': get_user_id(current_user),
            'report_id': report.id,
            'report_context': report_context,
            'message': {
                'content': content,
            },
            'recent_messages': build_recent_messages(report),
        },
    )

    output_guardrail = call_ai(
        client.output_guardrail,
        {
            'request_id': request_id,
            'task_type': 'chat_response',
            'content': chat_response['content'],
            'citations': chat_response.get('citations', []),
        },
    )

    if not output_guardrail.get('is_allowed', True):
        chat_response['content'] = (
            output_guardrail.get('safe_message')
            or '안전한 답변을 제공하기 위해 응답을 제한했습니다.'
        )
        chat_response['guardrail_result'] = {
            'is_allowed': False,
            'risk_level': output_guardrail.get('risk_level', 'high'),
        }

    return {
        'role': 'assistant',
        'content': chat_response['content'],
        'guardrail_result': chat_response.get('guardrail_result', {}),
        'citations': chat_response.get('citations', []),
    }


def call_ai(method, payload):
    try:
        return method(payload)
    except AIServiceUnavailableError as error:
        raise AIServiceUnavailableException() from error
    except AIClientError as error:
        if error.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            raise AIServiceUnavailableException() from error
        raise AIServerException(
            ai_status_code=error.status_code,
            ai_payload=error.payload,
            ai_path=error.path,
        ) from error


def inject_iherb_links(ingredients: list) -> None:
    """
    recommended_ingredients 리스트를 in-place로 수정한다.
    normalized_name 기준으로 IngredientLinkMapping을 조회하고,
    allowlist 도메인 검증을 통과한 URL만 주입한다.
    """
    if not ingredients:
        return

    normalized_names = [
        ingredient.get('normalized_name', '')
        for ingredient in ingredients
        if ingredient.get('normalized_name')
    ]

    mappings = IngredientLinkMapping.objects.filter(
        normalized_name__in=normalized_names,
    )

    mapping_dict = {}
    blocked_names = set()
    for mapping in mappings:
        if not mapping.is_active:
            blocked_names.add(mapping.normalized_name)
        elif is_iherb_url_allowed(mapping.iherb_url):
            mapping_dict[mapping.normalized_name] = mapping
        else:
            blocked_names.add(mapping.normalized_name)

    for ingredient in ingredients:
        normalized_name = ingredient.get('normalized_name', '')
        mapping = mapping_dict.get(normalized_name)
        if mapping:
            ingredient['iherb_url'] = mapping.iherb_url
            ingredient['iherb_category_name'] = mapping.iherb_category_name or None
        elif normalized_name in blocked_names:
            ingredient['iherb_url'] = None
            ingredient['iherb_category_name'] = None
        elif is_iherb_url_allowed(ingredient.get('iherb_url')):
            ingredient['iherb_category_name'] = ingredient.get('iherb_category_name') or None
        else:
            ingredient['iherb_url'] = None
            ingredient['iherb_category_name'] = None


def is_iherb_url_allowed(url: str | None) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme == 'https' and parsed.netloc in IHERB_ALLOWED_DOMAINS
    except Exception:
        return False


def create_request_id():
    return f'req_{uuid.uuid4().hex}'


def get_user_id(user):
    return user.id if user and getattr(user, 'id', None) else 0


def build_input_text(request_data):
    parts = []
    parts.extend(item['name'] for item in request_data['health_goals'])
    parts.extend(item['name'] for item in request_data.get('medications', []))
    parts.extend(item['name'] for item in request_data.get('special_conditions', []))

    additional_notes = request_data.get('additional_notes')
    if additional_notes:
        parts.append(additional_notes)

    return ' '.join(parts)


def build_clarification_response(ai_response):
    if ai_response.get('is_allowed') is False:
        return {
            'status': 'needs_clarification',
            'questions': [
                {
                    'code': ai_response.get('blocked_reason') or 'ai_guardrail_blocked',
                    'message': ai_response.get('safe_message') or '요청을 처리할 수 없습니다.',
                }
            ],
        }

    if ai_response.get('needs_clarification'):
        return {
            'status': 'needs_clarification',
            'questions': ai_response.get('questions', []),
        }

    return None


def build_report_normalized_input(request_data, normalized_input):
    return {
        'age': request_data['age'],
        'gender': request_data['gender'],
        'health_goals': normalized_input.get('health_goals', []),
        'medications': normalized_input.get('medications', []),
        'special_conditions': normalized_input.get('special_conditions', []),
        'additional_terms': normalized_input.get('additional_terms', []),
        'additional_notes': request_data.get('additional_notes') or '',
    }


def build_rag_contexts(results):
    return [
        {
            'document_id': result['document_id'],
            'source_type': result['source_type'],
            'source_name': result.get('source_name'),
            'title': result['title'],
            'content': result['content'],
            'metadata': build_rag_metadata(result),
        }
        for result in results
    ]


def build_rag_metadata(result):
    metadata = dict(result.get('metadata', {}))
    if 'score' in result:
        metadata['score'] = result['score']
    return metadata


def build_report_output_text(report_response):
    ingredient_text = ' '.join(
        [
            ingredient.get('reason', '')
            for ingredient in report_response.get('recommended_ingredients', [])
        ]
    )

    return ' '.join(
        [
            report_response.get('title', ''),
            ingredient_text,
            report_response.get('disclaimer', ''),
        ]
    ).strip()


def build_report_context(report):
    return {
        'title': report.title,
        'recommended_ingredients': [
            {
                'name_ko': ingredient.get('name_ko', ''),
                'name_en': ingredient.get('name_en', ''),
                'normalized_name': ingredient.get('normalized_name', ''),
                'precautions': ingredient.get('precautions', []),
            }
            for ingredient in report.recommended_ingredients
        ],
        'disclaimer': report.disclaimer,
        'citations': report.citations,
    }


def build_recent_messages(report):
    messages = list(report.messages.order_by('-created_at', '-id')[:5])

    return [
        {
            'role': message.role,
            'content': message.content,
        }
        for message in reversed(messages)
    ]
