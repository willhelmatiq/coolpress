import datetime

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from press.models import Category, Post, CoolUser


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
    return render(request, 'posts_detail.html', {'post_obj': post})