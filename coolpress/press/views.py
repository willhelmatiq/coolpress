import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView
from rest_framework import viewsets, permissions, mixins, filters
from rest_framework.viewsets import GenericViewSet

from press.forms import PostForm, CommentForm, CategoryForm
from press.models import Category, Post, CoolUser, Comment, PostStatus
from press.serializers import AuthorSerializer, CategorySerializer, PostSerializer


def home(request):
    now = datetime.datetime.now()
    msg = 'Welcome to Coolpres'
    user = request.user
    cat_nums = Category.objects.annotate(num_posts=Count('post')).values('label', 'num_posts').order_by('id')
    li_cats = [f'<li>{cat_num["label"]}: {cat_num["num_posts"]}</li>' for cat_num in cat_nums]
    cats_ul = f'<ul>{"".join(li_cats)}</ul>'
    last_5_posts = Post.objects.all().order_by('-creation_date')[:5]
    li_posts = [f'<li>{post.title}</li>' for post in last_5_posts]
    posts_ul = f'<ul>{"".join(li_posts)}</ul>'
    html = f"<html><head><title>{msg}</title><body><h1>{msg}</h1><div>{user}</div><p>It is now {now}.<p><h2>Section1</h2><section>{cats_ul}</section>" \
           f"<p><h2>Section2</h2><section>{posts_ul}</body></html>"
    return HttpResponse(html)

def authors(request):
    msg = 'Authors list page'
    users = CoolUser.objects.all().values('user__first_name', 'user__last_name', 'user__username', 'github_profile', 'gh_repositories')
    li_users = [f'<li>{user["user__first_name"]} {user["user__last_name"]} {user["user__username"]}' \
                f'{user["github_profile"]} {user["gh_repositories"]}</li>' for user in users]
    users_ul = f'<ul>{"".join(li_users)}</ul>'
    html = f"<html><head><title>{msg}</title><body><h1>{msg}</h1>{users_ul}</body></html>"
    return HttpResponse(html)


def render_a_post(post):
    return f'<div style="margin: 20px;padding-bottom: 10px;"><h2>{post.title}</h2><p style="color: gray;">{post.body}</p><p>{post.author.user.username}</p></div>'


def posts_list(request):
    objects = Post.objects.all()[:20]
    return render(request, 'posts_list.html', {'posts_list': objects})


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    data = request.POST or {'votes': 10}
    form = CommentForm(data)

    comments = post.comment_set.order_by('-creation_date')
    return render(request, 'posts_detail.html', {'post_obj': post, 'comment_form': form, 'comments': comments})


@login_required
def add_post_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    data = request.POST or {'votes': 10}
    form = CommentForm(data)
    print(request)
    if request.method == 'POST':
        if form.is_valid():
            votes = form.cleaned_data.get('votes')
            body = form.cleaned_data['body']
            Comment.objects.create(votes=votes, body=body, post=post, author=request.user.cooluser)
            return HttpResponseRedirect(reverse('posts-detail', kwargs={'post_id': post_id}))

    return render(request, 'comment-add.html', {'form': form, 'post': post})


@login_required
def post_update(request, post_id=None):
    post = None
    if post_id:
        post = get_object_or_404(Post, pk=post_id)
        if request.user != post.author.user:
            return HttpResponseBadRequest('Not allowed to change others posts')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            instance = form.save(commit=False)
            username = request.user.username
            instance.author = CoolUser.objects.get(user__username=username)
            instance.save()
            return HttpResponseRedirect(reverse('posts-detail', kwargs={'post_id': instance.id}))
    else:
        form = PostForm(instance=post)

    return render(request, 'post_update.html', {'form': form})

@login_required
def post_create(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            body = form.cleaned_data['body']
            image_link = form.cleaned_data.get('image_link')
            category = form.cleaned_data.get('category')
            status = form.cleaned_data.get('status')
            post = Post.objects.create(title=title, body=body, image_link=image_link, category=category, status=status,
                                   author=request.user.cooluser)
            post.save()
            return redirect('/posts')
    return render(request, 'post_create.html', {'form': form})

@login_required
def category_create(request):
    form = CategoryForm
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            label = form.cleaned_data.get('label')
            slug = form.cleaned_data.get('slug')
            category = Category.objects.create(label=label, slug=slug,
                                   created_by=request.user.cooluser)
            category.save()
            return redirect('/posts')
    return render(request, 'category_create.html', {'form': form})
class AboutView(TemplateView):
    template_name = "about.html"


class CategoryListView(ListView):
    model = Category


class PostClassBasedListView(ListView):
    paginate_by = 20
    queryset = Post.objects.filter(status=PostStatus.PUBLISHED).order_by('-last_update')
    context_object_name = 'posts_list'
    template_name = 'posts_list.html'


class PostClassFilteringListView(PostClassBasedListView):
    paginate_by = 5

    def get_queryset(self):
        queryset = super(PostClassFilteringListView, self).get_queryset()
        category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return queryset.filter(category=category)

class PostClassFilteringByAuthorListView(PostClassBasedListView):

    def get_queryset(self):
        queryset = super(PostClassFilteringByAuthorListView, self).get_queryset()
        author = get_object_or_404(CoolUser, id=self.kwargs['post_author_id'])
        return queryset.filter(author=author)


def category_api(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    return JsonResponse(
        dict(slug=cat.slug, label=cat.label)
    )


def categories_api(request):
    cats = {}
    for cat in Category.objects.all():
        cats[cat.id] = dict(slug=cat.slug, label=cat.label, created_by=cat.created_by)
    return JsonResponse(
        cats
    )


class ModelNonDeletableViewSet(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               # mixins.DestroyModelMixin,
                               mixins.ListModelMixin,
                               GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass


class CategoryViewSet(ModelNonDeletableViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.author == request.user.cooluser


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Post.objects.all().filter(status=PostStatus.PUBLISHED) \
        .order_by('-creation_date')
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['category__id']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.cooluser)

class AuthorsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = CoolUser.objects.alias(posts=Count('post')).filter(posts__gte=1)
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['post__category__slug']