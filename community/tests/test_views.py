from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from community.models import ForumPost, ForumComment, ForumPostLike

class CommunityViewsTests(APITestCase):
    def setUp(self):
        # Create active verified user
        self.user = User.objects.create_user(
            email="communityuser@example.com",
            password="password123",
            full_name="Community User",
            is_verified=True
        )
        
        # Get JWT Token
        login_url = reverse('login')
        response = self.client.post(login_url, {"email": "communityuser@example.com", "password": "password123"})
        self.access_token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create a post for testing
        self.post_obj = ForumPost.objects.create(
            user=self.user,
            content="Welcome to the fitness forum!"
        )

        # Create another user for testing permissions
        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="password123",
            full_name="Other User",
            is_verified=True
        )

        # URLs
        self.posts_url = reverse('community:forum-post-list')
        self.post_detail_url = reverse('community:forum-post-detail', kwargs={'pk': self.post_obj.id})
        self.like_url = reverse('community:forum-post-like')
        self.comment_create_url = reverse('community:forum-comment-create')
        self.comment_list_url = reverse('community:forum-comments', kwargs={'post_id': self.post_obj.id})

    def test_list_forum_posts(self):
        response = self.client.get(self.posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], "Welcome to the fitness forum!")

    def test_create_forum_post(self):
        payload = {"content": "Checking in today!"}
        response = self.client.post(self.posts_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], "Checking in today!")
        self.assertTrue(ForumPost.objects.filter(content="Checking in today!").exists())

    def test_update_forum_post(self):
        payload = {"content": "Welcome to the updated fitness forum!"}
        response = self.client.patch(self.post_detail_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post_obj.refresh_from_db()
        self.assertEqual(self.post_obj.content, "Welcome to the updated fitness forum!")

    def test_delete_forum_post(self):
        response = self.client.delete(self.post_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ForumPost.objects.filter(id=self.post_obj.id).exists())

    def test_like_and_unlike_forum_post(self):
        # 1. Like
        payload = {"post": self.post_obj.id}
        response = self.client.post(self.like_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post_obj.refresh_from_db()
        self.assertEqual(self.post_obj.likes, 1)

        # 2. Unlike
        response_unlike = self.client.post(self.like_url, payload, format='json')
        self.assertEqual(response_unlike.status_code, status.HTTP_200_OK)
        self.post_obj.refresh_from_db()
        self.assertEqual(self.post_obj.likes, 0)

    def test_create_comment(self):
        payload = {
            "post": self.post_obj.id,
            "content": "Awesome post!"
        }
        response = self.client.post(self.comment_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], "Awesome post!")

        # Verify comment is created
        self.assertTrue(ForumComment.objects.filter(content="Awesome post!").exists())

    def test_list_comments(self):
        # Create a comment
        comment = ForumComment.objects.create(
            user=self.user,
            post=self.post_obj,
            content="Great advice."
        )
        response = self.client.get(self.comment_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)

    def test_update_and_delete_comment(self):
        comment = ForumComment.objects.create(
            user=self.user,
            post=self.post_obj,
            content="Typo here."
        )
        comment_detail_url = reverse('community:forum-comment-detail', kwargs={'pk': comment.id})
        
        # Patch
        payload = {"content": "Fixed typo."}
        response = self.client.patch(comment_detail_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.content, "Fixed typo.")

        # Delete
        response_del = self.client.delete(comment_detail_url)
        self.assertEqual(response_del.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ForumComment.objects.filter(id=comment.id).exists())
