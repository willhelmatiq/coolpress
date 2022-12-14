from typing import Optional

import requests
from django.contrib.auth.models import User
from django.db import models
from libgravatar import Gravatar


class CoolUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gravatar_link = models.URLField(null=True, blank=True, editable=False)
    gravatar_updated_at = models.DateTimeField(null=True)
    github_profile = models.CharField(max_length=150, null=True, blank=True)
    gh_repositories = models.IntegerField(null=True, blank=True, editable=False)
    gh_stars = models.IntegerField(null=True, blank=True, editable=False)
    last_github_check = models.DateTimeField(null=True)

    # def save(self, *args, **kwargs):
    #     super(CoolUser, self).save(*args, **kwargs)
    #
    #     email = self.user.email
    #     if email:
    #         old_image_link = self.gravatar_link
    #         new_image_link = get_gravatar_image(email)
    #         if (new_image_link != old_image_link):
    #             self.gravatar_updated_at = timezone.now()
    #         self.gravatar_link = new_image_link
    #
    #     if self.github_profile and (timezone.now() - self.last_github_check).total_seconds() /(60*60*24) >=1:
    #         repositories = get_github_repositories(self.github_profile)
    #         stars = get_github_stars(self.github_profile)
    #         self.last_github_check = timezone.now()
    #         self.gh_repositories = repositories
    #         self.gh_stars = stars
    #
    #     super(CoolUser, self).save()
    def save(self, *args, **kwargs):
        if self.user.email is not None:
            self.gravatar_link = Gravatar(self.user.email).get_image()
        self.gh_repositories = self.get_github_repos()
        super(CoolUser, self).save(*args, **kwargs)

    def get_github_url(self) -> Optional[str]:
        if self.github_profile:
            url = f'https://github.com/{self.github_profile}'
            response = requests.get(url)
            if response.status_code == 200:
                return url

    def get_github_repos(self) -> Optional[int]:
        url = self.get_github_url()
        if url:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            css_selector = '.Counter'
            repositories_info = soup.select_one(css_selector)
            repos_text = repositories_info.text
            return int(repos_text)


    def __str__(self):
        return f'{self.user.username}'


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'categories'

    label = models.CharField(max_length=200)
    slug = models.SlugField()
    created_by = models.ForeignKey(CoolUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.label} ({self.id})'


class PostStatus:
    DRAFT = 'DRAFT'
    PUBLISHED = 'PUBLISHED'


class Post(models.Model):
    title = models.CharField(max_length=400)
    body = models.TextField(null=True)
    image_link = models.URLField(null=True)
    status = models.CharField(max_length=32,
                              choices=[(PostStatus.DRAFT, 'Draft'),
                                       (PostStatus.PUBLISHED, 'Published Post')],
                              default=PostStatus.DRAFT)

    author = models.ForeignKey(CoolUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.category.label}: {self.title}'

class CommentStatus:
    PUBLISHED = 'PUBLISHED'
    NON_PUBLISHED = 'NON_PUBLISHED'


class Comment(models.Model):
    body = models.TextField()
    status = models.CharField(max_length=32,
                              choices=[(CommentStatus.PUBLISHED, 'Published'),
                                       (CommentStatus.NON_PUBLISHED, 'Non Published')],
                              default=CommentStatus.PUBLISHED)
    votes = models.IntegerField()

    author = models.ForeignKey(CoolUser, on_delete=models.DO_NOTHING)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.body[:10]} - from: {self.author.user.username}'