from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from community.models import Comment, Post
from reports.models import Report


User = get_user_model()


class AuthApiTests(APITestCase):
    def test_signup_login_refresh_and_logout(self):
        signup_response = self.client.post(
            '/api/v1/auth/signup/',
            {
                'email': 'user@example.com',
                'username': 'neutripic_user',
                'password': 'StrongPass1234!',
                'age': 30,
                'gender': 'female',
            },
            format='json',
        )

        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(signup_response.data['email'], 'user@example.com')
        self.assertNotIn('password', signup_response.data)

        login_response = self.client.post(
            '/api/v1/auth/login/',
            {
                'login_id': 'user@example.com',
                'password': 'StrongPass1234!',
            },
            format='json',
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', login_response.data)
        self.assertIn('refresh_token', login_response.data)
        self.assertEqual(login_response.data['user']['role'], 'user')

        refresh_response = self.client.post(
            '/api/v1/auth/token/refresh/',
            {'refresh_token': login_response.data['refresh_token']},
            format='json',
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', refresh_response.data)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access_token']}"
        )
        logout_response = self.client.post(
            '/api/v1/auth/logout/',
            {'refresh_token': login_response.data['refresh_token']},
            format='json',
        )

        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)


class UserApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            username='neutripic_user',
            password='StrongPass1234!',
            age=30,
            gender='female',
        )
        self.client.force_authenticate(user=self.user)

    def test_me_get_patch_and_password_change(self):
        get_response = self.client.get('/api/v1/users/me/')

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['email'], self.user.email)

        patch_response = self.client.patch(
            '/api/v1/users/me/',
            {
                'age': 31,
                'gender': 'female',
            },
            format='json',
        )

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['age'], 31)

        password_response = self.client.patch(
            '/api/v1/users/me/password/',
            {
                'current_password': 'StrongPass1234!',
                'new_password': 'NewStrongPass1234!',
            },
            format='json',
        )

        self.assertEqual(password_response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass1234!'))

    def test_mypage_returns_actual_counts(self):
        post = Post.objects.create(
            author=self.user,
            title='My post',
            content='My post content',
        )
        Comment.objects.create(
            post=post,
            author=self.user,
            content='My comment',
        )
        Report.objects.create(
            user=self.user,
            status=Report.STATUS_COMPLETED,
            title='My report',
            input_summary={'health_goals': ['fatigue']},
            recommended_ingredients=[
                {'normalized_name': 'magnesium', 'name_ko': 'Magnesium'}
            ],
            lifestyle_tips=[],
            disclaimer='disclaimer',
            citations=[],
        )

        response = self.client.get('/api/v1/mypage/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['report_count'], 1)
        self.assertEqual(response.data['post_count'], 1)
        self.assertEqual(response.data['comment_count'], 1)

    def test_me_delete(self):
        response = self.client.delete('/api/v1/users/me/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
