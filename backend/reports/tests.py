from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from .models import HealthGoal, IngredientLinkMapping, MedicationOption, Report, SpecialConditionOption


User = get_user_model()


class FakeAIClient:
    def input_guardrail(self, payload):
        return {
            'is_allowed': True,
            'risk_level': 'low',
            'blocked_reason': None,
            'safe_message': None,
            'needs_clarification': False,
            'questions': [],
        }

    def normalize(self, payload):
        return {
            'normalized_input': {
                'health_goals': [
                    {
                        'code': item['code'],
                        'name_ko': item['name'],
                        'name_en': item['code'],
                        'priority': item['priority'],
                        'confidence': 0.95,
                    }
                    for item in payload['health_goals']
                ],
                'medications': [
                    {
                        'code': item['code'],
                        'name_ko': item['name'],
                        'name_en': item['code'],
                        'confidence': 0.95,
                    }
                    for item in payload.get('medications', [])
                ],
                'special_conditions': [
                    {
                        'code': item['code'],
                        'name_ko': item['name'],
                        'name_en': item['code'],
                        'confidence': 0.95,
                    }
                    for item in payload.get('special_conditions', [])
                ],
                'additional_terms': [],
            },
            'search_queries': ['fatigue supplements'],
            'rag_query_bundle': {
                'idisk': {
                    'ingredient_ids': [],
                    'condition_ids': ['DIS000000'],
                    'drug_ids': ['D000000'],
                    'relation_targets': ['is_effective_for', 'interacts_with'],
                },
                'text_queries': ['fatigue supplements'],
            },
            'needs_clarification': False,
            'questions': [],
        }

    def rag_search(self, payload):
        assert payload['rag_query_bundle']['idisk']['condition_ids'] == ['DIS000000']
        return {
            'results': [
                {
                    'document_id': 'functional_ingredient_magnesium',
                    'source_type': 'functional_ingredient',
                    'source_name': '건강기능식품 기능성원료 인정현황',
                    'title': '마그네슘',
                    'content': '기능성, 일일섭취량, 섭취 시 주의사항 요약',
                    'score': 0.91,
                    'metadata': {
                        'ingredient_name_ko': '마그네슘',
                        'ingredient_name_en': 'Magnesium',
                        'normalized_name': 'magnesium',
                        'daily_dosage': '기능성 원료 인정현황 기준 범위 내에서 섭취하세요.',
                        'expected_effects': ['수면 질 관리', '근육 기능 유지'],
                        'side_effects': ['설사', '복부 불편감'],
                        'precautions': ['질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.'],
                    },
                }
            ],
        }

    def generate_report(self, payload):
        normalized_input = payload['normalized_input']

        return {
            'status': 'completed',
            'title': 'Fatigue 개선을 위한 성분 리포트',
            'input_summary': {
                'age': normalized_input['age'],
                'gender': normalized_input['gender'],
                'health_goals': ['Fatigue'],
                'medications': ['Anticoagulant'],
                'special_conditions': ['Allergy'],
                'additional_notes': normalized_input.get('additional_notes', ''),
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
                }
            ],
            'lifestyle_tips': ['카페인 섭취 시간과 양을 조절해 보세요.'],
            'disclaimer': '질환이 있거나 약을 복용 중인 경우 전문가와 상담하세요.',
            'citations': [
                {
                    'source_type': 'functional_ingredient',
                    'source_name': '건강기능식품 기능성원료 인정현황',
                    'document_id': 'functional_ingredient_magnesium',
                }
            ],
            'guardrail_result': {
                'is_allowed': True,
                'risk_level': 'low',
            },
        }

    def output_guardrail(self, payload):
        return {
            'is_allowed': True,
            'risk_level': 'low',
            'blocked_reason': None,
            'safe_message': None,
            'required_fixes': [],
        }

    def chat_respond(self, payload):
        return {
            'content': (
                '일반적으로 리포트에 포함된 성분은 개인의 건강 상태와 복용 중인 약을 '
                '함께 고려해 섭취 여부를 판단하는 것이 좋습니다. 질환이 있거나 약을 '
                '복용 중인 경우 전문가와 상담하세요.'
            ),
            'guardrail_result': {
                'is_allowed': True,
                'risk_level': 'low',
            },
            'citations': [
                {
                    'source_type': 'functional_ingredient',
                    'source_name': '건강기능식품 기능성원료 인정현황',
                    'document_id': 'functional_ingredient_magnesium',
                }
            ],
        }


class ChatInputBlockedAIClient(FakeAIClient):
    def __init__(self):
        self.chat_respond_called = False

    def input_guardrail(self, payload):
        if payload.get('task_type') == 'chat_response':
            return {
                'is_allowed': False,
                'risk_level': 'high',
                'blocked_reason': 'medical_high_risk',
                'safe_message': '의학적 진단, 처방, 약물 변경은 제공할 수 없습니다. 전문가와 상담하세요.',
                'needs_clarification': False,
                'questions': [],
            }

        return super().input_guardrail(payload)

    def chat_respond(self, payload):
        self.chat_respond_called = True
        return super().chat_respond(payload)


