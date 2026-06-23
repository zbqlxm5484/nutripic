from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import HealthGoal, MedicationOption, Report, SpecialConditionOption


User = get_user_model()


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
