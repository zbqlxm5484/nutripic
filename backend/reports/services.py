def generate_report(request_data):
    # TODO: AI/RAG 서버가 준비되면 아래 mock 응답 대신 실제 내부 API 호출로 교체한다.
    # response = requests.post(AI_SERVER_URL, json=request_data, timeout=30)
    # response.raise_for_status()
    # return response.json()

    health_goal_names = [item['name'] for item in request_data['health_goals']]
    medication_names = [item['name'] for item in request_data.get('medications', [])]
    special_condition_names = [
        item['name'] for item in request_data.get('special_conditions', [])
    ]

    title_goals = '와 '.join(health_goal_names[:2])
    title = f'{title_goals} 개선을 위한 성분 리포트'

    return {
        'status': 'completed',
        'title': title,
        'input_summary': {
            'age': request_data['age'],
            'gender': request_data['gender'],
            'health_goals': health_goal_names,
            'medications': medication_names,
            'special_conditions': special_condition_names,
            'additional_notes': request_data.get('additional_notes', ''),
        },
        'recommended_ingredients': [
            {
                'name_ko': '마그네슘',
                'name_en': 'Magnesium',
                'normalized_name': 'magnesium',
                'reason': '수면과 근육 이완 관련 기능성 근거가 있어 후보로 선정되었습니다.',
                'expected_effects': ['수면 질 관리', '근육 기능 유지'],
                'recommended_dosage': '기능성 원료 인정현황 기준 범위 내에서 섭취하세요.',
                'side_effects': ['설사', '복부 불편감'],
                'precautions': ['질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.'],
                'iherb_url': 'https://kr.iherb.com/c/minerals',
            }
        ],
        'lifestyle_tips': [
            '카페인 섭취 시간과 양을 조절해 보세요.',
        ],
        'disclaimer': '질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.',
        'citations': [
            {
                'source_type': 'functional_ingredient',
                'source_name': '건강기능식품 기능성원료 인정현황',
                'document_id': 'functional_ingredient_magnesium',
            }
        ],
    }