from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from press.models import CoolUser, Category, Post, PostStatus, Comment


class TrendingPostPagesTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='user')
        cu = CoolUser.objects.create(user=user)
        category = Category.objects.create(label='Tech', slug='tech')
        title= ['FTX: Tougher crypto rules needed after collapse, says Bank of England', ]
        post = Post.objects.create(status = PostStatus.PUBLISHED,  category=category, title=title, author=cu)

        cls.user = user
        cls.post = post
        cls.cu = cu

    def setUp(self):
        self.client = Client()

    def test_post_before_comment(self):
        response = self.client.get(reverse('posts-list-trending'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts_list']), 0)

    def test_post_after_comment(self):
        post = self.post
        comment_titles = ['test', 'test comment', 'one more', 'another one', 'and another one']
        for comment_title in comment_titles:
            Comment.objects.create(body=comment_title, votes=10, author=self.cu, post=post)

        response = self.client.get(reverse('posts-list-trending'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts_list']), 1)

