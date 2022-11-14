from django.urls import path
from press import views

urlpatterns = [
    path('home/', views.home),
    path('posts/', views.posts_list, name='posts-list'),
    path('post_details/<int:post_id>', views.post_detail, name='posts-detail'),
    path('authors/', views.authors),
    path('post/<int:post_id>/comment-add/', views.add_post_comment, name='comment-add'),
    path('post/update/<int:post_id>', views.post_update, name='post-update'),
    path('post/add/', views.post_create, name='post-create'),
    path('category/add/', views.category_create, name='category-create'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('categories/', views.CategoryListView.as_view(), name='category-list')
]