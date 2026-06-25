from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from community.models import Comment, Post, PostLike
from reports.models import Report


User = get_user_model()


class AdminPanelApiTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='StrongPass1234!',
            role='admin',
        )
        self.normal_user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='StrongPass1234!',
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='other',
            password='StrongPass1234!',
        )
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)
        self.normal_client = APIClient()
        self.normal_client.force_authenticate(user=self.normal_user)

    def create_admin_data(self):
        post = Post.objects.create(
            author=self.normal_user,
            title='Admin target post',
            content='Admin target content',
        )
        comment = Comment.objects.create(
            post=post,
            author=self.other_user,
            content='Admin target comment',
        )
        PostLike.objects.create(post=post, user=self.admin_user)
        report = Report.objects.create(
            user=self.normal_user,
            status=Report.STATUS_COMPLETED,
            title='Admin target report',
            input_summary={
                'health_goals': [
                    {
                        'code': 'fatigue',
                        'name': 'Fatigue',
                    }
                ]
            },
            recommended_ingredients=[
                {
                    'normalized_name': 'magnesium',
                    'name_ko': 'Magnesium',
                }
            ],
            lifestyle_tips=[],
            disclaimer='disclaimer',
            citations=[],
        )
        return post, comment, report

    def test_admin_permission_checks(self):
        anonymous_response = self.client.get('/api/v1/admin/users/')
        self.assertEqual(anonymous_response.status_code, status.HTTP_401_UNAUTHORIZED)

        normal_response = self.normal_client.get('/api/v1/admin/users/')
        self.assertEqual(normal_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_apis(self):
        self.create_admin_data()

        list_response = self.admin_client.get('/api/v1/admin/users/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertIn('results', list_response.data)

        detail_response = self.admin_client.get(
            f'/api/v1/admin/users/{self.normal_user.id}/'
        )
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['id'], self.normal_user.id)
        self.assertEqual(detail_response.data['post_count'], 1)
        self.assertEqual(detail_response.data['report_count'], 1)

        patch_response = self.admin_client.patch(
            f'/api/v1/admin/users/{self.normal_user.id}/',
            {'is_active': False},
            format='json',
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.normal_user.refresh_from_db()
        self.assertFalse(self.normal_user.is_active)

    def test_admin_post_comment_and_statistics_apis(self):
        post, comment, report = self.create_admin_data()

        post_list_response = self.admin_client.get('/api/v1/admin/posts/')
        self.assertEqual(post_list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(post_list_response.data['results'][0]['id'], post.id)
        self.assertEqual(post_list_response.data['results'][0]['like_count'], 1)
        self.assertEqual(post_list_response.data['results'][0]['comment_count'], 1)

        comment_list_response = self.admin_client.get('/api/v1/admin/comments/')
        self.assertEqual(comment_list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(comment_list_response.data['results'][0]['id'], comment.id)

        statistics_response = self.admin_client.get('/api/v1/admin/reports/statistics/')
        self.assertEqual(statistics_response.status_code, status.HTTP_200_OK)
        self.assertEqual(statistics_response.data['report_count'], 1)
        self.assertEqual(
            statistics_response.data['popular_health_goals'][0]['code'],
            'fatigue',
        )
        self.assertEqual(
            statistics_response.data['popular_ingredients'][0]['normalized_name'],
            'magnesium',
        )

        forbidden_comment_delete_response = self.normal_client.delete(
            f'/api/v1/admin/comments/{comment.id}/'
        )
        self.assertEqual(
            forbidden_comment_delete_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        comment_delete_response = self.admin_client.delete(
            f'/api/v1/admin/comments/{comment.id}/'
        )
        self.assertEqual(comment_delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())

        forbidden_post_delete_response = self.normal_client.delete(
            f'/api/v1/admin/posts/{post.id}/'
        )
        self.assertEqual(
            forbidden_post_delete_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        post_delete_response = self.admin_client.delete(
            f'/api/v1/admin/posts/{post.id}/'
        )
        self.assertEqual(post_delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post.id).exists())
        self.assertTrue(Report.objects.filter(id=report.id).exists())
