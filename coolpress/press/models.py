from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Category(models.Model):

    class Meta:
        verbose_name_plural = 'categories'

    label = models.CharField(max_length=200)
    slug = models.SlugField()

    def __str__(self):
        return f'{self.label} ({self.id})'


class PostStatus:
    DRAFT = 'DRAFT'
    PUBLISHED = 'PUBLISHED'

class CoolUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gravatar_link = models.URLField()
    github_profile = models.URLField()
    gh_repositories = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.user.username}'


class Post(models.Model):
    title = models.CharField(max_length=400)
    body = models.TextField()
    image_link = models.URLField()
    status = models.CharField(max_length=32,
                              choices=[(PostStatus.DRAFT, 'Draft'), (PostStatus.PUBLISHED, 'Published Post')],
                              default=PostStatus.DRAFT)
    author = models.ForeignKey(CoolUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
