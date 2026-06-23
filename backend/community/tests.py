from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Comment, Post, PostLike


User = get_user_model()


class CommunityApiTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            email='author@example.com',
            username='author',
            password='StrongPass1234!',
        )
        self.other = User.objects.create_user(
            email='other@example.com',
            username='other',
            password='StrongPass1234!',
        )
        self.author_client = APIClient()
        self.author_client.force_authenticate(user=self.author)
        self.other_client = APIClient()
        self.other_client.force_authenticate(user=self.other)

    def test_post_crud_and_permissions(self):
        public_response = self.client.get('/api/v1/posts/')
        self.assertEqual(public_response.status_code, status.HTTP_200_OK)

        unauthorized_response = self.client.post(
            '/api/v1/posts/',
            {
                'title': 'Guest title',
                'content': 'Guest content',
            },
            format='json',
        )
        self.assertEqual(unauthorized_response.status_code, status.HTTP_401_UNAUTHORIZED)

        create_response = self.author_client.post(
            '/api/v1/posts/',
            {
                'title': 'Post title',
                'content': 'Post content',
            },
            format='json',
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        post_id = create_response.data['id']

        detail_response = self.client.get(f'/api/v1/posts/{post_id}/')
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['id'], post_id)

        forbidden_patch_response = self.other_client.patch(
            f'/api/v1/posts/{post_id}/',
            {
                'title': 'Bad title',
                'content': 'Bad content',
            },
            format='json',
        )
        self.assertEqual(forbidden_patch_response.status_code, status.HTTP_403_FORBIDDEN)

        patch_response = self.author_client.patch(
            f'/api/v1/posts/{post_id}/',
            {
                'title': 'Updated title',
                'content': 'Updated content',
            },
            format='json',
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['title'], 'Updated title')

        forbidden_delete_response = self.other_client.delete(f'/api/v1/posts/{post_id}/')
        self.assertEqual(forbidden_delete_response.status_code, status.HTTP_403_FORBIDDEN)

        delete_response = self.author_client.delete(f'/api/v1/posts/{post_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post_id).exists())

    def test_like_and_ordering(self):
        first_post = Post.objects.create(
            author=self.author,
            title='First post',
            content='First content',
        )
        second_post = Post.objects.create(
            author=self.author,
            title='Second post',
            content='Second content',
        )
        PostLike.objects.create(post=second_post, user=self.other)

        like_response = self.author_client.post(f'/api/v1/posts/{first_post.id}/like/')
        self.assertEqual(like_response.status_code, status.HTTP_200_OK)
        self.assertTrue(like_response.data['is_liked'])
        self.assertEqual(like_response.data['like_count'], 1)

        duplicate_response = self.author_client.post(f'/api/v1/posts/{first_post.id}/like/')
        self.assertEqual(duplicate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(duplicate_response.data['like_count'], 1)

        unlike_response = self.author_client.delete(f'/api/v1/posts/{first_post.id}/like/')
        self.assertEqual(unlike_response.status_code, status.HTTP_200_OK)
        self.assertFalse(unlike_response.data['is_liked'])
        self.assertEqual(unlike_response.data['like_count'], 0)

        ordering_response = self.client.get('/api/v1/posts/?ordering=likes')
        self.assertEqual(ordering_response.status_code, status.HTTP_200_OK)
        self.assertEqual(ordering_response.data['results'][0]['id'], second_post.id)

        invalid_ordering_response = self.client.get('/api/v1/posts/?ordering=bad')
        self.assertEqual(invalid_ordering_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid_ordering_response.data['error_code'], 'validation_error')

    def test_comments_replies_and_permissions(self):
        post = Post.objects.create(
            author=self.author,
            title='Post title',
            content='Post content',
        )

        unauthorized_response = self.client.post(
            f'/api/v1/posts/{post.id}/comments/',
            {
                'content': 'Guest comment',
                'parent_id': None,
            },
            format='json',
        )
        self.assertEqual(unauthorized_response.status_code, status.HTTP_401_UNAUTHORIZED)

        comment_response = self.author_client.post(
            f'/api/v1/posts/{post.id}/comments/',
            {
                'content': 'Root comment',
                'parent_id': None,
            },
            format='json',
        )
        self.assertEqual(comment_response.status_code, status.HTTP_201_CREATED)
        comment_id = comment_response.data['id']
        self.assertIsNone(comment_response.data['parent_id'])

        reply_response = self.other_client.post(
            f'/api/v1/posts/{post.id}/comments/',
            {
                'content': 'Reply comment',
                'parent_id': comment_id,
            },
            format='json',
        )
        self.assertEqual(reply_response.status_code, status.HTTP_201_CREATED)
        reply_id = reply_response.data['id']
        self.assertEqual(reply_response.data['parent_id'], comment_id)

        nested_reply_response = self.author_client.post(
            f'/api/v1/posts/{post.id}/comments/',
            {
                'content': 'Nested reply',
                'parent_id': reply_id,
            },
            format='json',
        )
        self.assertEqual(nested_reply_response.status_code, status.HTTP_400_BAD_REQUEST)

        list_response = self.client.get(f'/api/v1/posts/{post.id}/comments/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data[0]['id'], comment_id)
        self.assertEqual(list_response.data[0]['replies'][0]['id'], reply_id)

        forbidden_patch_response = self.other_client.patch(
            f'/api/v1/comments/{comment_id}/',
            {'content': 'Bad edit'},
            format='json',
        )
        self.assertEqual(forbidden_patch_response.status_code, status.HTTP_403_FORBIDDEN)

        patch_response = self.author_client.patch(
            f'/api/v1/comments/{comment_id}/',
            {'content': 'Updated comment'},
            format='json',
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['content'], 'Updated comment')

        forbidden_delete_response = self.other_client.delete(f'/api/v1/comments/{comment_id}/')
        self.assertEqual(forbidden_delete_response.status_code, status.HTTP_403_FORBIDDEN)

        delete_response = self.author_client.delete(f'/api/v1/comments/{comment_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())
