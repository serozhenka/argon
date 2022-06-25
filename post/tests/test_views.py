import json

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from model_bakery import baker

from users.models import Account
from post.models import Post, Comment, PostImage, CommentLike

class TestPostPublicViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.post = baker.make(Post)
        self.comment = baker.make(Comment)

    def test_feed_get_request(self):
        url = reverse('post:feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_post_page_get_request(self):
        url = reverse('post:post-page', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_post_add_get_request(self):
        url = reverse('post:post-add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_post_edit_get_request(self):
        url = reverse('post:post-edit', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_post_like_get_request(self):
        url = reverse('post:post-like', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_post_comment_get_request(self):
        url = reverse('post:post-comment', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_post_comment_like_get_request(self):
        url = reverse('post:post-comment-like', kwargs={'comment_id': self.comment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_post_comment_remove_get_request(self):
        url = reverse('post:post-comment-remove', kwargs={'comment_id': self.comment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class TestPostPrivateViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()

        self.pwd = '21b4f6bcb67f57ce9487cfbd0eb91265'
        self.user = baker.make(Account)
        self.other_user = baker.make(Account)
        self.user.set_password(self.pwd)
        self.user.save()
        self.client.login(email=self.user.email, password=self.pwd)

        self.ou_post = baker.make(Post, user=self.other_user)

    def test_feed_get_request(self):
        url = reverse('post:feed')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_post_page_get_request(self):
        url = reverse('post:post-page', kwargs={'post_id': self.ou_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_post_page_unknown_post_id_get_request(self):
        url = reverse('post:post-page', kwargs={'post_id': -1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_post_page_user_is_private_not_following_get_request(self):
        self.other_user.is_public = False
        self.other_user.save()
        url = reverse('post:post-page', kwargs={'post_id': self.ou_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_post_page_user_is_private_following_get_request(self):
        self.other_user.is_public = False
        self.other_user.save()
        self.user.following.add_following(self.other_user)
        url = reverse('post:post-page', kwargs={'post_id': self.ou_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_post_add_get_request(self):
        url = reverse('post:post-add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_add_no_images_post_request(self):
        url = reverse('post:post-add')
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 302)

    def test_post_add_post_request(self):
        url = reverse('post:post-add')
        post_count = Post.objects.count()
        post_images = list(PostImage.objects.all())

        with open(str(settings.MEDIA_ROOT) + "/" + settings.DEFAULT_PROFILE_IMAGE_FILEPATH, 'rb') as img:
            response = self.client.post(url, {'images': [img], 'description': ""})

        added_post_image = list(set(PostImage.objects.all()) - set(post_images))[0]

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.count(), post_count + 1)
        self.assertTrue(PostImage.objects.count(), len(post_images) + 1)

        added_post_image.image.delete(save=False)

    def test_post_edit_not_users_get_request(self):
        url = reverse('post:post-edit', kwargs={'post_id': self.ou_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_post_edit_get_request(self):
        post = baker.make(Post, user=self.user)
        url = reverse('post:post-edit', kwargs={'post_id': post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_post_like_get_request(self):
        post = baker.make(Post, user=self.user)
        url = reverse('post:post-like', kwargs={'post_id': post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_post_like_post_request(self):
        post = baker.make(Post, user=self.user)
        url = reverse('post:post-like', kwargs={'post_id': post.id})
        response = self.client.generic('POST', url, json.dumps({'action': 'like'}))
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.likes_count, 1)
        self.assertEqual(response_data['response_result'], "success")

    def test_post_like_no_action_post_request(self):
        post = baker.make(Post, user=self.user)
        post_likes_count = post.likes_count
        url = reverse('post:post-like', kwargs={'post_id': post.id})
        response = self.client.generic('POST', url, json.dumps({}))
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.likes_count, post_likes_count)
        self.assertEqual(response_data['response_result'], "error")

    def test_post_like_private_user_post_request(self):
        self.other_user.is_public = False
        self.other_user.save()
        url = reverse('post:post-like', kwargs={'post_id': self.ou_post.id})
        response = self.client.generic('POST', url, json.dumps({'action': 'like'}))
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ou_post.likes_count, 0)
        self.assertEqual(response_data['response_result'], "error")

    def test_post_comment_get_request(self):
        url = reverse('post:post-comment', kwargs={'post_id': self.ou_post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_post_comment_post_request(self):
        url = reverse('post:post-comment', kwargs={'post_id': self.ou_post.id})
        response = self.client.generic("POST", url, json.dumps({'description': 'comment'}))
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['response_result'], "success")
        self.assertEqual(Comment.objects.filter(post=self.ou_post).count(), 1)

    def test_post_comment_no_description_post_request(self):
        url = reverse('post:post-comment', kwargs={'post_id': self.ou_post.id})
        response = self.client.generic("POST", url, json.dumps({}))
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['response_result'], "error")
        self.assertEqual(Comment.objects.filter(post=self.ou_post).count(), 0)

    def test_post_comment_like_get_request(self):
        comment = baker.make(Comment, user=self.user)
        url = reverse('post:post-comment-like', kwargs={'comment_id': comment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_post_comment_like_post_request(self):
        comment = baker.make(Comment, user=self.user)
        url = reverse('post:post-comment-like', kwargs={'comment_id': comment.id})
        response = self.client.generic("POST", url, json.dumps({"action": "like"}))
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['response_result'], "success")
        self.assertEqual(CommentLike.objects.filter(comment=comment).count(), 1)

    def test_post_comment_like_no_action_post_request(self):
        comment = baker.make(Comment, user=self.user)
        url = reverse('post:post-comment-like', kwargs={'comment_id': comment.id})
        response = self.client.generic("POST", url, json.dumps({}))
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['response_result'], "error")
        self.assertEqual(CommentLike.objects.filter(comment=comment).count(), 0)



