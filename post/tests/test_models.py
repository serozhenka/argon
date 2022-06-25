from PIL import Image
from django.conf import settings
from django.test import TestCase
from django.contrib.humanize.templatetags.humanize import naturaltime
from model_bakery import baker
from tempfile import NamedTemporaryFile

from post.models import Post, PostImage, Comment, PostLike, CommentLike, get_post_image_path


class TestPostModel(TestCase):
    """Testing custom user model"""

    def setUp(self) -> None:
        self.post = baker.make(Post)
        self.post_image = PostImage.objects.create(post=self.post)
        self.comment = baker.make(Comment, post=self.post)

    def test_post_created(self):
        self.assertTrue(isinstance(self.post, Post))
        self.assertEqual(str(self.post), str(self.post.id))
        self.assertEqual(self.post.likes_count, 0)
        self.assertEqual(self.post.timestamp, str(naturaltime(self.post.created)))

    def test_post_image_created(self):
        self.assertTrue(isinstance(self.post_image, PostImage))
        self.assertEqual(str(self.post_image), f"{self.post.user.username} post image")
        self.assertEqual(self.post_image.order, 0)

    def test_comment_created(self):
        self.assertTrue(isinstance(self.comment, Comment))
        self.assertEqual(str(self.comment), f'{self.comment.id} by {self.comment.user.username}')
        self.assertEqual(self.comment.likes_count, 0)
        self.assertEqual(self.comment.timestamp, str(naturaltime(self.comment.created)))

    def test_image_url_resolved(self):
        filename = 'test.jpg'

        with NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (1, 1))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.post_image.image.save(filename, ntf)

        self.assertEqual(
            self.post_image.image.url,
            settings.MEDIA_URL + get_post_image_path(self.post_image, filename)
        )
        self.post_image.image.delete(save=False)

    def test_post_like_created(self):
        self.post_like = baker.make(PostLike, post=self.post)
        self.assertTrue(isinstance(self.post_like, PostLike))
        self.assertEqual(self.post_like.is_liked, True)
        self.assertEqual(self.post.likes_count, 1)

    def test_comment_like_created(self):
        self.comment_like = baker.make(CommentLike, comment=self.comment)
        self.assertTrue(isinstance(self.comment_like, CommentLike))
        self.assertEqual(self.comment_like.is_liked, True)
        self.assertEqual(self.comment.likes_count, 1)

