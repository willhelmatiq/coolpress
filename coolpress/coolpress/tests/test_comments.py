from django.test import TestCase, Client

from django.contrib.auth.models import User
from django.urls import reverse

from press.models import CoolUser, Post, Category, Comment, CommentStatus


class CommentTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='Mr X')
        cu = CoolUser.objects.create(user=user)
        post = Post.objects.create(category=Category.objects.create(label='Tech', slug='tech'),
                                   title='a new mac is out there',
                                   author=cu)
        comment = Comment.objects.create(body='my test body', votes=0, author=cu, post=post)

        cls.user = user
        cls.post = post
        cls.cu = cu
        cls.comment = comment

    def setUp(self):
        self.client = Client()

    def test_published_status_test(self):
        actual = self.comment.status
        expected = CommentStatus.PUBLISHED
        self.assertEqual(actual, expected)

    def test_post_detail_comment_is_present(self):
        response = self.client.get(reverse('posts-detail', kwargs={'post_id': self.post.id}))
        comment = response.context['comments'].values()[0]
        self.assertEqual(comment['body'], self.comment.body)

    def test_post_detail_after_comment_status_change(self):
        comment = self.comment
        comment.body = "new text"
        comment.status = CommentStatus.NON_PUBLISHED
        comment.save()
        response = self.client.get(reverse('posts-detail', kwargs={'post_id': self.post.id}))
        num_of_comments = len(response.context['comments'])
        self.assertEqual(0, num_of_comments)