class SurveyMetadataApiTests(APITestCase):
    def setUp(self):
        self.health_goal = HealthGoal.objects.create(
            code='fatigue',
            name='Fatigue',
            order=1,
            is_active=True,
        )
        self.medication = MedicationOption.objects.create(
            code='anticoagulant',
            name='Anticoagulant',
            order=1,
            is_active=True,
        )
        self.condition = SpecialConditionOption.objects.create(
            code='allergy',
            name='Allergy',
            order=1,
            is_active=True,
        )

    def test_metadata_endpoints_are_public(self):
        health_response = self.client.get('/api/v1/health_goals/')
        medication_response = self.client.get('/api/v1/medication_options/')
        condition_response = self.client.get('/api/v1/special_condition_options/')

        self.assertEqual(health_response.status_code, status.HTTP_200_OK)
        self.assertEqual(medication_response.status_code, status.HTTP_200_OK)
        self.assertEqual(condition_response.status_code, status.HTTP_200_OK)
        self.assertEqual(health_response.data[0]['code'], self.health_goal.code)
        self.assertEqual(medication_response.data[0]['code'], self.medication.code)
        self.assertEqual(condition_response.data[0]['code'], self.condition.code)


class ReportApiTests(APITestCase):
    def setUp(self):
        self.ai_client_patcher = patch(
            'reports.services.get_ai_client',
            return_value=FakeAIClient(),
        )
        self.ai_client_patcher.start()
        self.addCleanup(self.ai_client_patcher.stop)

        self.user = User.objects.create_user(
            email='user@example.com',
            username='neutripic_user',
            password='StrongPass1234!',
        )
        self.client.force_authenticate(user=self.user)
        self.health_goal = HealthGoal.objects.create(
            code='fatigue',
            name='Fatigue',
            order=1,
            is_active=True,
        )
        self.medication = MedicationOption.objects.create(
            code='anticoagulant',
            name='Anticoagulant',
            order=1,
            is_active=True,
        )
        self.condition = SpecialConditionOption.objects.create(
            code='allergy',
            name='Allergy',
            order=1,
            is_active=True,
        )

    def create_report(self):
        return self.client.post(
            '/api/v1/reports/',
            {
                'age': 30,
                'gender': 'female',
                'health_goals': [
                    {
                        'code': self.health_goal.code,
                        'priority': 1,
                    }
                ],
                'medications': [
                    {
                        'code': self.medication.code,
                    }
                ],
                'special_conditions': [
                    {
                        'code': self.condition.code,
                    }
                ],
                'additional_notes': 'notes',
            },
            format='json',
        )

    def test_report_crud(self):
        create_response = self.create_report()

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('recommended_ingredients', create_response.data)
        report_id = create_response.data['id']

        list_response = self.client.get('/api/v1/reports/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)

        detail_response = self.client.get(f'/api/v1/reports/{report_id}/')
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['id'], report_id)

        patch_response = self.client.patch(
            f'/api/v1/reports/{report_id}/',
            {'title': 'Updated title'},
            format='json',
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['title'], 'Updated title')

        delete_response = self.client.delete(f'/api/v1/reports/{report_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Report.objects.filter(id=report_id).exists())

    def test_report_messages(self):
        create_response = self.create_report()
        report_id = create_response.data['id']

        list_response = self.client.get(f'/api/v1/reports/{report_id}/messages/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data, [])

        message_response = self.client.post(
            f'/api/v1/reports/{report_id}/messages/',
            {'content': 'When should I take magnesium?'},
            format='json',
        )

        self.assertEqual(message_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(message_response.data['role'], 'assistant')
        self.assertIn('content', message_response.data)
        self.assertIn('citations', message_response.data)

    def test_report_message_input_guardrail_blocks_before_chat_generation(self):
        guarded_client = ChatInputBlockedAIClient()

        with patch('reports.services.get_ai_client', return_value=guarded_client):
            create_response = self.create_report()
            report_id = create_response.data['id']

            message_response = self.client.post(
                f'/api/v1/reports/{report_id}/messages/',
                {'content': '복용 중인 약을 끊어도 되나요?'},
                format='json',
            )

        self.assertEqual(message_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(message_response.data['role'], 'assistant')
        self.assertEqual(message_response.data['guardrail_result']['is_allowed'], False)
        self.assertIn('전문가와 상담', message_response.data['content'])
        self.assertFalse(guarded_client.chat_respond_called)

    @override_settings(REPORT_DAILY_CREATE_LIMIT=3)
    def test_report_daily_create_limit(self):
        for _ in range(3):
            response = self.create_report()
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        limited_response = self.create_report()

        self.assertEqual(
            limited_response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.assertEqual(limited_response.data['error_code'], 'rate_limit_exceeded')
        self.assertEqual(limited_response.data['details']['resource'], 'report')

    @override_settings(REPORT_CHAT_DAILY_CREATE_LIMIT=30)
    def test_report_chat_daily_create_limit(self):
        create_response = self.create_report()
        report_id = create_response.data['id']

        for _ in range(30):
            response = self.client.post(
                f'/api/v1/reports/{report_id}/messages/',
                {'content': 'When should I take magnesium?'},
                format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        limited_response = self.client.post(
            f'/api/v1/reports/{report_id}/messages/',
            {'content': 'When should I take magnesium?'},
            format='json',
        )

        self.assertEqual(
            limited_response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        self.assertEqual(limited_response.data['error_code'], 'rate_limit_exceeded')
        self.assertEqual(
            limited_response.data['details']['resource'],
            'report_chat',
        )


class IherbLinkMappingTests(APITestCase):
    """
    iHerb URL allowlist 검증 및 서버 저장값 기반 응답 주입 테스트.
    """

    def setUp(self):
        self.ai_client_patcher = patch(
            'reports.services.get_ai_client',
            return_value=FakeAIClient(),
        )
        self.ai_client_patcher.start()
        self.addCleanup(self.ai_client_patcher.stop)

        self.user = User.objects.create_user(
            email='iherb_test@example.com',
            username='iherb_tester',
            password='StrongPass1234!',
        )
        self.client.force_authenticate(user=self.user)
        self.health_goal = HealthGoal.objects.create(
            code='fatigue', name='Fatigue', order=1, is_active=True
        )
        self.medication = MedicationOption.objects.create(
            code='anticoagulant', name='Anticoagulant', order=1, is_active=True
        )
        self.condition = SpecialConditionOption.objects.create(
            code='allergy', name='Allergy', order=1, is_active=True
        )

    def _create_report(self):
        return self.client.post(
            '/api/v1/reports/',
            {
                'age': 30,
                'gender': 'female',
                'health_goals': [{'code': self.health_goal.code, 'priority': 1}],
                'medications': [{'code': self.medication.code}],
                'special_conditions': [{'code': self.condition.code}],
                'additional_notes': 'notes',
            },
            format='json',
        )

    def test_iherb_url_is_injected_when_mapping_exists(self):
        """IngredientLinkMapping이 있는 성분은 iherb_url이 응답에 포함된다."""
        IngredientLinkMapping.objects.create(
            normalized_name='magnesium',
            ingredient_name_ko='마그네슘',
            iherb_url='https://kr.iherb.com/c/minerals',
            iherb_category_name='Minerals',
            is_active=True,
        )

        response = self._create_report()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ingredients = response.data['recommended_ingredients']
        self.assertTrue(len(ingredients) > 0)
        magnesium = next(
            (i for i in ingredients if i.get('normalized_name') == 'magnesium'),
            None,
        )
        self.assertIsNotNone(magnesium)
        self.assertEqual(magnesium['iherb_url'], 'https://kr.iherb.com/c/minerals')
        self.assertEqual(magnesium['iherb_category_name'], 'Minerals')

    def test_iherb_url_is_null_when_no_mapping(self):
        """IngredientLinkMapping이 없는 성분은 iherb_url이 null이다."""
        # mapping 없음
        response = self._create_report()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ingredients = response.data['recommended_ingredients']
        magnesium = next(
            (i for i in ingredients if i.get('normalized_name') == 'magnesium'),
            None,
        )
        self.assertIsNotNone(magnesium)
        self.assertIsNone(magnesium.get('iherb_url'))

    def test_iherb_url_blocked_when_not_in_allowlist(self):
        """allowlist 밖 도메인 URL은 저장되어 있어도 응답에 주입되지 않는다."""
        IngredientLinkMapping.objects.create(
            normalized_name='magnesium',
            ingredient_name_ko='마그네슘',
            iherb_url='https://evil.example.com/magnesium',  # allowlist 외 도메인
            iherb_category_name='',
            is_active=True,
        )

        response = self._create_report()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ingredients = response.data['recommended_ingredients']
        magnesium = next(
            (i for i in ingredients if i.get('normalized_name') == 'magnesium'),
            None,
        )
        self.assertIsNotNone(magnesium)
        # allowlist 밖이므로 주입 안 됨
        self.assertIsNone(magnesium.get('iherb_url'))

    def test_inactive_mapping_is_not_injected(self):
        """is_active=False인 매핑은 주입되지 않는다."""
        IngredientLinkMapping.objects.create(
            normalized_name='magnesium',
            ingredient_name_ko='마그네슘',
            iherb_url='https://kr.iherb.com/c/minerals',
            iherb_category_name='Minerals',
            is_active=False,  # 비활성
        )

        response = self._create_report()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ingredients = response.data['recommended_ingredients']
        magnesium = next(
            (i for i in ingredients if i.get('normalized_name') == 'magnesium'),
            None,
        )
        self.assertIsNotNone(magnesium)
        self.assertIsNone(magnesium.get('iherb_url'))

    def test_iherb_mapping_rejects_non_allowlist_url_on_validation(self):
        mapping = IngredientLinkMapping(
            normalized_name='magnesium',
            ingredient_name_ko='마그네슘',
            ingredient_name_en='Magnesium',
            iherb_url='https://evil.example.com/magnesium',
            iherb_category_name='Minerals',
            is_active=True,
        )

        with self.assertRaises(ValidationError):
            mapping.full_clean()
