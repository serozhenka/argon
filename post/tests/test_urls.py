from django.test import TestCase
from django.urls import resolve, reverse
from model_bakery import baker

from post import views
from post.models import Post, Comment

class TestPostUrls(TestCase):

    def setUp(self) -> None:
        self.post = baker.make(Post)
        self.comment = baker.make(Comment)

    def test_feed_url_resolved(self):
        url = reverse('post:feed')
        self.assertEqual(resolve(url).func, views.feed_page)

    def test_post_edit_url_resolved(self):
        url = reverse('post:post-edit', kwargs={'post_id': self.post.id})
        self.assertEqual(resolve(url).func, views.post_edit_page)

    def test_post_add_url_resolved(self):
        url = reverse('post:post-add')
        self.assertEqual(resolve(url).func, views.post_add_page)

    def test_post_page_url_resolved(self):
        url = reverse('post:post-page', kwargs={'post_id': self.post.id})
        self.assertEqual(resolve(url).func, views.post_page)

    def test_post_like_url_resolved(self):
        url = reverse('post:post-like', kwargs={'post_id': self.post.id})
        self.assertEqual(resolve(url).func, views.post_like_page)

    def test_post_comment_url_resolved(self):
        url = reverse('post:post-comment', kwargs={'post_id': self.post.id})
        self.assertEqual(resolve(url).func, views.post_comment_page)

    def test_post_comment_like_url_resolved(self):
        url = reverse('post:post-comment-like', kwargs={'comment_id': self.comment.id})
        self.assertEqual(resolve(url).func, views.post_comment_like_page)

    def test_post_comment_remove_url_resolved(self):
        url = reverse('post:post-comment-remove', kwargs={'comment_id': self.comment.id})
        self.assertEqual(resolve(url).func, views.post_comment_remove_page)